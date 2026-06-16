"""
Nó 10 - Validador (modo observador)
Atualmente apenas regista a resposta. Pode ser reativado no futuro.
"""
from loguru import logger
from app.graph.state import AgenteState

async def validador(state: AgenteState) -> AgenteState:
    logger.info(f"Validador (bypass): resposta gerada com {len(state.get('resposta_final', ''))} caracteres")
    return state