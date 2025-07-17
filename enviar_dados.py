import pandas as pd
import gspread
import os
import json
from oauth2client.service_account import ServiceAccountCredentials
from services.db import listar_mensagens  # Importa função do seu db.py

# 🔐 Autenticação com Google Sheets usando variável de ambiente
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# Lê o conteúdo JSON da variável de ambiente
creds_json = json.loads(os.environ["GOOGLE_SHEETS_CREDENTIALS_JSON"])
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_json, scope)
client = gspread.authorize(creds)

# 📄 Informações da planilha
planilha_id = os.environ["PLANILHA_ID"]
nome_aba = "Página1"

# 📥 Consulta ao banco de dados
mensagens = listar_mensagens(limit=100)

# 🔄 Converte para DataFrame
df = pd.DataFrame(mensagens, columns=["Telefone", "Mensagem", "Data Recebimento"])
df = df.astype(str)

# 🔗 Abre a planilha e aba
spreadsheet = client.open_by_key(planilha_id)
worksheet = spreadsheet.worksheet(nome_aba)

# 🧹 Limpa e atualiza
worksheet.clear()
worksheet.update([df.columns.values.tolist()] + df.values.tolist())

print("✅ Dados do banco enviados com sucesso para o Google Sheets!")
