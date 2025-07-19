import os
import json
from datetime import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Inicializa conexão com Google Sheets
def get_sheets_service():
    creds_json = json.loads(os.environ["GOOGLE_SHEETS_CREDENTIALS_JSON"])
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = service_account.Credentials.from_service_account_info(creds_json, scopes=scopes)
    return build("sheets", "v4", credentials=creds)

# ✅ Lê e filtra mensagens não processadas, ordena por data e limita a 10 por telefone
def listar_mensagens(limit=1000):
    spreadsheet_id = os.environ["PLANILHA_ID"]
    range_name = "Página1!A2:G"  # A:Telefone | B:Mensagem | C:Resposta | D:DataHora | ... | G:Processado

    service = get_sheets_service()
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range=range_name
    ).execute()

    values = result.get("values", [])[:limit]
    historico = {}

    for idx, row in enumerate(values):
        telefone = row[0] if len(row) > 0 else ""
        mensagem = row[1] if len(row) > 1 else ""
        resposta = row[2] if len(row) > 2 else ""
        datahora = row[3] if len(row) > 3 else ""
        processado = row[6].strip().lower() == "ok" if len(row) > 6 else False

        if not telefone or not mensagem or not datahora or processado:
            continue  # pula se já estiver processado ou campos incompletos

        if telefone not in historico:
            historico[telefone] = []

        historico[telefone].append({
            "linha": idx + 2,
            "mensagem": mensagem,
            "resposta": resposta,
            "datahora": datahora,
            "processado": processado
        })

    # Ordena por data/hora decrescente e mantém apenas as 10 mais recentes por telefone
    for tel, mensagens in historico.items():
        mensagens.sort(key=lambda x: datetime.strptime(x["datahora"], "%Y-%m-%d %H:%M:%S"), reverse=True)
        historico[tel] = mensagens[:10]

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
        valueInputOption="USER_ENTERED",
        insertDataOption="INSERT_ROWS",
        body=body
    ).execute()

    print(f"✅ {result.get('updates', {}).get('updatedCells', 0)} células adicionadas com sucesso.")

# ✅ Marca como processado: preenche as colunas C:D:G na linha indicada
def marcar_como_processado(linha, resposta, datahora):
    spreadsheet_id = os.environ["PLANILHA_ID"]
    range_name = f"Página1!C{linha}:G{linha}"  # C:Resposta | D:DataHora | G:Processado

    service = get_sheets_service()
    body = {
        "values": [[resposta, datahora, "", "", "OK"]]
    }

    result = service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range=range_name,
        valueInputOption="USER_ENTERED",
        body=body
    ).execute()

    print(f"✅ Linha {linha} marcada como processada (coluna G).")
