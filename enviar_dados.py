import logging
import requests
from services.sheets_service import listar_mensagens

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(message)s')

WEBHOOK_URL = "https://prosperojus-bot-editar.onrender.com/webhook"

def enviar_respostas():
    mensagens_por_telefone = listar_mensagens()
    processadas = 0

    for telefone, lista in mensagens_por_telefone.items():
        for msg in lista:
            if msg.get("mensagem") and not msg.get("resposta"):
                payload = {
                    "sender": telefone,
                    "message": msg.get("mensagem")
                }

                logging.info(f"📨 Enviando mensagem para webhook: {payload}")

                try:
                    r = requests.post(WEBHOOK_URL, json=payload)
                    if r.status_code == 200:
                        logging.info(f"✅ Mensagem enviada com sucesso para {telefone}")
                        processadas += 1
                    else:
                        logging.warning(f"⚠️ Erro ao enviar para {telefone}: {r.status_code} - {r.text}")
                except Exception as e:
                    logging.error(f"❌ Erro ao enviar requisição: {e}")

    logging.info(f"📊 Total de mensagens processadas: {processadas}")


if __name__ == "__main__":
    enviar_respostas()
