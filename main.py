from flask import Flask, request, send_file
import asyncio
import edge_tts
import os
from pydub import AudioSegment

app = Flask(__name__)

async def generate_voice(text, output_path, rate, pitch):
    # Usando a voz Multilingual que você testou e aprovou
    voice = "pt-BR-ThalitaMultilingualNeural"
    
    # Ajustando a velocidade (rate) e o tom (pitch)
    # Se não for enviado via URL, o padrão será -10% de vel e -3Hz de tom
    r = f"{rate}%" if rate.startswith(('+', '-')) else f"{rate}%"
    p = f"{pitch}Hz" if pitch.startswith(('+', '-')) else f"{pitch}Hz"
    
    # TRATAMENTO DE TEXTO PARA SOAR HUMANO:
    # Substituímos pontos por pausas maiores para a Thalita "respirar"
    processed_text = text.replace(". ", "... . . . ").replace("! ", "! . . . ")
    
    temp_mp3 = "temp_audio.mp3"
    
    # 1. Gera o áudio em MP3 usando a voz premium
    communicate = edge_tts.Communicate(processed_text, voice, rate=r, pitch=p)
    await communicate.save(temp_mp3)
    
    # 2. Converte para OGG com o codec libopus (Obrigatório para WhatsApp PTT)
    audio = AudioSegment.from_mp3(temp_mp3)
    audio.export(output_path, format="ogg", codec="libopus")
    
    # Limpa o arquivo MP3 temporário
    if os.path.exists(temp_mp3):
        os.remove(temp_mp3)

@app.route("/falar")
def falar():
    # Pega os parâmetros da URL (com valores padrão para máxima naturalidade)
    texto = request.args.get("texto", "")
    velocidade = request.args.get("vel", "-10") # -10% de velocidade por padrão
    tom = request.args.get("tom", "-3")        # -3Hz de tom por padrão
    
    if not texto:
        return "Erro: O parâmetro 'texto' é obrigatório", 400
    
    output_file = "audio.ogg"
    
    try:
        # Roda o processo assíncrono de geração de voz
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(generate_voice(texto, output_file, velocidade, tom))
        loop.close()
        
        # Envia o arquivo final como áudio OGG
        return send_file(output_file, mimetype="audio/ogg")
    
    except Exception as e:
        print(f"Erro no servidor: {str(e)}")
        return f"Erro interno: {str(e)}", 500

if __name__ == "__main__":
    # Rodando na porta 5000 conforme seu Dockerfile
    app.run(host="0.0.0.0", port=5000)
