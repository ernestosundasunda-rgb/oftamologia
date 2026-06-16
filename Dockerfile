# Imagem base Python
FROM python:3.11-slim

# Diretório de trabalho
WORKDIR /app

# Instalar dependências do sistema (se necessário)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o código da aplicação
COPY . .

# Expor a porta
EXPOSE 8000

# Comando de arranque
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]