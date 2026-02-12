from flask import Flask, request, send_file
import asyncio
import edge_tts
import os

app = Flask(__name__)

async def generate_voice(text, output_path, rate, pitch):
    # Formatação de velocidade e tom
    rate_str = f"{rate}%" if rate.startswith(('+', '-')) else f"+{rate}%"
    pitch_str = f"{pitch}Hz" if pitch.startswith(('+', '-')) else f"+{pitch}Hz"
    
    # Substitui os pontos por silêncio REAL
    # Usamos o formato simplificado que o edge-tts converte melhor
    processed_text = text.replace("...", " . ")
    processed_text = processed_text.replace("..", " . ")

    # Criamos o objeto de comunicação direto
    # Se o SSML está lendo o código, vamos usar o Communicate direto com os ajustes
    communicate = edge_tts.Communicate(
        text=text, 
        voice="pt-BR-ThalitaNeural",
        rate=rate_str,
        pitch=pitch_str
    )
    
    await communicate.save(output_path)

@app.route("/falar")
def falar():
    texto = request.args.get("texto", "")
    velocidade = request.args.get("vel", "0")
    tom = request.args.get("tom", "0")
    
    if not texto:
        return "Erro: Texto vazio", 400
    
    output_file = "audio.mp3"
    
    try:
        # Garantindo que o loop de eventos funcione em cada chamada
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(generate_voice(texto, output_file, velocidade, tom))
        loop.close()
        
        return send_file(output_file, mimetype="audio/mpeg")
    except Exception as e:
        return f"Erro: {str(e)}", 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
