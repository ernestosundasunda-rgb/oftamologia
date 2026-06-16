"""
Nó 8 - Fora do escopo
Responde educadamente que o assistente é especializado.
"""
from app.graph.state import AgenteState

MENSAGEM_FORA_ESCOPO = (
    "Peço desculpa, mas sou um assistente especializado em assuntos relacionados "
    "com o Centro Oftalmológico e com a saúde ocular. "
    "Posso ajudar com informações sobre os nossos serviços, horários, especialidades, "
    "ou com questões educativas sobre a visão. "
    "Em que mais posso ser útil?"
)

async def fora_do_escopo(state: AgenteState) -> AgenteState:
    state["resposta_final"] = MENSAGEM_FORA_ESCOPO
    return state