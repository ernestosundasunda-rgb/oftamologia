import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import json
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.core.embeddings import criar_embeddings
from app.db.supabase_client import supabase

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
    arquivo = PASTA_DADOS / "faq.json"
    if not arquivo.exists():
        print(f"Ficheiro {arquivo} não encontrado.")
        return

    with open(arquivo, "r", encoding="utf-8") as f:
        documentos = json.load(f)

    for doc in documentos:
        conteudo = doc.get("conteudo", "")
        if not conteudo.strip():
            continue

        chunks = text_splitter.split_text(conteudo)
        for i, chunk in enumerate(chunks):
            vector = embeddings.embed_query(chunk)
            metadados = {
                "tipo": "geral",
                "titulo": doc.get("titulo", ""),
                "fonte": doc.get("fonte", ""),
                "categoria": doc.get("categoria", ""),
                "doc_id": doc.get("id", ""),
                "chunk_index": i,
                "arquivo": arquivo.name
            }
            supabase.table("documents").insert({
                "content": chunk,
                "metadata": metadados,
                "embedding": vector
            }).execute()
            print(f"Indexado: {doc.get('id')} (chunk {i})")

    print("Indexação concluída!")

if __name__ == "__main__":
    carregar_e_indexar()