"""
Nó 5 - RAG Institucional
Estratégia híbrida: resposta direta do documento para similaridade alta.
"""
import traceback
from loguru import logger
from langchain_core.prompts import ChatPromptTemplate
from app.graph.state import AgenteState
from app.core.llm import criar_llm
from app.db.vector_store import buscar_documentos

async def rag_institucional(state: AgenteState) -> AgenteState:
    pergunta = state["mensagem_reformulada"]
    try:
        docs = buscar_documentos(pergunta, tipo="institucional", k=5, threshold=0.2)
        if not docs:
            state["resposta_final"] = "Não encontrei essa informação na nossa base de conhecimento. Posso ajudar com outra questão?"
            return state

        docs.sort(key=lambda d: d.metadata.get("similarity", 0), reverse=True)
        top_doc = docs[0]
        top_similarity = top_doc.metadata.get("similarity", 0)

        if top_similarity >= 0.8:
            resposta = top_doc.page_content
            if len(docs) > 1:
                second_sim = docs[1].metadata.get("similarity", 0)
                if second_sim >= 0.7 and (top_similarity - second_sim) <= 0.1:
                    resposta += "\n\n" + docs[1].page_content
            state["resposta_final"] = resposta
            logger.info(f"RAG Institucional determinístico: doc(s) usados com sim {top_similarity:.4f}")
            return state

        # Fallback com LLM
        llm = criar_llm()
        prompt = ChatPromptTemplate.from_messages([
            ("system", "Utiliza exclusivamente os documentos. Se não souberes, diz que não sabes."),
            ("user", "Documentos:\n{documentos}\n\nPergunta: {pergunta}")
        ])
        contexto = "\n\n---\n\n".join(doc.page_content for doc in docs)
        resposta = await llm.ainvoke(prompt.format_messages(documentos=contexto, pergunta=pergunta))
        state["resposta_final"] = resposta.content.strip()
        logger.info("RAG Institucional com LLM (similaridade baixa)")

    except Exception as e:
        logger.error(f"Erro no RAG institucional: {traceback.format_exc()}")
        state["resposta_final"] = "Ocorreu um erro ao processar a sua pergunta. Por favor, tente novamente."
    return state