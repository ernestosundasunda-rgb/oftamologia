"""
Cliente Supabase reutilizável.
Inicializa a conexão uma única vez e exporta o objeto.
"""
from supabase import create_client, Client
from app.core.config import get_settings

settings = get_settings()

supabase: Client = create_client(
    settings.SUPABASE_URL,
    settings.SUPABASE_KEY
)