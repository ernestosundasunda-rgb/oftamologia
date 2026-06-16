"""
Operações de leitura e escrita na tabela chat_history.
"""
from typing import List, Dict
from app.db.supabase_client import supabase
from app.core.config import get_settings

settings = get_settings()


def carregar_historico(session_id: str) -> List[Dict[str, str]]:
    """
    Recupera as últimas N mensagens da conversa, ordenadas por data.
    Retorna lista de dicionários: { "role": "user"|"assistant", "message": "..." }
    """
    result = (
        supabase.table("chat_history")
        .select("role, message")
        .eq("session_id", session_id)
        .order("created_at", desc=True)
        .limit(settings.MAX_HISTORICO * 2)  # pares user+assistant
        .execute()
    )
    # Inverter para ordem cronológica
    registos = list(reversed(result.data)) if result.data else []
    return registos


def guardar_mensagem(session_id: str, role: str, message: str) -> None:
    """
    Insere uma nova mensagem na tabela chat_history.
    """
    supabase.table("chat_history").insert({
        "session_id": session_id,
        "role": role,
        "message": message
    }).execute()