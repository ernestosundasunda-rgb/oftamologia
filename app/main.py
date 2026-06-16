"""
Ponto de entrada da aplicação FastAPI.
"""
from fastapi import FastAPI
from app.api.routes import router

import logging
logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="Assistente Oftalmológico",
    description="Agente conversacional inteligente para centro oftalmológico",
    version="1.0.0"
)

app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)