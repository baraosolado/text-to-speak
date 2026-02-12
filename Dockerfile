# Usa a imagem oficial do Python (mantive a 3.10 que você já usava)
FROM python:3.10-slim

# Define a pasta de trabalho
WORKDIR /app

# 1. Instala o FFMPEG no sistema (Isso é o que faltava para o áudio virar OGG)
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

# 2. Copia todos os seus arquivos do GitHub (main.py, etc) para dentro do Docker
COPY . .

# 3. Força a instalação de TODAS as bibliotecas necessárias
# Flask (para a API), Edge-TTS (para a voz da Thalita) e Pydub (para a conversão)
RUN pip install --no-cache-dir flask edge-tts pydub

# 4. Abre a porta que você já usa
EXPOSE 5000

# 5. Comando para ligar a sua API
CMD ["python", "main.py"]
