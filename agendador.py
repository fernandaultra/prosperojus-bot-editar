import schedule
import time
import os

def rodar_script():
    os.system("python enviar_dados.py")

# Roda a cada 1 hora
schedule.every(1).minutes.do(rodar_script)

while True:
    schedule.run_pending()
    time.sleep(60)
