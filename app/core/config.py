from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    SUPABASE_URL: str
    SUPABASE_KEY: str
    GROQ_API_KEY: str
    LLM_MODEL: str = "llama-3.1-8b-instant"
    LLM_TEMPERATURE: float = 0.3
    HUGGINGFACEHUB_API_TOKEN: str
    EMBEDDING_MODEL: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    MAX_HISTORICO: int = 5

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

@lru_cache()
def get_settings() -> Settings:
    return Settings()