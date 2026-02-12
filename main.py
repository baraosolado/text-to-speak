from flask import Flask, request, send_file
import edge_tts
import asyncio
import os

app = Flask(__name__)

# Função que realmente gera o áudio
async def generate_voice(text, output_path):
    communicate = edge_tts.Communicate(text, "pt-BR-FranciscaNeural")
    await communicate.save(output_path)

@app.route("/falar")
def falar():
    texto = request.args.get("texto")
    if not texto:
        return "Falta o parâmetro texto", 400
    
    output_file = "audio.mp3"
    
    try:
        # Loop para rodar a função assíncrona dentro do Flask
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(generate_voice(texto, output_file))
        loop.close()
        
        return send_file(output_file, mimetype="audio/mpeg")
    except Exception as e:
        return str(e), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
