from flask import Flask, request, send_file
import asyncio
import edge_tts
import os
from pydub import AudioSegment

app = Flask(__name__)

async def generate_voice(text, output_path, rate, pitch):
    r = f"{rate}%" if rate.startswith(('+', '-')) else f"+{rate}%"
    p = f"{pitch}Hz" if pitch.startswith(('+', '-')) else f"+{pitch}Hz"
    
    # Substituições de pausas humanas
    processed_text = text.replace("...", " . ").replace("..", " . ")
    
    temp_mp3 = "temp_audio.mp3"
    
    # 1. Gera em MP3 primeiro (padrão do edge-tts)
    communicate = edge_tts.Communicate(processed_text, "pt-BR-ThalitaNeural", rate=r, pitch=p)
    await communicate.save(temp_mp3)
    
    # 2. Converte MP3 para OGG (Formato que o WhatsApp ama)
    audio = AudioSegment.from_mp3(temp_mp3)
    audio.export(output_path, format="ogg", codec="libopus")
    
    # Limpa o arquivo temporário
    if os.path.exists(temp_mp3):
        os.remove(temp_mp3)

@app.route("/falar")
def falar():
    texto = request.args.get("texto", "")
    velocidade = request.args.get("vel", "0")
    tom = request.args.get("tom", "0")
    
    if not texto: return "Erro", 400
    
    # Agora o arquivo final é .ogg
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
