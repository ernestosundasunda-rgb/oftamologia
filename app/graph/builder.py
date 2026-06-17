from langgraph.graph import StateGraph, END
from app.graph.state import AgenteState
from app.graph.nodes import (
    gestor_de_memoria,
    analisador_de_contexto,
    classificador,
    saudacao,
    fora_do_escopo,
    rag,
    validador,
    guardar_historico
)

def decidir_rota(state: AgenteState) -> str:
    return state.get("classificacao", {}).get("rota", "rag")

def criar_grafo():
    workflow = StateGraph(AgenteState)

    workflow.add_node("memoria", gestor_de_memoria)
    workflow.add_node("contexto", analisador_de_contexto)
    workflow.add_node("classificador", classificador)
    workflow.add_node("saudacao", saudacao)
    workflow.add_node("fora_do_escopo", fora_do_escopo)
    workflow.add_node("rag", rag)
    workflow.add_node("validador", validador)
    workflow.add_node("guardar_historico", guardar_historico)

    workflow.set_entry_point("memoria")
    workflow.add_edge("memoria", "contexto")
    workflow.add_edge("contexto", "classificador")

    workflow.add_conditional_edges(
        "classificador",
        decidir_rota,
        {
            "saudacao": "saudacao",
            "fora_do_escopo": "fora_do_escopo",
            "rag": "rag"
        }
    )

    for no in ["saudacao", "fora_do_escopo", "rag"]:
        workflow.add_edge(no, "validador")

    workflow.add_edge("validador", "guardar_historico")
    workflow.add_edge("guardar_historico", END)

    return workflow.compile()

grafo = criar_grafo()