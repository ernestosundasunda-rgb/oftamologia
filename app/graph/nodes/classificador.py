"""
Nó 3 – Classificador de intenções (3 rotas) com blindagem anti‑falsas saudações
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

Regra ABSOLUTA: se a frase menciona qualquer aspecto do centro ou saúde ocular → "rag". Mesmo que pareça uma afirmação ou uma despedida. Ex: "O centro funciona das 8h às 19h" → "rag".

Responde APENAS com JSON: {{"rota":"...", "justificacao":"..."}}"""),
    ("user", "Frase: {pergunta}")
])

# Palavras que, se presentes, impedem a classificação como saudação
PALAVRAS_INFORMATIVAS = [
    "consulta", "tempo", "médico", "horário", "funcionamento", "marcação",
    "documento", "contacto", "telefone", "morada", "especialidade", "serviço",
    "glaucoma", "catarata", "miopia", "astigmatismo", "hipermetropia",
    "sintoma", "exame", "cirurgia", "olho", "visão", "óculos", "lente"
]

async def classificador(state: AgenteState) -> AgenteState:
    pergunta = state["mensagem_reformulada"].lower()
    try:
        resposta = await llm.ainvoke(prompt.format_messages(pergunta=pergunta))
        rota = resposta.rota
        justificacao = resposta.justificacao

        # Blindagem: se a LLM escolheu "saudacao" mas a pergunta contém palavras informativas, força "rag"
        if rota == "saudacao" and any(p in pergunta for p in PALAVRAS_INFORMATIVAS):
            rota = "rag"
            justificacao = "A frase contém palavras-chave informativas, forçando 'rag'."

        state["classificacao"] = {"rota": rota, "justificacao": justificacao}
        logger.info(f"Classificação: {rota} | {justificacao}")
    except Exception as e:
        logger.error(f"Erro no classificador: {traceback.format_exc()}")
        state["classificacao"] = {"rota": "rag", "justificacao": "Erro na classificação"}
    return state