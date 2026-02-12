from flask import Flask, request, send_file
import asyncio
import edge_tts
import os

app = Flask(__name__)

@app.route("/falar")
async def falar():
    texto = request.args.get("texto")
    # Voz Francisca (Neural) - A melhor para converter vendas de emagrecimento
    communicate = edge_tts.Communicate(texto, "pt-BR-FranciscaNeural")
    await communicate.save("audio.mp3")
    return send_file("audio.mp3", mimetype="audio/mpeg")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
