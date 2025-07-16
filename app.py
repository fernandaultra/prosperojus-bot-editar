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
    return "<h2>🚀 ProsperoJus Bot está rodando com sucesso!</h2>", 200

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
        "datahora": datahora.strftime("%Y-%m-%d %H:%M:%S.%f")
    })

    historico_por_telefone[numero] = historico_por_telefone[numero][:MAX_MENSAGENS]
    return jsonify({"status": "ok"}), 200

@app.route("/mensagens", methods=["GET"])
def mensagens():
    telefone = request.args.get("telefone")
    telefones = list(historico_por_telefone.keys())
    mensagens = historico_por_telefone.get(telefone, [])

    html = """
    <html>
    <head>
        <meta charset='utf-8'>
        <meta http-equiv="refresh" content="10">
        <title>📨 Mensagens - ProsperoJus</title>
        <style>
            body { font-family: Arial; padding: 20px; }
            .abas a { margin-right: 10px; text-decoration: none; padding: 8px; border: 1px solid #ccc; border-radius: 5px; }
            .card { border: 1px solid #ccc; padding: 15px; border-radius: 8px; margin-top: 10px; background: #f9f9f9; }
            .sugestao { margin-top: 10px; }
            textarea { width: 100%; height: 100px; display: none; margin-top: 10px; }
            button { margin-top: 5px; margin-right: 10px; cursor: pointer; padding: 6px 12px; border: none; border-radius: 5px; }
        </style>
        <script>
            function editar(id) {
                document.getElementById('resposta-'+id).style.display = 'none';
                document.getElementById('edit-'+id).style.display = 'block';
                document.getElementById('btn-editar-'+id).style.display = 'none';
                document.getElementById('btn-salvar-'+id).style.display = 'inline';
            }
            function copiarTexto(id) {
                navigator.clipboard.writeText(document.getElementById(id).innerText);
                alert('Texto copiado!');
            }
        </script>
    </head>
    <body>
        <h2>📨 Mensagens Recebidas - ProsperoJus</h2>
        <div class="abas">
            {% for tel in telefones %}
                <a href="/mensagens?telefone={{ tel }}">{{ tel }}</a>
            {% endfor %}
        </div>
        {% for item in mensagens %}
            <div class="card">
                <div><strong>📅 {{ item.datahora }}</strong></div>
                <div><strong>📥 Mensagem:</strong> {{ item.mensagem }}</div>
                <div class="sugestao">
                    <strong>🤖 Sugestão:</strong>
                    <div id="resposta-{{ loop.index }}">{{ item.html|safe }}</div>
                    <form method="POST" action="/editar">
                        <input type="hidden" name="telefone" value="{{ telefone }}">
                        <input type="hidden" name="datahora" value="{{ item.datahora }}">
                        <textarea name="nova_resposta" id="edit-{{ loop.index }}">{{ item.resposta }}</textarea>
                        <button type="button" id="btn-editar-{{ loop.index }}" style="background-color:#f9c74f;" onclick="editar({{ loop.index }})">✏️ Editar</button>
                        <button type="submit" id="btn-salvar-{{ loop.index }}" style="display:none;background-color:#f9c74f;">📎 Salvar texto</button>
                        <button type="button" style="background-color:#90be6d;" onclick="copiarTexto('resposta-{{ loop.index }}')">📋 Copiar</button>
                    </form>
                </div>
            </div>
        {% endfor %}
    </body>
    </html>
    """
    return render_template_string(html, telefones=telefones, telefone=telefone, mensagens=mensagens)

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
