"""
Nó 3 - Classificador de intenções (versão de alta precisão)
Prompt reforçado com regras explícitas e temperatura zero para determinismo.
"""
import traceback
from loguru import logger
from langchain_core.prompts import ChatPromptTemplate
from app.graph.state import AgenteState, DecisaoRota
from app.core.llm import criar_llm

# LLM específica para classificação com temperatura zero
llm = criar_llm(temperature=0.0).with_structured_output(DecisaoRota, method="json_mode")

prompt = ChatPromptTemplate.from_messages([
    ("system", """Tu és um classificador de intenções para um centro oftalmológico. 
A tua tarefa é decidir a rota correta. Responde APENAS com um JSON com os campos "rota" e "justificacao".

ROTAS DISPONÍVEIS:

1. "saudacao" – Cumprimentos, despedidas, agradecimentos.
   Ex: "Olá", "Bom dia", "Obrigado", "Adeus", "Tudo bem?"

2. "rag_institucional" – Perguntas sobre o centro: horários, localização, contactos, serviços, médicos, equipa, documentos para consulta, seguros, preços.
   Ex: "Quais os horários?", "Que documentos levar?", "Como marcar consulta?", "Têm oftalmopediatria?", "Aceitam Multicare?"

3. "rag_medico" – Perguntas educativas sobre saúde ocular: definições, doenças, sintomas, exames, tratamentos (sem diagnóstico pessoal).
   Ex: "O que é glaucoma?", "Sintomas de catarata?", "O que é astigmatismo?", "Como tratar miopia?", "O que é OCT?", "Prevenir fadiga ocular?"

4. "emergencia" – Sintomas agudos que exigem atendimento imediato: perda súbita de visão, dor intensa, trauma, flashes de luz, hemorragia ocular.
   Ex: "Perdi a visão de repente", "Bati no olho", "Estou a ver tudo turvo", "Olho vermelho e dor forte"

5. "fora_do_escopo" – Assuntos sem relação com oftalmologia ou o centro.
   Ex: "Quem ganhou o Euro?", "Fala-me de carros", "Receita de bolo"

6. "contingencia" – Pergunta confusa, ambígua, ou que não encaixa claramente em nenhuma rota.

REGRA CRÍTICA:
- Qualquer pergunta que peça definição, descrição ou explicação de uma doença, condição, exame ou termo oftalmológico (ex: "O que é X?", "Defina Y", "Explica Z") → "rag_medico".
- Não uses a presença da palavra "consulta" para decidir; analisa o tópico central da pergunta."""),
    ("user", "Pergunta: {pergunta}")
])

async def classificador(state: AgenteState) -> AgenteState:
    pergunta = state["mensagem_reformulada"]
    try:
        resposta = await llm.ainvoke(prompt.format_messages(pergunta=pergunta))
        state["classificacao"] = {"rota": resposta.rota, "justificacao": resposta.justificacao}
        logger.info(f"Classificação: {resposta.rota} | {resposta.justificacao}")
    except Exception as e:
        logger.error(f"Erro no classificador: {traceback.format_exc()}")
        state["classificacao"] = {"rota": "contingencia", "justificacao": "Erro na classificação"}
    return state