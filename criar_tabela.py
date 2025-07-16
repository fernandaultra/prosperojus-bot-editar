import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

# Conecta usando as variáveis de ambiente do Render
conn = psycopg2.connect(
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT")
)

cur = conn.cursor()

# SQL para criar a tabela
cur.execute("""
    CREATE TABLE IF NOT EXISTS mensagens (
        id SERIAL PRIMARY KEY,
        telefone TEXT NOT NULL,
        mensagem TEXT NOT NULL,
        resposta TEXT NOT NULL,
        datahora TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
    );
""")

conn.commit()
cur.close()
conn.close()

print("✅ Tabela 'mensagens' criada com sucesso!")
