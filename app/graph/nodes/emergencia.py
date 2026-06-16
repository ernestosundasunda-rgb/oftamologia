"""
Nó 7 - Emergência
Responde a situações urgentes com instruções de ação imediata.
"""
from app.graph.state import AgenteState

MENSAGEM_EMERGENCIA = (
    "🚨 **ATENÇÃO: Possível Emergência Oftalmológica**\n\n"
    "Os sintomas que descreveu podem indicar uma situação que requer atendimento médico urgente. "
    "Recomendamos que:\n\n"
    "1. Se houver perda súbita de visão, dor intensa, trauma ou hemorragia ocular, dirija-se IMEDIATAMENTE ao serviço de urgência mais próximo.\n"
    "2. Não esfregue os olhos nem aplique qualquer produto sem orientação médica.\n"
    "3. Se possível, contacte o nosso centro (+351 210 123 456) para orientação adicional.\n\n"
    "A sua visão é preciosa. Não hesite em procurar ajuda profissional."
)

async def emergencia(state: AgenteState) -> AgenteState:
    state["resposta_final"] = MENSAGEM_EMERGENCIA
    return state