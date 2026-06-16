"""
Schemas Pydantic para o agente.
Inclui o estado do LangGraph e o modelo de saída do classificador.
"""
from typing import Literal, List, Dict, Any, Optional
from pydantic import BaseModel, Field
from typing_extensions import TypedDict


# ---------- Estado global do grafo ----------
class AgenteState(TypedDict):
    session_id: str
    mensagem_original: str
    mensagem_reformulada: str
    historico: List[Dict[str, str]]
    classificacao: Dict[str, Any]       # conterá "rota" e "justificacao"
    documentos_recuperados: List[Dict]
    resposta_final: str
    erro: Optional[str]


# ---------- Saída estruturada do classificador ----------
class DecisaoRota(BaseModel):
    rota: Literal[
        "saudacao",
        "rag_institucional",
        "rag_medico",
        "emergencia",
        "fora_do_escopo",
        "contingencia"
    ] = Field(description="Rota selecionada com base na intenção")
    justificacao: str = Field(description="Breve explicação da escolha")


# ---------- Modelos de Request e Response da API ----------
class MensagemRequest(BaseModel):
    session_id: str
    mensagem: str


class MensagemResponse(BaseModel):
    resposta: str