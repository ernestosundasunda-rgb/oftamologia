"""
Busca vetorial personalizada. Se tipo for None, não filtra por tipo.
"""
from typing import List, Optional
from langchain_core.documents import Document
from loguru import logger
from app.db.supabase_client import supabase
from app.core.embeddings import criar_embeddings

embeddings = criar_embeddings()

def buscar_documentos(
    query: str,
    tipo: Optional[str] = None,
    k: int = 5,
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
            doc_id = item["metadata"].get("doc_id", "?")
            logger.info(f"Doc: {doc_id} | Sim: {similarity:.4f} | Título: {item['metadata'].get('titulo', '')}")

            if similarity >= threshold:
                doc = Document(
                    page_content=item["content"],
                    metadata=item["metadata"]
                )
                doc.metadata["similarity"] = similarity
                docs.append(doc)
        return docs

    except Exception as e:
        logger.error(f"Erro na busca vetorial: {e}")
        return []