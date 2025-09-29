# Dockerfile

# 1. Imagem base
FROM python:3.11-slim

# 2. Diretório de trabalho
WORKDIR /app

# 3. Copia apenas requirements para cache de dependências
COPY requirements.txt .

# 4. Instala dependências
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copia todo o projeto para o container
COPY . .

# 6. Ajusta PYTHONPATH para garantir que o módulo 'app' seja encontrado
ENV PYTHONPATH=/app

# 7. Comando padrão para rodar a API
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
