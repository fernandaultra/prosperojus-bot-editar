from flask import Flask, request, jsonify, render_template_string, redirect, url_for
from services.gpt_service import gerar_resposta_com_gpt
import requests
import os
from dotenv import load_dotenv
import base64

load_dotenv()

app = Flask(__name__)

historico = [
    {
        "mensagem": "Olá, tenho um precatório para vender.",
        "resposta": "Olá! Posso te ajudar com isso 😊. Me diga o número do processo."
    }
]

@app.route("/", methods=["GET"])
def home():
    return "<h2>🚀 ProsperoJus Bot está rodando com sucesso!</h2>", 200

@app.route("/webhook", methods=["POST"])
def receber_mensagem():
    dados = request.json
    mensagem_cliente = dados.get("mensagem")

    if not mensagem_cliente:
        return jsonify({"erro": "Mensagem não fornecida"}), 400

    resposta_gerada = gerar_resposta_com_gpt(mensagem_cliente)

    historico.append({
        "mensagem": mensagem_cliente,
        "resposta": resposta_gerada
    })

    return jsonify({"resposta": resposta_gerada}), 200

@app.route("/mensagens", methods=["GET"])
def mensagens():
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
            .resposta { margin-top: 10px; white-space: pre-wrap; }
            textarea { width: 100%; height: 60px; margin-top: 10px; display: none; }
            button { margin-top: 10px; padding: 5px 10px; cursor: pointer; }
        </style>
        <script>
            function ativarEdicao(id) {
                const respostaText = document.getElementById('resposta-text-' + id);
                const respostaInput = document.getElementById('resposta-input-' + id);
                const editarBtn = document.getElementById('editar-btn-' + id);

                respostaText.style.display = 'none';
                respostaInput.style.display = 'block';
                editarBtn.innerText = '💾 Salvar edição';
                editarBtn.onclick = function() { document.getElementById('form-' + id).submit(); };
            }
        </script>
    </head>
    <body>
        <h1>📨 Mensagens Recebidas - ProsperoJus</h1>
        {% for item in historico %}
            <div class="card">
                <strong>Mensagem recebida:</strong><br> {{ item.mensagem }}<br><br>
                <strong>Sugestão de resposta:</strong>
                <div id="resposta-text-{{ loop.index }}" class="resposta">{{ item.resposta }}</div>

                <form method="POST" action="/editar" id="form-{{ loop.index }}">
                    <input type="hidden" name="mensagem" value="{{ item.mensagem }}">
                    <textarea name="resposta" id="resposta-input-{{ loop.index }}">{{ item.resposta }}</textarea>
                    <button type="button" onclick="ativarEdicao({{ loop.index }})" id="editar-btn-{{ loop.index }}">✏️ Editar</button>
                </form>
            </div>
        {% endfor %}
    </body>
    </html>
    """
    return render_template_string(html, historico=historico)

@app.route("/editar", methods=["POST"])
def editar():
    mensagem = request.form.get("mensagem")
    nova_resposta = request.form.get("resposta")

    for item in historico:
        if item["mensagem"] == mensagem:
            item["resposta"] = nova_resposta
            break

    atualizar_contexto_no_github()
    return redirect(url_for('mensagens'))

def atualizar_contexto_no_github():
    token = os.getenv("GITHUB_TOKEN")
    repo = "fernandaultra/prosperojus-bot-editar"
    branch = "main"
    path = "contexto.txt"

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json"
    }

    url_get = f"https://api.github.com/repos/{repo}/contents/{path}?ref={branch}"
    r_get = requests.get(url_get, headers=headers)
    if r_get.status_code != 200:
        print("Erro ao obter SHA do arquivo:", r_get.text)
        return

    sha = r_get.json()["sha"]

    novo_conteudo = "\n\n".join(
        f"📩 {item['mensagem']}\n💬 {item['resposta']}" for item in historico
    )

    payload = {
        "message": "📝 Atualização automática do contexto.txt pelo bot",
        "content": base64.b64encode(novo_conteudo.encode()).decode("utf-8"),
        "sha": sha,
        "branch": branch
    }

    r_put = requests.put(url_get, headers=headers, json=payload)

    if r_put.status_code == 200 or r_put.status_code == 201:
        print("✅ contexto.txt atualizado com sucesso no GitHub!")
    else:
        print("❌ Erro ao atualizar contexto.txt:", r_put.text)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
