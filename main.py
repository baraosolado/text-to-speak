from flask import Flask, request, send_file
import asyncio
import edge_tts
import os
from pydub import AudioSegment

app = Flask(__name__)

async def generate_voice(text, output_path, rate, pitch):
    voice = "pt-BR-ThalitaMultilingualNeural"
    
    r = f"{rate}%" if rate.startswith(('+', '-')) else f"{rate}%"
    p = f"{pitch}Hz" if pitch.startswith(('+', '-')) else f"{pitch}Hz"
    
    # Removemos a linha que injetava pontos extras
    # Agora o texto vai puro, respeitando apenas a pontuação da Tatiana
    temp_mp3 = "temp_audio.mp3"
    
    communicate = edge_tts.Communicate(text, voice, rate=r, pitch=p)
    await communicate.save(temp_mp3)
    
    audio = AudioSegment.from_mp3(temp_mp3)
    audio.export(output_path, format="ogg", codec="libopus")
    
    if os.path.exists(temp_mp3):
        os.remove(temp_mp3)

@app.route("/falar")
def falar():
    texto = request.args.get("texto", "")
    velocidade = request.args.get("vel", "-10") 
    tom = request.args.get("tom", "-3")        
    
    if not texto:
        return "Erro: O parâmetro 'texto' é obrigatório", 400
    
    output_file = "audio.ogg"
    
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(generate_voice(texto, output_file, velocidade, tom))
        loop.close()
        return send_file(output_file, mimetype="audio/ogg")
    except Exception as e:
        return f"Erro: {str(e)}", 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
