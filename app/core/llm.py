"""
Factory para criar a LLM (ChatGroq).
"""
from langchain_groq import ChatGroq
from app.core.config import get_settings

def criar_llm(temperature: float = None) -> ChatGroq:
    settings = get_settings()
    return ChatGroq(
        model=settings.LLM_MODEL,
        temperature=temperature if temperature is not None else settings.LLM_TEMPERATURE,
        api_key=settings.GROQ_API_KEY,
    )