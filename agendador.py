import schedule
import time
import os
import subprocess
import logging

# Configura logging para aparecer no painel do Render
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(message)s')

SCRIPT = "enviar_dados.py"

def rodar_script():
    logging.info(f"⏳ Executando script {SCRIPT}...")

    try:
        result = subprocess.run(["python", SCRIPT], capture_output=True, text=True)

        if result.returncode == 0:
            logging.info("✅ Script executado com sucesso.")
            logging.info(result.stdout)
        else:
            logging.error("❌ Erro ao executar o script:")
            logging.error(result.stderr)

    except Exception as e:
        logging.exception(f"⚠️ Erro inesperado ao executar {SCRIPT}: {e}")

# 🔁 Roda a cada 1 minuto (modo de teste ou produção leve)
schedule.every(1).minutes.do(rodar_script)

logging.info("🚀 Agendador iniciado. Executando enviar_dados.py a cada 1 minuto...")

while True:
    schedule.run_pending()
    time.sleep(60)
