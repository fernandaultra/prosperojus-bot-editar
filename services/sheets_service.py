import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
import pandas as pd

# Inicializa conexão com Google Sheets
def get_sheets_service():
    creds_json = json.loads(os.environ["GOOGLE_SHEETS_CREDENTIALS_JSON"])
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = service_account.Credentials.from_service_account_info(creds_json, scopes=scopes)
    return build("sheets", "v4", credentials=creds)

# Lê as mensagens da planilha e retorna como lista de dicionários
def listar_mensagens(limit=100):
    spreadsheet_id = os.environ["PLANILHA_ID"]
    range_name = "Página1!A2:D"  # A:Telefone, B:Mensagem, C:Resposta, D:DataHora

    service = get_sheets_service()
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range=range_name
    ).execute()

    values = result.get("values", [])[:limit]

    mensagens = []
    for row in values:
        mensagens.append({
            "Telefone": row[0] if len(row) > 0 else "",
            "Mensagem": row[1] if len(row) > 1 else "",
            "Resposta": row[2] if len(row) > 2 else "",
            "DataHora": row[3] if len(row) > 3 else ""
        })

    return mensagens

# Atualiza a resposta e data/hora na planilha
def atualizar_resposta(linha, resposta, datahora):
    spreadsheet_id = os.environ["PLANILHA_ID"]
    range_name = f"Página1!C{linha}:D{linha}"  # Coluna C: Resposta | D: DataHora

    service = get_sheets_service()
    body = {
        "values": [[resposta, datahora]]
    }

    result = service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range=range_name,
        valueInputOption="RAW",
        body=body
    ).execute()

    print(f"✅ {result.get('updatedCells')} células atualizadas na linha {linha}.")

# Insere nova linha com mensagem recebida e resposta
def salvar_mensagem(telefone, mensagem, resposta, datahora):
    spreadsheet_id = os.environ["PLANILHA_ID"]
    range_name = "Página1!A:D"  # Inserção em todas as colunas

    service = get_sheets_service()
    body = {
        "values": [[telefone, mensagem, resposta, str(datahora)]]
    }

    result = service.spreadsheets().values().append(
        spreadsheetId=spreadsheet_id,
        range=range_name,
        valueInputOption="RAW",
        insertDataOption="INSERT_ROWS",
        body=body
    ).execute()

    print(f"✅ Mensagem salva na planilha. {result.get('updates', {}).get('updatedCells', 0)} células adicionadas.")
