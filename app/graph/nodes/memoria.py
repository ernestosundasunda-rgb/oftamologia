"""
Nó 1 - Gestor de Memória
Responsável por carregar o histórico da conversa e inseri-lo no estado.
"""
from app.graph.state import AgenteState
from app.db.historico import carregar_historico


async def gestor_de_memoria(state: AgenteState) -> AgenteState:
    """
    Carrega o histórico associado ao session_id e atualiza o estado.
    Este nó é assíncrono para manter compatibilidade com o grafo.
    """
    session_id = state["session_id"]

    # Carregar histórico do Supabase
    historico = carregar_historico(session_id)

    # Atualizar estado
    state["historico"] = historico
    # state["mensagem_reformulada"] ainda estará vazia,
    # será preenchida pelo analisador de contexto.
    return state