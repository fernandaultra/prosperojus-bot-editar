from flask import Flask, request, jsonify, render_template_string, redirect
from services.gpt_service import gerar_resposta_com_gpt
from markdown import markdown
from markupsafe import Markup
from datetime import datetime
from collections import defaultdict
from utils.audio_utils import download_audio
import openai
import os

app = Flask(__name__)
historico = []

@app.route("/", methods=["GET"])
def home():
    return "<h2>🚀 ProsperoJus Bot está rodando com sucesso!</h2>", 200

@app.route("/webhook", methods=["POST"])
def receber_mensagem():
    try:
        dados = request.get_json(force=True)
    except Exception as e:
        return jsonify({"error": "Erro ao interpretar JSON", "detalhe": str(e)}), 400

    numero = dados.get("phone") or dados.get("from") or dados.get("remoteJid") or dados.get("sender")
    mensagem = (
        dados.get("message") or
        dados.get("body") or
        dados.get("text") or
        dados.get("text", {}).get("message") or
        dados.get("messageData", {}).get("textMessageData", {}).get("textMessage")
    )

    sugestao = ""

    try:
        if not mensagem and dados.get("audio", {}).get("audioUrl"):
            audio_url = dados["audio"]["audioUrl"]
            local_path = download_audio(audio_url)
            with open(local_path, "rb") as audio_file:
                transcript = openai.Audio.transcribe("whisper-1", audio_file)
            transcribed = transcript["text"]
            mensagem = f"[ÁUDIO TRANSCRITO] {transcribed}"
            sugestao = gerar_resposta_com_gpt(transcribed)
        elif mensagem:
            sugestao = gerar_resposta_com_gpt(mensagem)
        else:
            mensagem = "[❗Mensagem não identificada ou sem conteúdo processável]"
            sugestao = "⚠️ Tivemos um problema ao gerar a resposta. Pode tentar novamente em instantes?"
    except Exception as e:
        mensagem = mensagem or "[⚠️ Erro ao processar áudio/texto]"
        sugestao = "⚠️ Tivemos um problema ao gerar a resposta. Pode tentar novamente em instantes?"

    historico.append({
        "numero": numero,
        "mensagem": mensagem,
        "sugestao": sugestao,
        "datahora": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    })

    return jsonify({
        "status": "mensagem registrada",
        "mensagem_recebida": mensagem,
        "sugestao_de_resposta": sugestao
    }), 200

@app.route("/mensagens", methods=["GET"])
def exibir_mensagens():
    agrupadas = defaultdict(list)
    for item in reversed(historico):
        agrupadas[item["numero"]].append(item)
        agrupadas[item["numero"]] = agrupadas[item["numero"]][:10]

    for lista in agrupadas.values():
        for item in lista:
            item["sugestao_html"] = Markup(markdown(item["sugestao"]))

    html_template = """...HTML OMITIDO AQUI POR BREVIDADE..."""
    return render_template_string(html_template, agrupadas=agrupadas)

@app.route("/atualizar_contexto", methods=["POST"])
def atualizar_contexto():
    dados = request.get_json()
    texto = dados.get("texto", "").strip()
    numero = dados.get("numero")

    if not texto:
        return jsonify({"error": "Texto vazio"}), 400

    timestamp = datetime.now().strftime("%d/%m/%Y %H:%M")
    entrada = f"\n\nCLIENTE: {numero}\nSUGESTÃO ORIGINAL: (original omitida)\nRESPOSTA EDITADA ({timestamp}):\n{texto}\n---"

    try:
        with open("contexto.txt", "a", encoding="utf-8") as f:
            f.write(entrada)
        return jsonify({"status": "✅ Resposta salva com sucesso no contexto.txt"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=True)