from flask import Flask, request, send_file
import asyncio
import edge_tts
import os

app = Flask(__name__)

# Função para gerar o áudio com a voz da Thalita
async def generate_voice(text, output_path, rate):
    # Formata a velocidade (ex: +0%, -10%, +20%)
    if not (rate.startswith('+') or rate.startswith('-')):
        rate = f"+{rate}%"
    else:
        rate = f"{rate}%"
    
    # Voz Thalita: pt-BR-ThalitaNeural
    communicate = edge_tts.Communicate(text, "pt-BR-ThalitaNeural", rate=rate)
    await communicate.save(output_path)

@app.route("/falar")
def falar():
    texto = request.args.get("texto")
    # Pega a velocidade da URL. Se não enviar, o padrão é +0 (normal)
    velocidade = request.args.get("vel", "0")
    
    if not texto:
        return "Erro: Falta o parâmetro texto", 400
    
    output_file = "audio.mp3"
    
    try:
        # Gerencia o loop de eventos para não dar erro no Docker
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(generate_voice(texto, output_file, velocidade))
        loop.close()
        
        return send_file(output_file, mimetype="audio/mpeg")
    except Exception as e:
        return f"Erro no servidor: {str(e)}", 500

if __name__ == "__main__":
    # Roda na porta 5000 conforme configurado no Easypanel
    app.run(host="0.0.0.0", port=5000)
