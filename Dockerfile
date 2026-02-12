# Usa uma imagem leve do Python
FROM python:3.10-slim

# Define a pasta de trabalho dentro do container
WORKDIR /app

# Instala as dependências do sistema (FFMPEG é vital para converter para OGG)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copia todos os arquivos do GitHub para dentro do container
COPY . .

# Instala todas as bibliotecas listadas no seu requirements.txt
# Isso inclui o pydub, flask e edge-tts automaticamente
RUN pip install --no-cache-dir -r requirements.txt

# Expõe a porta que a API vai usar
EXPOSE 5000

# Comando para iniciar a API
CMD ["python", "main.py"]
