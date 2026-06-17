from typing import Literal, List, Dict, Any, Optional
from pydantic import BaseModel, Field
from typing_extensions import TypedDict

class AgenteState(TypedDict):
    session_id: str
    mensagem_original: str
    mensagem_reformulada: str
    historico: List[Dict[str, str]]
    classificacao: Dict[str, Any]
    documentos_recuperados: List[Dict]
    resposta_final: str
    erro: Optional[str]

class DecisaoRota(BaseModel):
    rota: Literal["saudacao", "fora_do_escopo", "rag"] = Field(description="Rota selecionada")
    justificacao: str = Field(description="Breve explicação da escolha")

class MensagemRequest(BaseModel):
    session_id: str
    mensagem: str

class MensagemResponse(BaseModel):
    resposta: str