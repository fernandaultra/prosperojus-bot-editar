import os
from openai import OpenAI
from dotenv import load_dotenv

# Carrega variáveis de ambiente do .env
load_dotenv()

# Cliente da OpenAI (usa a variável OPENAI_API_KEY automaticamente)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def carregar_contexto():
    caminho = "contexto.txt"
    if not os.path.exists(caminho):
        raise FileNotFoundError(f"Arquivo de contexto não encontrado: {caminho}")
    with open(caminho, "r", encoding="utf-8") as f:
        return f.read()

def gerar_resposta_com_gpt(mensagem_usuario):
    contexto_empresa = carregar_contexto()

    prompt_final = f"""{contexto_empresa}

🗨️ Mensagem recebida do cliente:
"{mensagem_usuario}"

✍️ Crie uma sugestão de resposta seguindo o contexto e se inspirando nos exemplos fornecidos:
"""

    try:
        resposta = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Você é um atendente da equipe comercial da ProsperoJus, especialista em negociação de precatórios."},
                {"role": "user", "content": prompt_final}
            ],
            temperature=0.7,
            max_tokens=700
        )
        return resposta.choices[0].message.content.strip()

    except Exception as e:
        print(f"Erro ao chamar OpenAI: {e}")
        return "⚠️ Tivemos um problema ao gerar a resposta. Pode tentar novamente em instantes?"