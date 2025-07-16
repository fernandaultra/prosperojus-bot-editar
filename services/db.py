import psycopg2
import os
from dotenv import load_dotenv

# 📦 Carrega variáveis do .env localmente (útil para testes locais)
load_dotenv()

# 🔌 Conexão com o banco PostgreSQL
def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        port=os.getenv("DB_PORT", 5432)
    )

# 💾 Função para salvar mensagem no banco
def salvar_mensagem(telefone, mensagem, resposta, data_recebimento):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO mensagens (telefone, mensagem, resposta, data_recebimento)
        VALUES (%s, %s, %s, %s)
    """, (telefone, mensagem, resposta, data_recebimento))
    conn.commit()
    cursor.close()
    conn.close()

# 📤 Função para listar mensagens recentes
def listar_mensagens(limit=50):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT telefone, mensagem, data_recebimento
        FROM mensagens
        ORDER BY data_recebimento DESC
        LIMIT %s
    """, (limit,))
    resultados = cursor.fetchall()
    cursor.close()
    conn.close()
    return resultados
