"""
Operações de feedback do utilizador (a implementar endpoint próprio no futuro).
"""
from app.db.supabase_client import supabase

def guardar_feedback(session_id: str, rating: int, comentario: str = None) -> None:
    supabase.table("feedback").insert({
        "session_id": session_id,
        "rating": rating,
        "comentario": comentario
    }).execute()