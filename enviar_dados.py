import logging
from services.sheets_service import listar_mensagens, atualizar_resposta
from services.gpt_service import gerar_resposta_com_gpt
from datetime import datetime

# Configura logging (aproveita formato igual ao agendador)
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(message)s')

def enviar_respostas():
    mensagens = listar_mensagens()
    processadas = 0

    for idx, mensagem in enumerate(mensagens):
        numero = mensagem.get("Telefone")
        texto = mensagem.get("Mensagem")
        resposta = mensagem.get("Resposta")

        if texto and not resposta:
            logging.info(f"📨 Nova mensagem recebida de {numero}: {texto}")
            resposta_gerada = gerar_resposta_com_gpt(texto)
            logging.info(f"🤖 Resposta gerada: {resposta_gerada}")

            datahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            atualizar_resposta(idx + 2, resposta_gerada, datahora)
            processadas += 1

    logging.info(f"✅ Total de mensagens processadas: {processadas}")
    return processadas

if __name__ == "__main__":
    enviar_respostas()
