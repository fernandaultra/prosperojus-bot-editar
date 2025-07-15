from flask import Flask, request, jsonify, render_template_string, redirect, url_for
from services.gpt_service import gerar_resposta_com_gpt
from utils.audio_utils import download_audio
from datetime import datetime
from markdown import markdown
from markupsafe import Markup
import openai
import os

app = Flask(__name__)

historico_por_telefone = {}
MAX_MENSAGENS = 10

@app.route("/", methods=["GET"])
def home():
    return "<h2>🚀 ProsperoJus Bot está rodando com sucesso!</h2>", 200

@app.route("/webhook", methods=["POST"])
def receber_mensagem():
    dados = request.get_json(force=True)
    telefone = dados.get("telefone")
    mensagem_cliente = dados.get("mensagem")

    if not telefone or not mensagem_cliente:
        return jsonify({"erro": "Telefone ou mensagem não fornecidos"}), 400

    resposta_gerada = gerar_resposta_com_gpt(mensagem_cliente)

    if telefone not in historico_por_telefone:
        historico_por_telefone[telefone] = []

    historico_por_telefone[telefone].insert(0, {
        "mensagem": mensagem_cliente,
        "resposta": resposta_gerada,
        "html": Markup(markdown(resposta_gerada)),
        "datahora": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    })

    historico_por_telefone[telefone] = historico_por_telefone[telefone][:MAX_MENSAGENS]

    return jsonify({"resposta": resposta_gerada}), 200

@app.route("/mensagens", methods=["GET"])
def mensagens():
    telefone_selecionado = request.args.get("telefone")
    telefones = list(historico_por_telefone.keys())
    mensagens = historico_por_telefone.get(telefone_selecionado, []) if telefone_selecionado else []

    html = """
    <html>
    <head>
        <title>Mensagens Recebidas - ProsperoJus</title>
        <style>
            body { font-family: Arial; padding: 20px; background-color: #f9f9f9; }
            .card {
                background-color: white;
                padding: 15px;
                border-radius: 10px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                margin-bottom: 20px;
            }
            textarea { width: 100%; height: 60px; margin-top: 10px; }
            button { margin-top: 5px; padding: 5px 10px; }
        </style>
    </head>
    <body>
        <h1>📨 Mensagens Recebidas - ProsperoJus</h1>
        {% for tel in telefones %}
            <a href="/mensagens?telefone={{ tel }}">{{ tel }}</a> |
        {% endfor %}

        <hr>
        {% for item in mensagens %}
            <div class="card">
                <strong>📅 {{ item.datahora }}</strong><br>
                <strong>📥 Mensagem:</strong><br> {{ item.mensagem }}<br><br>
                <strong>🤖 Sugestão:</strong>
                <div>{{ item.html|safe }}</div>
            </div>
        {% endfor %}
    </body>
    </html>
    """
    return render_template_string(html, telefones=telefones, telefone=telefone_selecionado, mensagens=mensagens)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
