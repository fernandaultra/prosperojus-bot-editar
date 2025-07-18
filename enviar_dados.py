import logging
import time
import requests
from services.sheets_service import listar_mensagens

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(message)s')

WEBHOOK_URL = "https://prosperojus-bot-editar.onrender.com/webhook"

def enviar_respostas():
    mensagens_por_telefone = listar_mensagens()
    processadas = 0
    total_rejeitadas = 0

    for telefone, lista in mensagens_por_telefone.items():
        # Ordena por data (mais recente primeiro) se tiver campo "datahora"
        lista_ordenada = sorted(
            lista,
            key=lambda x: x.get("datahora", ""),
            reverse=True
        )[:10]  # Limita às 10 mais recentes

        for msg in lista_ordenada:
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
                        total_rejeitadas += 1
                except Exception as e:
                    logging.error(f"❌ Erro ao enviar requisição: {e}")
                    total_rejeitadas += 1

                time.sleep(2)  # ⏱️ Pausa entre cada envio
            else:
                total_rejeitadas += 1  # Já tem resposta ou mensagem vazia

    logging.info(f"📊 Total processadas: {processadas} | Ignoradas: {total_rejeitadas}")

if __name__ == "__main__":
    enviar_respostas()
