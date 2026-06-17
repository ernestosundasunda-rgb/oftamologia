"""
Busca vetorial híbrida: similaridade + prioridade absoluta por correspondência exata no título.
"""
from typing import List, Optional
from langchain_core.documents import Document
from loguru import logger
from app.db.supabase_client import supabase
from app.core.embeddings import criar_embeddings

embeddings = criar_embeddings()

def _match_titulo_exato(titulo: str, query: str) -> bool:
    """Retorna True se ≥80% das palavras da query estão no título."""
    if not titulo:
        return False
    palavras_query = set(query.lower().split())
    palavras_titulo = set(titulo.lower().split())
    if not palavras_query:
        return False
    intersecao = palavras_query & palavras_titulo
    return len(intersecao) >= len(palavras_query) * 0.8

def buscar_documentos(
    query: str,
    tipo: Optional[str] = None,
    k: int = 7,
    threshold: float = 0.2
) -> List[Document]:
    try:
        vector = embeddings.embed_query(query)
        filtro = {}
        if tipo:
            filtro = {"tipo": tipo}

        resultado = supabase.rpc(
            "match_documents",
            {
                "query_embedding": vector,
                "match_count": k,
                "filter": filtro
            }
        ).execute()

        if not resultado.data:
            logger.info(f"Nenhum documento encontrado para: '{query}'")
            return []

        docs = []
        for item in resultado.data:
            similarity = item.get("similarity", 0)
            titulo = item["metadata"].get("titulo", "")
            doc_id = item["metadata"].get("doc_id", "?")

            # Prioridade absoluta se o título corresponder exatamente à query
            if _match_titulo_exato(titulo, query):
                similarity = 2.0
                logger.info(f"Doc: {doc_id} | ⚡ Prioridade absoluta por título: {titulo}")
            else:
                logger.info(f"Doc: {doc_id} | Sim: {similarity:.4f} | Título: {titulo}")

            if similarity >= threshold:
                doc = Document(
                    page_content=item["content"],
                    metadata=item["metadata"]
                )
                doc.metadata["similarity"] = similarity
                docs.append(doc)

        docs.sort(key=lambda d: d.metadata.get("similarity", 0), reverse=True)
        return docs

    except Exception as e:
        logger.error(f"Erro na busca vetorial: {e}")
        return []