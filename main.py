from flask import Flask, request, send_file
import asyncio
import edge_tts
import os
from pydub import AudioSegment
import html

app = Flask(__name__)

async def generate_voice(text, output_path, rate, pitch, voice="pt-BR-ThalitaNeural"):
    r = f"{rate}%" if rate.startswith(('+', '-')) else f"+{rate}%"
    p = f"{pitch}Hz" if pitch.startswith(('+', '-')) else f"+{pitch}Hz"
    
    # 🔥 LIMPA O TEXTO DE QUALQUER HTML/XML
    clean_text = html.unescape(text)  # Remove &lt; &gt; etc
    clean_text = clean_text.replace("<", "").replace(">", "")  # Remove < >
    clean_text = clean_text.replace("&", "e")  # Substitui & por "e"
    
    # Processamento para voz mais humana (SEM SSML, direto no texto)
    processed_text = clean_text
    processed_text = processed_text.replace("...", " . . . ")   # Pausa longa
    processed_text = processed_text.replace("..", " . . ")      # Pausa média
    processed_text = processed_text.replace(", ", ", . ")       # Pausa após vírgula
    processed_text = processed_text.replace(": ", ": . ")       # Pausa após dois pontos
    processed_text = processed_text.replace("; ", "; . ")
    processed_text = processed_text.replace("? ", "? . . ")     # Pausa após pergunta
    processed_text = processed_text.replace("! ", "! . . ")     # Pausa após exclamação
    processed_text = processed_text.replace(". ", ". . ")       # Pausa entre frases
    
    temp_mp3 = "temp_audio.mp3"
    
    # ✅ USAR EDGE-TTS SEM SSML (modo simples e seguro)
    communicate = edge_tts.Communicate(
        processed_text, 
        voice,
        rate=r,
        pitch=p
    )
    await communicate.save(temp_mp3)
    
    # Converte para OGG
    audio = AudioSegment.from_mp3(temp_mp3)
    audio.export(output_path, format="ogg", codec="libopus")
    
    if os.path.exists(temp_mp3):
        os.remove(temp_mp3)

@app.route("/falar")
def falar():
    texto = request.args.get("texto", "")
    velocidade = request.args.get("vel", "-8")
    tom = request.args.get("tom", "3")
    voz = request.args.get("voz", "pt-BR-ThalitaNeural")
    
    if not texto: 
        return "Erro: Texto não fornecido", 400
    
    output_file = "audio.ogg"
    
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(generate_voice(texto, output_file, velocidade, tom, voz))
        loop.close()
        
        return send_file(output_file, mimetype="audio/ogg")
    except Exception as e:
        return f"Erro: {str(e)}", 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
