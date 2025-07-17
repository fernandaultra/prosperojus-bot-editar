import schedule
import time
import os
import subprocess
import logging

# Configura logging para aparecer no painel do Render
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(message)s')

def rodar_script():
    logging.info("⏳ Executando script enviar_dados.py...")

    try:
        result = subprocess.run(["python", "enviar_dados.py"], capture_output=True, text=True)

        if result.returncode == 0:
            logging.info("✅ Script enviado com sucesso.")
            logging.info(result.stdout)
        else:
            logging.error("❌ Erro ao executar script:")
            logging.error(result.stderr)

    except Exception as e:
        logging.exception(f"Erro inesperado: {e}")

# 🔁 Roda a cada 1 minuto (modo de teste)
schedule.every(1).minutes.do(rodar_script)

logging.info("🚀 Agendador iniciado. Executando enviar_dados.py a cada 1 minuto...")

while True:
    schedule.run_pending()
    time.sleep(60)

