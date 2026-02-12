from flask import Flask, request, send_file
import asyncio
import edge_tts
import os
from pydub import AudioSegment

app = Flask(__name__)

async def generate_voice(text, output_path, rate, pitch, voice="pt-BR-FranciscaNeural"):
    r = f"{rate}%" if rate.startswith(('+', '-')) else f"+{rate}%"
    p = f"{pitch}Hz" if pitch.startswith(('+', '-')) else f"+{pitch}Hz"
    
    # Processamento para voz mais humana
    processed_text = text
    processed_text = processed_text.replace("...", "<break time='800ms'/>")
    processed_text = processed_text.replace("..", "<break time='500ms'/>")
    processed_text = processed_text.replace(", ", ",<break time='200ms'/> ")
    processed_text = processed_text.replace(": ", ":<break time='300ms'/> ")
    processed_text = processed_text.replace("; ", ";<break time='300ms'/> ")
    processed_text = processed_text.replace("? ", "?<break time='600ms'/> ")
    processed_text = processed_text.replace("! ", "!<break time='600ms'/> ")
    processed_text = processed_text.replace(". ", ".<break time='400ms'/> ")
    
    # SSML para controle total
    ssml_text = f"""
    <speak version='1.0' xml:lang='pt-BR'>
        <voice name='{voice}'>
            <prosody rate='{r}' pitch='{p}'>
                {processed_text}
            </prosody>
        </voice>
    </speak>
    """
    
    temp_mp3 = "temp_audio.mp3"
    
    communicate = edge_tts.Communicate(ssml_text, voice)
    await communicate.save(temp_mp3)
    
    # Converte para OGG
    audio = AudioSegment.from_mp3(temp_mp3)
    audio.export(output_path, format="ogg", codec="libopus")
    
    if os.path.exists(temp_mp3):
        os.remove(temp_mp3)

@app.route("/falar")
def falar():
    texto = request.args.get("texto", "")
    velocidade = request.args.get("vel", "-5")  # Padrão mais lento
    tom = request.args.get("tom", "2")          # Padrão levemente mais agudo
    voz = request.args.get("voz", "pt-BR-FranciscaNeural")  # Permite escolher voz
    
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
