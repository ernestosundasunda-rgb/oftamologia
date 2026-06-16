"""
Endpoints da API.
Neste momento apenas a rota POST /chat que invoca o grafo.
"""
from fastapi import APIRouter, HTTPException
from app.models.agent import MensagemRequest, MensagemResponse
from app.graph.builder import grafo  # Será criado depois

router = APIRouter()


@router.post("/chat", response_model=MensagemResponse)
async def chat(request: MensagemRequest) -> MensagemResponse:
    """
    Endpoint principal que processa a mensagem do utilizador.
    O frontend envia { session_id, mensagem } e recebe { resposta }.
    """
    try:
        # Construir estado inicial
        estado_inicial = {
            "session_id": request.session_id,
            "mensagem_original": request.mensagem,
            "mensagem_reformulada": "",
            "historico": [],
            "classificacao": {},
            "documentos_recuperados": [],
            "resposta_final": "",
            "erro": None,
        }

        # Invocar o grafo
        estado_final = await grafo.ainvoke(estado_inicial)

        # Extrair resposta
        resposta = estado_final.get("resposta_final", "")

        return MensagemResponse(resposta=resposta)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")