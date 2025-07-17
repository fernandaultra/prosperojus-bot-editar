from services.sheets_service import listar_mensagens, atualizar_resposta
from services.gpt_service import gerar_resposta_com_gpt
from datetime import datetime
import time

def enviar_respostas():
    mensagens = listar_mensagens()

    for idx, mensagem in enumerate(mensagens):
        numero = mensagem.get("Telefone")
        texto = mensagem.get("Mensagem")
        resposta = mensagem.get("Resposta")

        if texto and not resposta:
            print(f"📨 Nova mensagem recebida de {numero}: {texto}")
            resposta_gerada = gerar_resposta_com_gpt(texto)
            print(f"🤖 Resposta gerada: {resposta_gerada}")

            datahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            atualizar_resposta(idx + 2, resposta_gerada, datahora)  # +2 pois a planilha geralmente tem cabeçalho

if __name__ == "__main__":
    while True:
        enviar_respostas()
        print("⏳ Aguardando 60 segundos...")
        time.sleep(60)
