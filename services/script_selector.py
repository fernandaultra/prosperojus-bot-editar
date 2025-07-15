import json

def carregar_respostas():
    with open("scripts/respostas.json", "r", encoding="utf-8") as f:
        return json.load(f)

def encontrar_resposta(msg_usuario):
    respostas = carregar_respostas()
    for chave, resposta in respostas.items():
        if chave.lower() in msg_usuario.lower():
            return resposta
    return "🤖 Desculpe, ainda não tenho uma resposta para isso. Poderia reformular?"
