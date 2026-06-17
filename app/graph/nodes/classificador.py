"""
Classificador determinístico. A LLM não é usada.
"""
from app.graph.state import AgenteState

# Conjuntos de palavras
SAUDACAO_PURAS = {"olá", "oi", "bom dia", "boa tarde", "boa noite", "adeus", "tchau", "obrigado", "obrigada", "até logo"}
FORA_ESCOPO = {"futebol", "política", "carros", "receita", "bolo", "clima", "jogo", "campeonato", "programação", "finanças", "ciclismo"}
INFORMATIVAS = {
    "horário", "consulta", "médico", "documento", "contacto", "telefone", "morada",
    "especialidade", "serviço", "glaucoma", "catarata", "miopia", "astigmatismo",
    "sintoma", "exame", "cirurgia", "olho", "visão", "óculos", "lente", "tempo",
    "marcação", "seguro", "preço", "equipa", "corpo clínico", "doutor", "funcionamento"
}

def classificar(pergunta: str) -> dict:
    pergunta_lower = pergunta.lower().strip()
    palavras = set(pergunta_lower.split())

    # Se houver qualquer palavra informativa, é RAG (mesmo que tenha palavras de saudação)
    if palavras & INFORMATIVAS:
        return {"rota": "rag", "justificacao": "Contém palavras informativas"}

    # Se não tem informativas, mas é só saudação
    if palavras.issubset(SAUDACAO_PURAS) or any(p in SAUDACAO_PURAS for p in palavras):
        return {"rota": "saudacao", "justificacao": "Saudação pura"}

    # Se tem palavras de fora do escopo
    if palavras & FORA_ESCOPO:
        return {"rota": "fora_do_escopo", "justificacao": "Fora do escopo"}

    # Qualquer outra coisa vai para RAG
    return {"rota": "rag", "justificacao": "Assunto geral"}

async def classificador(state: AgenteState) -> AgenteState:
    pergunta = state["mensagem_reformulada"]
    state["classificacao"] = classificar(pergunta)
    return state