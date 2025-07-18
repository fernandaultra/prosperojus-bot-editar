import os
import json
from datetime import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build
from markdown import markdown
from markupsafe import Markup

# 🔐 Autentica e retorna o serviço do Google Sheets
def get_sheets_service():
    creds_json = json.loads(os.environ["GOOGLE_SHEETS_CREDENTIALS_JSON"])
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = service_account.Credentials.from_service_account_info(creds_json, scopes=scopes)
    return build("sheets", "v4", credentials=creds)

# 📥 Lista mensagens para uso no painel /mensagens
def listar_mensagens():
    spreadsheet_id = os.environ["PLANILHA_ID"]
    range_name = "Página1!A2:D"  # A: Telefone | B: Mensagem | C: Resposta | D: DataHora

    service = get_sheets_service()
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range=range_name
    ).execute()

    values = result.get("values", [])

    mensagens = {}
    for row in values:
        telefone = row[0] if len(row) > 0 else ""
        mensagem = row[1] if len(row) > 1 else ""
        resposta = row[2] if len(row) > 2 else ""
        datahora = row[3] if len(row) > 3 else ""

        if not telefone:
            continue

        if telefone not in mensagens:
            mensagens[telefone] = []

        mensagens[telefone].insert(0, {
            "mensagem": mensagem,
            "resposta": resposta,
            "html": Markup(markdown(resposta)),
            "datahora": datahora
        })

    return mensagens

# 🧾 Atualiza resposta e datahora (usado no agendador, se necessário)
def atualizar_resposta(linha, resposta, datahora):
    spreadsheet_id = os.environ["PLANILHA_ID"]
    range_name = f"Página1!C{linha}:D{linha}"

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

# 💾 Salva mensagem (adaptado para dict único)
def salvar_mensagem(dados):
    spreadsheet_id = os.environ["PLANILHA_ID"]
    range_name = "Página1!A:D"

    service = get_sheets_service()

    values = [[
        dados.get("remetente", ""),
        dados.get("mensagem", ""),
        dados.get("resposta_sugerida", ""),
        dados.get("timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    ]]

    body = {"values": values}

    result = service.spreadsheets().values().append(
        spreadsheetId=spreadsheet_id,
        range=range_name,
        valueInputOption="RAW",
        insertDataOption="INSERT_ROWS",
        body=body
    ).execute()

    print(f"✅ Mensagem salva com sucesso: {result.get('updates', {}).get('updatedCells', 0)} células adicionadas.")
