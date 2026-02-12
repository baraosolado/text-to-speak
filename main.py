from flask import Flask, request, send_file
import asyncio
import edge_tts
import os
import re

app = Flask(__name__)

async def generate_voice(text, output_path, rate, pitch):
    # Ajusta velocidade e tom
    r = f"{rate}%" if rate.startswith(('+', '-')) else f"+{rate}%"
    p = f"{pitch}Hz" if pitch.startswith(('+', '-')) else f"+{pitch}Hz"
    
    # TRUQUE MÁGICO: Transforma "..." em pausas de 1 segundo e "," em pausas curtas
    # Isso evita que você tenha que enviar códigos chatos pelo n8n
    processed_text = text.replace("...", "<break time='1000ms'/>")
    processed_text = processed_text.replace("..", "<break time='500ms'/>")
    
    # Monta o SSML internamente para o edge-tts não ler as tags
    ssml = f"""<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="pt-BR">
               <voice name="pt-BR-ThalitaNeural">
               <prosody rate="{r}" pitch="{p}">{processed_text}</prosody>
               </voice>
               </speak>"""
    
    communicate = edge_tts.Communicate(ssml, "pt-BR-ThalitaNeural")
    await communicate.save(output_path)

@app.route("/falar")
def falar():
    texto = request.args.get("texto")
    velocidade = request.args.get("vel", "0")
    tom = request.args.get("tom", "0")
    
    if not texto: return "Erro", 400
    
    output_file = "audio.mp3"
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(generate_voice(texto, output_file, velocidade, tom))
        loop.close()
        return send_file(output_file, mimetype="audio/mpeg")
    except Exception as e:
        return f"Erro: {str(e)}", 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
