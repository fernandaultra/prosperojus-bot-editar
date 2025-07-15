from flask import Flask, request, jsonify, render_template_string
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

    html_template = """
    <html>
    <head>
        <meta charset="utf-8">
        <title>💬 Mensagens Recebidas - ProsperoJus</title>
        <meta http-equiv="refresh" content="15">
        <style>
            body { font-family: Arial; padding: 20px; background: #f5f5f5; }
            .aba { margin-bottom: 20px; }
            .mensagem { background: #fff; border-radius: 10px; padding: 15px; margin-bottom: 10px; box-shadow: 0 0 5px rgba(0,0,0,0.1); }
            .data { color: #888; font-size: 12px; }
            .sugestao { margin-top: 10px; background: #eef; padding: 10px; border-radius: 5px; }
            .btn { margin-top: 5px; cursor: pointer; padding: 5px 10px; border: none; border-radius: 4px; }
            .btn-copiar { background-color: #4CAF50; color: white; }
            .btn-editar { background-color: #2196F3; color: white; margin-left: 5px; }
            .btn-salvar { background-color: #FF9800; color: white; display: none; margin-left: 5px; }
            [contenteditable] { outline: 1px dashed #666; min-height: 60px; }
        </style>
        <script>
            function copiarTexto(id) {
                const texto = document.getElementById(id).innerText;
                navigator.clipboard.writeText(texto).then(() => alert('Texto copiado!'));
            }

            function editar(id, btnId) {
                const el = document.getElementById(id);
                el.setAttribute('contenteditable', true);
                document.getElementById(btnId).style.display = 'inline-block';
                el.focus();
            }

            function salvar(id, numero) {
                const texto = document.getElementById(id).innerText;
                fetch('/atualizar_contexto', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ texto: texto, numero: numero })
                })
                .then(r => r.json())
                .then(r => alert(r.status || r.error));
            }
        </script>
    </head>
    <body>
        <h1>📨 Mensagens Recebidas - ProsperoJus</h1>
        {% for numero, mensagens in agrupadas.items() %}
            <h3>📱 {{ numero }}</h3>
            {% for item in mensagens %}
                <div class="mensagem">
                    <div class="data">📅 {{ item["datahora"] }}</div>
                    <strong>Mensagem:</strong> {{ item["mensagem"] }}
                    <div class="sugestao">
                        <strong>Sugestão:</strong>
                        <div id="sugestao{{ loop.index }}" class="editable">{{ item["sugestao_html"] }}</div>
                        <button class="btn btn-copiar" onclick="copiarTexto('sugestao{{ loop.index }}')">📋 Copiar</button>
                        <button class="btn btn-editar" onclick="editar('sugestao{{ loop.index }}', 'salvar{{ loop.index }}')">✏️ Editar</button>
                        <button id="salvar{{ loop.index }}" class="btn btn-salvar" onclick="salvar('sugestao{{ loop.index }}', '{{ numero }}')">💾 Salvar Edição</button>
                    </div>
                </div>
            {% endfor %}
        {% endfor %}
    </body>
    </html>
    """
    return render_template_string(html_template, agrupadas=agrupadas)

@app.route("/atualizar_contexto", methods=["POST"])
def atualizar_contexto():
    dados = request.get_json()
    texto = dados.get("texto", "").strip()
    numero = dados.get("numero")

    if not texto:
        return jsonify({"error": "Texto vazio"}), 400

    timestamp = datetime.now().strftime("%d/%m/%Y %H:%M")
    entrada = f"\n\n### Resposta Editada - {timestamp} - {numero}\n{texto}"

    try:
        with open("contexto.txt", "a", encoding="utf-8") as f:
            f.write(entrada)
        return jsonify({"status": "✅ Resposta salva com sucesso no contexto.txt"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=True)
