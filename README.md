# 🤖 ProsperoJus Bot

Este é um chatbot automatizado com integração via WhatsApp (Z-API) para negociação de precatórios.

## 🚀 Funcionalidades
- Recebe mensagens via WhatsApp
- Responde automaticamente com base em scripts pré-definidos
- Hospedado na nuvem usando o [Render.com](https://render.com)

## 📁 Estrutura do Projeto

```
ProsperoJus/
├── app.py
├── requirements.txt
├── render.yaml
├── scripts/
│   └── respostas.json
├── services/
│   └── zapi_service.py
├── utils/
│   └── script_selector.py
```

## 🛠️ Como rodar localmente

1. Clone o repositório:
   ```
   git clone https://github.com/seu-usuario/prosperojus-bot.git
   cd prosperojus-bot
   ```

2. Crie o ambiente virtual:
   ```
   python -m venv .venv
   .\.venv\Scripts\activate
   ```

3. Instale as dependências:
   ```
   pip install -r requirements.txt
   ```

4. Rode a aplicação:
   ```
   python app.py
   ```

## ☁️ Deploy no Render

1. Faça login no [Render.com](https://render.com)
2. Crie um novo Web Service a partir deste repositório
3. Adicione as seguintes variáveis de ambiente no Render:
   - `ZAPI_TOKEN`
   - `ZAPI_INSTANCE_ID`
   - `ZAPI_URL`
4. O bot estará disponível em uma URL pública como:
   ```
   https://prosperojus-bot.onrender.com/webhook
   ```

## 🧠 Scripts de resposta

As mensagens e gatilhos ficam no arquivo `scripts/respostas.json`. Edite conforme sua estratégia de abordagem.

---

Feito com 💼 por ProsperoJus.
