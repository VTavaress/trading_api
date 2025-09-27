# Usa uma imagem base estável do Python
FROM python:3.11-slim

# Define o diretório de trabalho dentro do contêiner
WORKDIR /app

# Copia e instala as dependências primeiro
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o conteúdo da sua pasta 'app' local para o diretório de trabalho do contêiner
COPY ./app /app

# Comando para iniciar a API, assumindo que main.py está dentro da pasta 'app'
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]