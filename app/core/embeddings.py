"""
Factory para criar o modelo de embeddings (Hugging Face via API).
"""
from langchain_huggingface import HuggingFaceEndpointEmbeddings
from app.core.config import get_settings


def criar_embeddings() -> HuggingFaceEndpointEmbeddings:
    """Retorna o modelo de embeddings que utiliza a API de inferência da Hugging Face."""
    settings = get_settings()
    return HuggingFaceEndpointEmbeddings(
        model=settings.EMBEDDING_MODEL,
        huggingfacehub_api_token=settings.HUGGINGFACEHUB_API_TOKEN,
    )