from flask import Flask, request, send_file
import asyncio
import edge_tts
import os

app = Flask(__name__)

async def generate_voice(text, output_path, rate, pitch):
    # Se houver tags de pausa, criamos o XML que o motor da voz entende
    if "<break" in text:
        # Monta o pacote SSML necessário para o edge-tts
        ssml = f"""<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="pt-BR">
                   <voice name="pt-BR-ThalitaNeural">
                   <prosody rate="{rate}%" pitch="{pitch}Hz">{text}</prosody>
                   </voice>
                   </speak>"""
        communicate = edge_tts.Communicate(ssml, "pt-BR-ThalitaNeural")
    else:
        # Texto simples sem pausas complexas
        rate_str = f"{rate}%" if rate.startswith(('+', '-')) else f"+{rate}%"
        communicate = edge_tts.Communicate(text, "pt-BR-ThalitaNeural", rate=rate_str)
        
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
        return str(e), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
