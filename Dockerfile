# Usa uma imagem leve do Python
FROM python:3.10-slim

# Define a pasta de trabalho dentro do container
WORKDIR /app

# Instala as dependências necessárias do sistema para áudio
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

# Copia os arquivos do seu GitHub para dentro do container
COPY . .

# Instala as bibliotecas Python
RUN pip install --no-cache-dir edge-tts flask

# Expõe a porta que a API vai usar
EXPOSE 5000

# Comando para iniciar a API
CMD ["python", "main.py"]
