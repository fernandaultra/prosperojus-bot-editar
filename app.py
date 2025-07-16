from flask import Flask, request, jsonify, render_template_string, redirect, url_for
from services.gpt_service import gerar_resposta_com_gpt
from services.db import salvar_mensagem, listar_mensagens
from utils.audio_utils import download_audio
from datetime import datetime
from markdown import markdown
from markupsafe import Markup
import os
import base64
import requests
from dotenv import load_dotenv

app = Flask(__name__)
load_dotenv()

historico_por_telefone = {}
MAX_MENSAGENS = 10

@app.route("/", methods=["GET"])
def home():
    return u"<h2>🚀 ProsperoJus Bot está rodando com sucesso!</h2>", 200

@app.route("/webhook", methods=["POST"])
def webhook():
    dados = request.get_json(force=True)

    numero = dados.get("phone") or dados.get("from") or dados.get("remoteJid") or dados.get("sender")

    mensagem = (
        dados.get("message") or
        dados.get("body") or
        dados.get("text") or
        dados.get("text", {}).get("message") or
        dados.get("messageData", {}).get("textMessageData", {}).get("textMessage")
    )

    if isinstance(mensagem, dict) and "message" in mensagem:
        mensagem = mensagem["message"]
    elif isinstance(mensagem, str) and mensagem.startswith("{'message':"):
        mensagem = mensagem.replace("{'message': '", "").rstrip("'}")

    if not numero or not mensagem:
        return jsonify({"erro": "Número ou mensagem ausente"}), 400

    resposta = gerar_resposta_com_gpt(mensagem)
    datahora = datetime.now()

    salvar_mensagem(numero, mensagem, resposta, datahora)

    if numero not in historico_por_telefone:
        historico_por_telefone[numero] = []

    historico_por_telefone[numero].insert(0, {
        "mensagem": mensagem,
        "resposta": resposta,
        "html": Markup(markdown(resposta)),
        "datahora": datahora.strftime("%d/%m/%Y %H:%M:%S")
    })

    historico_por_telefone[numero] = historico_por_telefone[numero][:MAX_MENSAGENS]
    return jsonify({"status": "ok"}), 200

@app.route("/mensagens", methods=["GET"])
def mensagens():
    registros = listar_mensagens()
    html = """
    <html>
    <head>
        <meta charset='utf-8'>
        <meta http-equiv="refresh" content="15">
        <title>📨 Mensagens - ProsperoJus</title>
        <style>
            body { font-family: Arial; padding: 20px; }
            .card { border: 1px solid #ccc; padding: 15px; border-radius: 8px; margin-top: 10px; background: #f9f9f9; }
            .botao { margin-top: 5px; margin-right: 10px; padding: 5px 10px; cursor: pointer; }
            textarea { width: 100%; height: 100px; margin-top: 10px; }
        </style>
        <script>
            function copiarTexto(id) {
                var texto = document.getElementById(id).textContent;
                navigator.clipboard.writeText(texto).then(() => {
                    alert("Texto copiado para a área de transferência!");
                });
            }
        </script>
    </head>
    <body>
        <h2>📨 Mensagens Recebidas - ProsperoJus</h2>
        {% for tel, msg, resposta, data in registros %}
            <div class="card">
                <div><strong>📱 {{ tel }}</strong></div>
                <div><strong>📧 Mensagem:</strong> {{ msg }}</div>
                <div><strong> Resposta sugerida:</strong></div>
                <div id="resposta_{{ loop.index }}">{{ resposta or "⚠️ Resposta ainda não gerada." }}</div>
                <em>{{ data }}</em>
                <form method="POST" action="/editar">
                    <input type="hidden" name="telefone" value="{{ tel }}">
                    <input type="hidden" name="datahora" value="{{ data }}">
                    <textarea name="nova_resposta">{{ resposta or "" }}</textarea>
                    <br>
                    <button type="submit" class="botao">✏️ Editar Resposta</button>
                    <button type="button" class="botao" onclick="copiarTexto('resposta_{{ loop.index }}')">📋 Copiar</button>
                </form>
            </div>
        {% endfor %}
    </body>
    </html>
    """
    return render_template_string(html, registros=registros)

@app.route("/editar", methods=["POST"])
def editar():
    telefone = request.form.get("telefone")
    datahora = request.form.get("datahora")
    nova_resposta = request.form.get("nova_resposta")

    for item in historico_por_telefone.get(telefone, []):
        if item['datahora'] == datahora:
            item['resposta'] = nova_resposta
            item['html'] = Markup(markdown(nova_resposta))
            break

    atualizar_contexto_no_github()
    return redirect(url_for('mensagens', telefone=telefone))

def atualizar_contexto_no_github():
    token = os.getenv("GITHUB_TOKEN")
    repo = "fernandaultra/prosperojus-bot-editar"
    branch = "main"
    path = "contexto.txt"

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json"
    }

    r_get = requests.get(f"https://api.github.com/repos/{repo}/contents/{path}?ref={branch}", headers=headers)
    if r_get.status_code != 200:
        print("Erro ao obter SHA:", r_get.text)
        return
    sha = r_get.json()["sha"]

    conteudo_total = []
    for tel, lista in historico_por_telefone.items():
        for item in lista:
            conteudo_total.append(f"📩 {item['mensagem']}\n {item['resposta']}")
    novo_texto = "\n\n".join(conteudo_total)

    payload = {
        "message": "📝 Atualização automática do contexto.txt",
        "content": base64.b64encode(novo_texto.encode()).decode("utf-8"),
        "sha": sha,
        "branch": branch
    }
    r_put = requests.put(f"https://api.github.com/repos/{repo}/contents/{path}", headers=headers, json=payload)
    print("✅ Atualização GitHub status:", r_put.status_code)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
