from flask import Flask, request, send_file
import asyncio
import edge_tts
import os

app = Flask(__name__)

# Função principal para gerar a voz
async def generate_voice(text, output_path, rate, pitch):
    # Garante que a velocidade e o tom tenham o formato correto (+0%, -5%, etc)
    r = f"{rate}%" if rate.startswith(('+', '-')) else f"+{rate}%"
    p = f"{pitch}Hz" if pitch.startswith(('+', '-')) else f"+{pitch}Hz"
    
    # TRUQUE DE HUMANIZAÇÃO: 
    # Substituímos os pontos por tags de pausa que o edge-tts entende internamente
    # Sem que o n8n precise enviar HTML chato.
    processed_text = text.replace("...", "<break time='1000ms'/>")
    processed_text = processed_text.replace("..", "<break time='500ms'/>")
    
    # Montamos o SSML (o roteiro da Thalita)
    ssml = f"""<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="pt-BR">
               <voice name="pt-BR-ThalitaNeural">
               <prosody rate="{r}" pitch="{p}">{processed_text}</prosody>
               </voice>
               </speak>"""
    
    communicate = edge_tts.Communicate(ssml, "pt-BR-ThalitaNeural")
    await communicate.save(output_path)

@app.route("/falar")
def falar():
    # Pega os dados da URL
    texto = request.args.get("texto", "")
    velocidade = request.args.get("vel", "0")
    tom = request.args.get("tom", "0")
    
    if not texto:
        return "Erro: O campo texto está vazio", 400
    
    output_file = "audio.mp3"
    
    try:
        # Cria um novo loop de eventos para cada requisição (evita erro de servidor travado)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(generate_voice(texto, output_file, velocidade, tom))
        loop.close()
        
        return send_file(output_file, mimetype="audio/mpeg")
    except Exception as e:
        # Se der erro, ele avisa o que foi nos logs
        print(f"Erro detectado: {e}")
        return f"Erro interno: {str(e)}", 500

if __name__ == "__main__":
    # Roda na porta 5000 do Easypanel
    app.run(host="0.0.0.0", port=5000, debug=False)
