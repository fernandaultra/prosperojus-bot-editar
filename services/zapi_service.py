import os
import requests
from dotenv import load_dotenv

load_dotenv()

ZAPI_TOKEN = os.getenv("ZAPI_TOKEN")
ZAPI_INSTANCE_ID = os.getenv("ZAPI_INSTANCE_ID")
ZAPI_URL = os.getenv("ZAPI_URL")  # Exemplo: https://api.z-api.io


def enviar_mensagem(numero, mensagem):
    headers = {
        "Content-Type": "application/json",
        "Client-Token": ZAPI_TOKEN
    }

    url = f"{ZAPI_URL}/instances/{ZAPI_INSTANCE_ID}/send-text"

    payload = {
        "phone": numero,
        "message": mensagem
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        return response.json()
    except Exception as e:
        return {"error": str(e)}
