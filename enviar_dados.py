import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from services.db import listar_mensagens  # Importa função do seu db.py

# 🔐 Autenticação com Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credenciais.json", scope)
client = gspread.authorize(creds)

# 📄 Nome da planilha e da aba
nome_planilha = "dados_prosperojus"
nome_aba = "Página1"

# 📥 Pega dados do PostgreSQL usando o db.py
mensagens = listar_mensagens(limit=100)  # Pegue os últimos 100 registros

# 🔄 Converte para DataFrame
df = pd.DataFrame(mensagens, columns=["Telefone", "Mensagem", "Data Recebimento"])

# 🧽 Converte todos os valores para string (resolve erro de Timestamp)
df = df.astype(str)

# 🔗 Conecta ao Google Sheets
spreadsheet = client.open(nome_planilha)
worksheet = spreadsheet.worksheet(nome_aba)

# 🧹 Limpa conteúdo antigo e atualiza com novos dados
worksheet.clear()
worksheet.update([df.columns.values.tolist()] + df.values.tolist())

print("✅ Dados do banco enviados com sucesso para o Google Sheets!")
