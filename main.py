from flask import Flask, request, send_file
import asyncio
import edge_tts
import os

app = Flask(__name__)

async def generate_voice(text, output_path, rate, pitch):
    # Formata velocidade e tom
    rate_str = f"{rate}%" if rate.startswith(('+', '-')) else f"+{rate}%"
    pitch_str = f"{pitch}Hz" if pitch.startswith(('+', '-')) else f"+{pitch}Hz"
    
    # Se o texto já vier com as tags <speak>, usamos SSML direto
    if "<speak" in text:
        communicate = edge_tts.Communicate(text, "pt-BR-ThalitaNeural", rate=rate_str, pitch=pitch_str)
    else:
        communicate = edge_tts.Communicate(text, "pt-BR-ThalitaNeural", rate=rate_str, pitch=pitch_str)
        
    await communicate.save(output_path)

@app.route("/falar")
def falar():
    texto = request.args.get("texto")
    velocidade = request.args.get("vel", "0")
    tom = request.args.get("tom", "0") # Novo: controla se a voz é mais aguda ou grave
    
    if not texto: return "Erro", 400
    
    output_file = "audio.mp3"
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(generate_voice(texto, output_file, velocidade, tom))
        loop.close()
        return send_file(output_file, mimetype="audio/mpeg")
    except Exception as e:
        return str(e), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
