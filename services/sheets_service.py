import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Inicializa conexão com Google Sheets
def get_sheets_service():
    creds_json = json.loads(os.environ["GOOGLE_SHEETS_CREDENTIALS_JSON"])
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = service_account.Credentials.from_service_account_info(creds_json, scopes=scopes)
    return build("sheets", "v4", credentials=creds)

# ✅ Lê as mensagens da planilha e retorna agrupadas por telefone
def listar_mensagens(limit=100):
    spreadsheet_id = os.environ["PLANILHA_ID"]
    range_name = "Página1!A2:D"  # A:Telefone | B:Mensagem | C:Resposta | D:DataHora

    service = get_sheets_service()
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range=range_name
    ).execute()

    values = result.get("values", [])[:limit]
    historico = {}

    for row in values:
        telefone = row[0] if len(row) > 0 else ""
        mensagem = row[1] if len(row) > 1 else ""
        resposta = row[2] if len(row) > 2 else ""
        datahora = row[3] if len(row) > 3 else ""

        if telefone:
            if telefone not in historico:
                historico[telefone] = []
            historico[telefone].append({
                "mensagem": mensagem,
                "resposta": resposta,
                "datahora": datahora
            })

    return historico

# ✅ Salva uma nova linha no Sheets a partir de dict
def salvar_mensagem(data: dict):
    spreadsheet_id = os.environ["PLANILHA_ID"]
    range_name = "Página1!A:D"

    service = get_sheets_service()
    values = [[
        data.get("remetente", ""),
        data.get("mensagem", ""),
        data.get("resposta_sugerida", ""),
        data.get("timestamp", "")
    ]]
    body = {"values": values}

    result = service.spreadsheets().values().append(
        spreadsheetId=spreadsheet_id,
        range=range_name,
        valueInputOption="USER_ENTERED",  # ✅ melhor para exibir corretamente no Sheets
        insertDataOption="INSERT_ROWS",
        body=body
    ).execute()

    print(f"✅ {result.get('updates', {}).get('updatedCells', 0)} células adicionadas com sucesso.")
