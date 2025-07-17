import os
import json
import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build
from services.db import listar_mensagens  # Importa função do seu db.py

# 🔐 Carrega as credenciais da variável de ambiente
creds_json = json.loads(os.environ["GOOGLE_SHEETS_CREDENTIALS_JSON"])
scopes = ["https://www.googleapis.com/auth/spreadsheets"]
creds = service_account.Credentials.from_service_account_info(creds_json, scopes=scopes)

# 📄 Informações da planilha
spreadsheet_id = os.environ["PLANILHA_ID"]
range_name = "Página1!A1"

# 📥 Consulta ao banco de dados
mensagens = listar_mensagens(limit=100)

# 🔄 Converte para DataFrame
df = pd.DataFrame(mensagens, columns=["Telefone", "Mensagem", "Data Recebimento"])
df = df.astype(str)

# 🔗 Inicializa o serviço do Google Sheets
service = build("sheets", "v4", credentials=creds)

# 🧹 Limpa conteúdo antigo e atualiza com novos dados
# 1. Limpa a aba
clear_body = {}
service.spreadsheets().values().clear(
    spreadsheetId=spreadsheet_id,
    range=range_name,
    body=clear_body
).execute()

# 2. Prepara e envia os novos dados
body = {
    "values": [df.columns.tolist()] + df.values.tolist()
}

result = service.spreadsheets().values().update(
    spreadsheetId=spreadsheet_id,
    range=range_name,
    valueInputOption="RAW",
    body=body
).execute()

print(f"✅ {result.get('updatedCells')} células atualizadas com sucesso no Google Sheets.")
