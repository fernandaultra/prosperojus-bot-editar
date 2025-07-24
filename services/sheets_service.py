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

# ✅ Lê as mensagens com resposta preenchida (para interface)
def listar_mensagens(limit=1000):
    spreadsheet_id = os.environ["PLANILHA_ID"]
    range_name = "Página1!A2:G"  # A:Telefone | B:Mensagem | C:Resposta | D:DataHora | E/F/G complementares

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

        if not telefone or not mensagem or not datahora or not resposta:
            continue

        if telefone not in historico:
            historico[telefone] = []

        historico[telefone].append({
            "linha": idx + 2,
            "mensagem": mensagem,
            "resposta": resposta,
            "datahora": datahora
        })

    # Ordena por data/hora decrescente e mantém apenas as 10 mais recentes por telefone
    for tel, mensagens in historico.items():
        mensagens.sort(key=lambda x: datetime.strptime(x["datahora"], "%Y-%m-%d %H:%M:%S"), reverse=True)
        historico[tel] = mensagens[:10]

    return historico

# ✅ Salva uma nova linha com a sugestão e dados derivados
def salvar_mensagem(data: dict):
    spreadsheet_id = os.environ["PLANILHA_ID"]
    range_name = "Página1!A:G"

    service = get_sheets_service()

    # Deriva colunas extras E/F/G a partir da data completa
    datahora_obj = datetime.strptime(data.get("timestamp"), "%Y-%m-%d %H:%M:%S")
    data_aaaa_mm_dd = datahora_obj.strftime("%Y/%m/%d")
    hora_hh_mm_ss = datahora_obj.strftime("%H:%M:%S")
    faixa_horaria = datahora_obj.strftime("%H:00:00")

    values = [[
        data.get("remetente", ""),
        data.get("mensagem", ""),
        data.get("resposta_sugerida", ""),
        data.get("timestamp", ""),
        data_aaaa_mm_dd,
        hora_hh_mm_ss,
        faixa_horaria
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
