import os
import traceback
from openai import OpenAI
from dotenv import load_dotenv

# Carrega variáveis do .env
load_dotenv()

# Recupera chave da API
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("❌ Variável de ambiente 'OPENAI_API_KEY' não definida.")

# Cliente da OpenAI
client = OpenAI(api_key=OPENAI_API_KEY)

def carregar_contexto():
    caminho = "contexto.txt"
    if not os.path.exists(caminho):
        raise FileNotFoundError(f"❌ Arquivo de contexto não encontrado: {caminho}")
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
        print("📡 Chamando a OpenAI...")
        resposta = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Temporário para testes; volte para "gpt-4" se necessário
            messages=[
                {"role": "system", "content": "Você é Amanda Mariano, advogada (OAB 18.020), especialista em negociação de precatórios pela ProsperoJus."},
                {"role": "user", "content": prompt_final}
            ],
            temperature=0.7,
            max_tokens=700
        )

        # Loga toda a resposta da OpenAI como JSON formatado
        print("📦 Resposta bruta da OpenAI:")
        print(resposta.model_dump_json(indent=2))

        conteudo = resposta.choices[0].message.content.strip()
        print("✅ Resposta da OpenAI (limpa):", conteudo)
        return conteudo if conteudo else None

    except Exception as e:
        print("❌ Erro ao chamar OpenAI:", str(e))
        traceback.print_exc()
        return None
