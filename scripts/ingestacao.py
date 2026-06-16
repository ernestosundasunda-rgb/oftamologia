"""
Script para carregar documentos JSON da pasta dados/ e indexá-los no Supabase.
Deve ser executado uma vez (ou sempre que os documentos forem atualizados).
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))  # Adiciona a raiz ao PYTHONPATH

import os
import json
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.core.embeddings import criar_embeddings
from app.db.supabase_client import supabase
# Configurações
PASTA_DADOS = Path(__file__).parent.parent / "dados"
CHUNK_SIZE = 800
CHUNK_OVERLAP = 100

embeddings = criar_embeddings()
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE,
    chunk_overlap=CHUNK_OVERLAP,
    separators=["\n\n", "\n", ". ", "? ", "! ", " ", ""]
)

def carregar_e_indexar():
    for tipo in ["institucional", "medico"]:
        pasta = PASTA_DADOS / tipo
        if not pasta.exists():
            continue

        for arquivo in pasta.glob("*.json"):
            with open(arquivo, "r", encoding="utf-8") as f:
                documentos = json.load(f)

            for doc in documentos:
                conteudo = doc.get("conteudo", "")
                if not conteudo.strip():
                    continue

                # Dividir em chunks
                chunks = text_splitter.split_text(conteudo)
                
                for i, chunk in enumerate(chunks):
                    # Gerar embedding
                    vector = embeddings.embed_query(chunk)

                    # Preparar metadados
                    metadados = {
                        "tipo": tipo,
                        "titulo": doc.get("titulo", ""),
                        "fonte": doc.get("fonte", ""),
                        "categoria": doc.get("categoria", ""),
                        "doc_id": doc.get("id", ""),
                        "chunk_index": i,
                        "arquivo": arquivo.name
                    }

                    # Inserir no Supabase
                    supabase.table("documents").insert({
                        "content": chunk,
                        "metadata": metadados,
                        "embedding": vector
                    }).execute()

                    print(f"Indexado: {doc.get('id')} (chunk {i})")

            print(f"Ficheiro {arquivo.name} processado com sucesso.")

if __name__ == "__main__":
    carregar_e_indexar()
    print("Indexação concluída!")