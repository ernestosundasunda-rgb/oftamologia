"""
Nó 9 - Contingência
Resposta para situações de baixa confiança ou ambiguidade.
"""
from app.graph.state import AgenteState

MENSAGEM_CONTINGENCIA = (
    "Não tenho a certeza se compreendi bem a sua pergunta. "
    "Pode reformular ou fornecer mais detalhes? "
    "Estou aqui para ajudar com informações sobre o centro ou sobre saúde ocular."
)

async def contingencia(state: AgenteState) -> AgenteState:
    state["resposta_final"] = MENSAGEM_CONTINGENCIA
    return state