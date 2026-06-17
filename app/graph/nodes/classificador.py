"""
Nó 3 – Classificador de intenções (3 rotas, prompt cirúrgico)
"""
import traceback
from loguru import logger
from langchain_core.prompts import ChatPromptTemplate
from app.graph.state import AgenteState, DecisaoRota
from app.core.llm import criar_llm

llm = criar_llm(temperature=0.0).with_structured_output(DecisaoRota, method="json_mode")

prompt = ChatPromptTemplate.from_messages([
    ("system", """És um classificador para um centro oftalmológico. Escolhe APENAS uma destas rotas:

- "saudacao" → SÓ cumprimentos ou despedidas SEM nenhuma outra informação. Ex: "Olá", "Bom dia", "Obrigado", "Adeus".
- "fora_do_escopo" → assuntos sem relação com oftalmologia ou o centro.
- "rag" → TUDO o resto: perguntas, afirmações, pedidos, informações sobre o centro, saúde ocular, sintomas, exames, médicos, horários, contactos, etc.

Regra ABSOLUTA: se a frase menciona qualquer aspecto do centro ou saúde ocular → "rag". Mesmo que pareça uma afirmação. Ex: "O centro funciona das 8h às 19h" → "rag".

Responde APENAS com JSON: {{"rota":"...", "justificacao":"..."}}"""),
    ("user", "Frase: {pergunta}")
])

async def classificador(state: AgenteState) -> AgenteState:
    pergunta = state["mensagem_reformulada"]
    try:
        resposta = await llm.ainvoke(prompt.format_messages(pergunta=pergunta))
        state["classificacao"] = {"rota": resposta.rota, "justificacao": resposta.justificacao}
        logger.info(f"Classificação: {resposta.rota} | {resposta.justificacao}")
    except Exception as e:
        logger.error(f"Erro no classificador: {traceback.format_exc()}")
        state["classificacao"] = {"rota": "rag", "justificacao": "Erro na classificação"}
    return state