import json
import os

# Caminho seguro mesmo que o script seja executado de outro diretório
SCRIPT_PATH = os.path.join(os.path.dirname(__file__), "..", "scripts", "respostas.json")

def carregar_respostas():
    with open(SCRIPT_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def encontrar_resposta(msg_usuario):
    respostas = carregar_respostas()
    for chave, resposta in respostas.items():
        if chave.lower() in msg_usuario.lower():
            return resposta
    return None  # Retorna None em vez de string padrão
