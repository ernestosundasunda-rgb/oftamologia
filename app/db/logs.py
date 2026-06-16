"""
Registo de logs da execução do agente.
"""
from app.db.supabase_client import supabase

def registar_log(session_id: str, rota: str, pergunta: str, resposta: str) -> None:
    supabase.table("logs").insert({
        "session_id": session_id,
        "rota": rota,
        "pergunta": pergunta,
        "resposta": resposta
    }).execute()