"""
Nó 2 - Analisador de Contexto
Reformula a pergunta do utilizador com base no histórico recente.
"""
from langchain_core.prompts import ChatPromptTemplate
from app.graph.state import AgenteState
from app.core.llm import criar_llm

llm = criar_llm()

prompt = ChatPromptTemplate.from_messages([
    ("system", """Tu és um analisador de contexto. Recebes uma conversa anterior (histórico) e a nova mensagem do utilizador.
A tua tarefa é reformular a mensagem do utilizador para que fique totalmente autónoma, resolvendo todas as referências a mensagens anteriores (pronomes, elipses, assuntos implícitos).
Se a mensagem já for completa, devolve-a igual.
Devolve APENAS a mensagem reformulada, sem explicações, sem prefixos."""),
    ("user", "Histórico da conversa:\n{historico}\n\nNova mensagem: {mensagem}")
])

async def analisador_de_contexto(state: AgenteState) -> AgenteState:
    historico = state["historico"]
    mensagem_original = state["mensagem_original"]

    # Se não há histórico, mantém a mensagem original
    if not historico:
        state["mensagem_reformulada"] = mensagem_original
        return state

    # Formatar histórico como texto legível
    historico_texto = "\n".join(
        f"{msg['role']}: {msg['message']}" for msg in historico
    )

    # Obter reformulação via LLM
    resposta = await llm.ainvoke(
        prompt.format_messages(historico=historico_texto, mensagem=mensagem_original)
    )
    reformulada = resposta.content.strip()

    # Se a LLM devolver algo vazio, usa a original
    state["mensagem_reformulada"] = reformulada if reformulada else mensagem_original
    return state