import logging
import time
import requests
from datetime import datetime
import pytz
from services.sheets_service import listar_mensagens, marcar_como_processado

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(message)s')

WEBHOOK_URL = "https://prosperojus-bot-editar.onrender.com/webhook"
brasilia = pytz.timezone("America/Sao_Paulo")

def enviar_respostas():
    mensagens_por_telefone = listar_mensagens()
    processadas = 0

    for telefone, lista in mensagens_por_telefone.items():
        # Ordena por data, mantém só as 10 últimas
        lista_ordenada = sorted(lista, key=lambda x: x.get("datahora", ""), reverse=True)[:10]

        for msg in lista_ordenada:
            # Só processa se ainda não foi marcado como OK e ainda não tem resposta
            if msg.get("mensagem") and not msg.get("resposta") and not msg.get("processado"):
                payload = {
                    "sender": telefone,
                    "message": msg["mensagem"]
                }

                logging.info(f"📨 Enviando mensagem para webhook: {payload}")

                try:
                    r = requests.post(WEBHOOK_URL, json=payload)
                    if r.status_code == 200:
                        logging.info(f"✅ Sucesso: {telefone}")
                        processadas += 1

                        # Marca como processado
                        datahora = datetime.now(brasilia).strftime("%Y-%m-%d %H:%M:%S")
                        marcar_como_processado(msg["linha"], "", datahora)

                    else:
                        logging.warning(f"⚠️ Erro {telefone}: {r.status_code} - {r.text}")

                except Exception as e:
                    logging.error(f"❌ Erro ao enviar: {e}")

                time.sleep(2)

    logging.info(f"📊 Total de mensagens processadas: {processadas}")

if __name__ == "__main__":
    enviar_respostas()
