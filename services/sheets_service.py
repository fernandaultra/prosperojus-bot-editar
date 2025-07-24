import os
import json
from datetime import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build
import pandas as pd

# Inicializa conexão com Google Sheets
def get_sheets_service():
    creds_json = json.loads(os.environ["GOOGLE_SHEETS_CREDENTIALS_JSON"])
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = service_account.Credentials.from_service_account_info(creds_json, scopes=scopes)
    return build("sheets", "v4", credentials=creds)

# ✅ Lê todas as mensagens e retorna como DataFrame
def carregar_dados_em_dataframe():
    spreadsheet_id = os.environ["PLANILHA_ID"]
    range_name = "Página1!A2:G"

    service = get_sheets_service()
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range=range_name
    ).execute()

    values = result.get("values", [])
    colunas = ["Telefone", "Mensagem", "Resposta", "DataHora", "Data", "Hora", "Faixa"]
    df = pd.DataFrame(values, columns=colunas)

    if df.empty:
        return pd.DataFrame(columns=colunas + ["dif_minutos"])

    # 🔄 Converte a coluna DataHora para datetime
    df["DataHora"] = pd.to_datetime(df["DataHora"], format="%Y-%m-%d %H:%M:%S", errors="coerce")

    # 🔁 Ordena por telefone e horário
    df = df.sort_values(by=["Telefone", "DataHora"])

    # ⏱ Calcula diferença de tempo entre mensagens consecutivas por telefone
    df["dif_segundos"] = df.groupby("Telefone")["DataHora"].diff().dt.total_seconds()
    df["dif_minutos"] = (df["dif_segundos"] / 60).fillna(0).astype(int)

    return df

# ✅ Lê as mensagens com resposta preenchida (para interface)
def listar_mensagens(limit=1000):
    df = carregar_dados_em_dataframe()
    df = df[df["Resposta"] != ""]
    historico = {}

    for idx, row in df.head(limit).iterrows():
        telefone = row["Telefone"]
        if telefone not in historico:
            historico[telefone] = []

        historico[telefone].append({
            "linha": idx + 2,
            "mensagem": row["Mensagem"],
            "resposta": row["Resposta"],
            "datahora": row["DataHora"].strftime("%Y-%m-%d %H:%M:%S")
        })

    # Ordena e limita
    for tel in historico:
        historico[tel] = sorted(historico[tel], key=lambda x: x["datahora"], reverse=True)[:10]

    return historico

# ✅ Salva uma nova linha com sugestão e colunas derivadas + dif_minutos
def salvar_mensagem(data: dict):
    spreadsheet_id = os.environ["PLANILHA_ID"]
    range_name = "Página1!A:H"

    service = get_sheets_service()

    # Dados de data e hora
    datahora_obj = datetime.strptime(data.get("timestamp"), "%Y-%m-%d %H:%M:%S")
    data_aaaa_mm_dd = datahora_obj.strftime("%Y/%m/%d")
    hora_hh_mm_ss = datahora_obj.strftime("%H:%M:%S")
    faixa_horaria = datahora_obj.strftime("%H:00:00")

    # Carrega base atual para calcular diferença
    df = carregar_dados_em_dataframe()
    telefone = data.get("remetente", "")

    # Filtra mensagens anteriores do mesmo telefone
    df_tel = df[df["Telefone"] == telefone].copy()
    dif_minutos = 0

    if not df_tel.empty:
        ultima_datahora = df_tel["DataHora"].max()
        dif_seg = (datahora_obj - ultima_datahora).total_seconds()
        dif_minutos = int(dif_seg // 60)

    # Prepara linha para inserção
    values = [[
        telefone,
        data.get("mensagem", ""),
        data.get("resposta_sugerida", ""),
        data.get("timestamp", ""),
        data_aaaa_mm_dd,
        hora_hh_mm_ss,
        faixa_horaria,
        dif_minutos
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
