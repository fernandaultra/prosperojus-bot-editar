from flask import Flask, request, jsonify, render_template_string, redirect, url_for
from services.gpt_service import gerar_resposta_com_gpt
from utils.audio_utils import download_audio
import openai
import os
import base64
import requests
from dotenv import load_dotenv
from datetime import datetime
from markdown import markdown
from markupsafe import Markup

app = Flask(__name__)
load_dotenv()

historico_por_telefone = {}
MAX_MENSAGENS = 10

@app.route("/", methods=["GET"])
def home():
    return "<h2>🚀 ProsperoJus Bot está rodando com sucesso!</h2>", 200

@app.route("/webhook", methods=["POST"])
def receber_mensagem():
    try:
        dados = request.get_json(force=True)
        print("📥 JSON recebido:", dados)
    except Exception as e:
        return jsonify({"erro": f"Erro ao ler JSON: {e}"}), 400

    numero = dados.get("phone") or dados.get("from") or dados.get("remoteJid") or dados.get("sender")

    # Detecção robusta da mensagem recebida
    mensagem = None
    campos = [
        ("message", str),
        ("body", str),
        ("text", str),
        ("text", dict),
        ("messageData", dict)
    ]

    for campo, tipo_esperado in campos:
        valor = dados.get(campo)
        if isinstance(valor, tipo_esperado):
            if isinstance(valor, dict):
                mensagem = valor.get("message") or valor.get("textMessage")
            else:
                mensagem = valor
            if mensagem:
                break

    # Se ainda estiver no formato {'message': '...'}
    if isinstance(mensagem, dict) and "message" in mensagem:
        mensagem = mensagem["message"]
    elif isinstance(mensagem, str) and mensagem.startswith("{'message':"):
        mensagem = mensagem.replace("{'message': '", "").rstrip("'}")

    resposta = ""
    try:
        if not mensagem and dados.get("audio", {}).get("audioUrl"):
            audio_url = dados["audio"]["audioUrl"]
            local_path = download_audio(audio_url)
            with open(local_path, "rb") as f:
                transcript = openai.Audio.transcribe("whisper-1", f)
            mensagem = f"[ÁUDIO TRANSCRITO] {transcript['text']}"
            resposta = gerar_resposta_com_gpt(transcript['text'])
        elif mensagem:
            resposta = gerar_resposta_com_gpt(mensagem)
        else:
            mensagem = "[mensagem vazia ou sem suporte]"
            resposta = "⚠️ Não foi possível gerar uma resposta."
    except Exception as e:
        resposta = f"⚠️ Erro ao gerar sugestão: {e}"

    if numero not in historico_por_telefone:
        historico_por_telefone[numero] = []

    datahora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    historico_por_telefone[numero].insert(0, {
        "mensagem": mensagem,
        "resposta": resposta,
        "html": Markup(markdown(resposta)),
        "datahora": datahora
    })

    historico_por_telefone[numero] = historico_por_telefone[numero][:MAX_MENSAGENS]

    return jsonify({"resposta": resposta}), 200

# (restante do código permanece inalterado)
@app.route("/mensagens", methods=["GET"])
def mensagens():
    telefone = request.args.get("telefone")
    telefones = list(historico_por_telefone.keys())
    mensagens = historico_por_telefone.get(telefone, [])

    html = """
    <!-- (HTML do template permanece inalterado) -->
    """
    return render_template_string(html, telefones=telefones, telefone=telefone, mensagens=mensagens)

# (rotas de edição e github permanecem iguais)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
