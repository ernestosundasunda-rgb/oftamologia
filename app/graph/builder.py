from langgraph.graph import StateGraph, END
from app.graph.state import AgenteState
from app.graph.nodes import (
    gestor_de_memoria,
    analisador_de_contexto,
    classificador,
    saudacao,
    rag_institucional,
    rag_medico,
    emergencia,
    fora_do_escopo,
    contingencia,
    validador,
    guardar_historico
)

def decidir_rota(state: AgenteState) -> str:
    return state.get("classificacao", {}).get("rota", "contingencia")

def criar_grafo():
    workflow = StateGraph(AgenteState)

    # Adicionar todos os nós
    workflow.add_node("memoria", gestor_de_memoria)
    workflow.add_node("contexto", analisador_de_contexto)
    workflow.add_node("classificador", classificador)
    workflow.add_node("saudacao", saudacao)
    workflow.add_node("rag_institucional", rag_institucional)
    workflow.add_node("rag_medico", rag_medico)
    workflow.add_node("emergencia", emergencia)
    workflow.add_node("fora_do_escopo", fora_do_escopo)
    workflow.add_node("contingencia", contingencia)
    workflow.add_node("validador", validador)
    workflow.add_node("guardar_historico", guardar_historico)

    # Ligar os nós
    workflow.set_entry_point("memoria")
    workflow.add_edge("memoria", "contexto")
    workflow.add_edge("contexto", "classificador")

    workflow.add_conditional_edges(
        "classificador",
        decidir_rota,
        {
            "saudacao": "saudacao",
            "rag_institucional": "rag_institucional",
            "rag_medico": "rag_medico",
            "emergencia": "emergencia",
            "fora_do_escopo": "fora_do_escopo",
            "contingencia": "contingencia",
        }
    )

    # Todos os especializados vão para o validador
    for no in ["saudacao", "rag_institucional", "rag_medico", "emergencia", "fora_do_escopo", "contingencia"]:
        workflow.add_edge(no, "validador")

    workflow.add_edge("validador", "guardar_historico")
    workflow.add_edge("guardar_historico", END)

    return workflow.compile()

grafo = criar_grafo()