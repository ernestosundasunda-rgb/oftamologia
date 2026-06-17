from langgraph.graph import StateGraph, END
from app.graph.state import AgenteState
from app.graph.nodes import (
    gestor_de_memoria,
    analisador_de_contexto,
    responder,
    validador,
    guardar_historico
)

def criar_grafo():
    workflow = StateGraph(AgenteState)

    workflow.add_node("memoria", gestor_de_memoria)
    workflow.add_node("contexto", analisador_de_contexto)
    workflow.add_node("responder", responder)
    workflow.add_node("validador", validador)
    workflow.add_node("guardar_historico", guardar_historico)

    workflow.set_entry_point("memoria")
    workflow.add_edge("memoria", "contexto")
    workflow.add_edge("contexto", "responder")
    workflow.add_edge("responder", "validador")
    workflow.add_edge("validador", "guardar_historico")
    workflow.add_edge("guardar_historico", END)

    return workflow.compile()

grafo = criar_grafo()