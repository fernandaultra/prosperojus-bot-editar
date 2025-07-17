from services.db import listar_mensagens

mensagens = listar_mensagens(limit=1000)

for telefone, mensagem, data in mensagens:
    print(f"[{data}] {telefone}: {mensagem}")
