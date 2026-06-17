"""
Nó RAG único – busca em toda a base e geração restrita.
k=7, instrução para priorizar o documento de título mais relevante.
"""
import traceback
from loguru import logger
from langchain_core.prompts import ChatPromptTemplate
from app.graph.state import AgenteState
from app.core.llm import criar_llm
from app.db.vector_store import buscar_documentos

llm = criar_llm(temperature=0.0)

prompt = ChatPromptTemplate.from_messages([
    ("system", """Tu és um assistente do Centro Oftalmológico. Usa APENAS os DOCUMENTOS abaixo.
Regras INQUEBRÁVEIS:
1. Só podes usar factos que aparecem EXPLICITAMENTE nos DOCUMENTOS.
2. Proibido acrescentar NENHUM conhecimento externo.
3. Se a informação não estiver nos DOCUMENTOS, diz: "Não encontrei essa informação na nossa base de conhecimento. Posso ajudar com outra questão?"
4. Não faças diagnósticos, não prescrevas medicamentos.
5. Sê conciso e direto.
6. Inclui o aviso "⚠️ Esta informação é apenas educativa. Consulte sempre um oftalmologista." apenas se o conteúdo for de saúde ocular.
7. Se houver um documento cujo título corresponda exatamente ao tema da pergunta, usa ESSE documento como fonte principal, mesmo que outro tenha similaridade mais alta."""),
    ("user", "DOCUMENTOS:\n{documentos}\n\nPergunta: {pergunta}")
])

async def rag(state: AgenteState) -> AgenteState:
    pergunta = state["mensagem_reformulada"]
    try:
        docs = buscar_documentos(pergunta, tipo=None, k=7, threshold=0.2)
        if not docs:
            state["resposta_final"] = "Não encontrei essa informação na nossa base de conhecimento. Posso ajudar com outra questão?"
            return state

        contexto = "\n\n---\n\n".join(doc.page_content for doc in docs)
        resposta = await llm.ainvoke(prompt.format_messages(documentos=contexto, pergunta=pergunta))
        state["resposta_final"] = resposta.content.strip()
        logger.info(f"RAG: {len(docs)} docs fornecidos à LLM")
    except Exception as e:
        logger.error(f"Erro no RAG: {traceback.format_exc()}")
        state["resposta_final"] = "Ocorreu um erro ao processar a sua pergunta. Por favor, tente novamente."
    return state