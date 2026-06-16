"""
Nó 6 - RAG Médico
Estratégia híbrida: resposta direta do documento para similaridade alta,
fallback para LLM apenas quando necessário.
"""
import traceback
from loguru import logger
from langchain_core.prompts import ChatPromptTemplate
from app.graph.state import AgenteState
from app.core.llm import criar_llm
from app.db.vector_store import buscar_documentos

DISCLAIMER = "\n\n⚠️ Esta informação é apenas educativa. Consulte sempre um oftalmologista."

async def rag_medico(state: AgenteState) -> AgenteState:
    pergunta = state["mensagem_reformulada"]
    try:
        docs = buscar_documentos(pergunta, tipo="medico", k=5, threshold=0.2)
        if not docs:
            state["resposta_final"] = "Não encontrei informação suficiente na nossa base de conhecimento. Recomendo uma consulta com um oftalmologista."
            return state

        # Ordenar por similaridade decrescente
        docs.sort(key=lambda d: d.metadata.get("similarity", 0), reverse=True)
        top_doc = docs[0]
        top_similarity = top_doc.metadata.get("similarity", 0)

        # Resposta determinística para similaridade alta (>=0.8)
        if top_similarity >= 0.8:
            resposta = top_doc.page_content
            # Se houver um segundo documento com similaridade alta e próxima (diferença <= 0.1), juntar ambos
            if len(docs) > 1:
                second_sim = docs[1].metadata.get("similarity", 0)
                if second_sim >= 0.7 and (top_similarity - second_sim) <= 0.1:
                    resposta += "\n\n" + docs[1].page_content
            state["resposta_final"] = resposta + DISCLAIMER
            logger.info(f"RAG Médico determinístico: doc(s) usados com sim {top_similarity:.4f}")
            return state

        # Fallback para LLM apenas se similaridade for inferior a 0.8
        llm = criar_llm()
        prompt = ChatPromptTemplate.from_messages([
            ("system", "Utiliza exclusivamente os documentos fornecidos. Se não houver resposta exata, diz que não sabes. Inclui o disclaimer no final."),
            ("user", "Documentos:\n{documentos}\n\nPergunta: {pergunta}")
        ])
        contexto = "\n\n---\n\n".join(doc.page_content for doc in docs)
        resposta = await llm.ainvoke(prompt.format_messages(documentos=contexto, pergunta=pergunta))
        state["resposta_final"] = resposta.content.strip() + DISCLAIMER
        logger.info("RAG Médico com LLM (similaridade baixa)")

    except Exception as e:
        logger.error(f"Erro no RAG médico: {traceback.format_exc()}")
        state["resposta_final"] = "Ocorreu um erro ao processar a sua pergunta. Por favor, tente novamente."
    return state