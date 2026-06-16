"""
Nó 11 - Guardar Histórico e Logs
Persiste a interação nas tabelas chat_history e logs.
"""
from app.graph.state import AgenteState
from app.db.historico import guardar_mensagem
from app.db.logs import registar_log

async def guardar_historico(state: AgenteState) -> AgenteState:
    session_id = state["session_id"]
    pergunta = state["mensagem_original"]
    resposta = state.get("resposta_final", "")
    rota = state.get("classificacao", {}).get("rota", "desconhecida")

    # Guardar mensagem do utilizador
    guardar_mensagem(session_id, "user", pergunta)

    # Guardar resposta do assistente
    if resposta:
        guardar_mensagem(session_id, "assistant", resposta)

    # Registar log
    registar_log(session_id, rota, pergunta, resposta)

    return state