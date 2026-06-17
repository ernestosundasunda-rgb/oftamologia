"""
Busca vetorial personalizada com bónus de similaridade por correspondência no título.
"""
from typing import List, Optional
from langchain_core.documents import Document
from loguru import logger
from app.db.supabase_client import supabase
from app.core.embeddings import criar_embeddings

embeddings = criar_embeddings()

def _titulo_bonus(titulo: str, query: str) -> float:
    """Retorna um pequeno bónus (0.05) se alguma palavra da query aparecer no título."""
    if not titulo:
        return 0.0
    palavras_query = set(query.lower().split())
    palavras_titulo = set(titulo.lower().split())
    if palavras_query & palavras_titulo:
        return 0.05
    return 0.0

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
            logger.info(f"Nenhum documento encontrado para a query: '{query}'")
            return []

        docs = []
        for item in resultado.data:
            similarity = item.get("similarity", 0)
            # Bónus por correspondência no título
            titulo = item["metadata"].get("titulo", "")
            bonus = _titulo_bonus(titulo, query)
            similarity += bonus

            doc_id = item["metadata"].get("doc_id", "?")
            logger.info(f"Doc: {doc_id} | Sim: {similarity:.4f} (bónus: {bonus}) | Título: {titulo}")

            if similarity >= threshold:
                doc = Document(
                    page_content=item["content"],
                    metadata=item["metadata"]
                )
                doc.metadata["similarity"] = similarity
                docs.append(doc)

        # Reordenar pela similaridade ajustada
        docs.sort(key=lambda d: d.metadata.get("similarity", 0), reverse=True)
        return docs

    except Exception as e:
        logger.error(f"Erro na busca vetorial: {e}")
        return []