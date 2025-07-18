import logging
import requests
from services.sheets_service import listar_mensagens
from datetime import datetime

# Configura logging
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(message)s')

# URL pública do seu webhook Flask no Render
WEBHOOK_URL = "https://prosperojus-bot-editar.onrender.com/webhook"

def enviar_respostas():
    mensagens = listar_mensagens()
    processadas = 0

    for mensagem in mensagens:
        numero = mensagem.get("Telefone") or mensagem.get("remetente")
        texto = mensagem.get("Mensagem") or mensagem.get("mensagem")
        resposta = mensagem.get("Resposta") or mensagem.get("resposta_sugerida")

        if texto and not resposta:
            payload = {
                "sender": numero,
                "message": texto
            }

            logging.info(f"📨 Enviando mensagem para webhook: {payload}")

            try:
                r = requests.post(WEBHOOK_URL, json=payload)
                if r.status_code == 200:
                    logging.info(f"✅ Mensagem de {numero} enviada com sucesso para o webhook")
                    processadas += 1
                else:
                    logging.warning(f"⚠️ Erro ao enviar para webhook: {r.status_code} - {r.text}")
            except Exception as e:
                logging.error(f"❌ Erro ao enviar requisição: {e}")

    logging.info(f"📊 Total de mensagens processadas: {processadas}")
    return processadas

if __name__ == "__main__":
    enviar_respostas()
