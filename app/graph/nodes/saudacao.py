"""
Nó 4 - Saudação
Responde de forma cordial e profissional.
"""
from app.graph.state import AgenteState

RESPOSTAS_SAUDACAO = {
    "entrada": "Olá! Bem-vindo(a) ao Centro Oftalmológico. Em que posso ajudar?",
    "despedida": "Foi um prazer ajudar. Desejo-lhe uma excelente visão! Até breve.",
    "agradecimento": "De nada! Estou aqui para ajudar. Tem mais alguma dúvida?",
}

async def saudacao(state: AgenteState) -> AgenteState:
    mensagem = state["mensagem_reformulada"].lower()

    if any(palavra in mensagem for palavra in ["adeus", "até logo", "xau", "tchau"]):
        resposta = RESPOSTAS_SAUDACAO["despedida"]
    elif any(palavra in mensagem for palavra in ["obrigado", "obrigada", "brigado", "valeu"]):
        resposta = RESPOSTAS_SAUDACAO["agradecimento"]
    else:
        resposta = RESPOSTAS_SAUDACAO["entrada"]

    state["resposta_final"] = resposta
    return state