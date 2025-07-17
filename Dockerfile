# Imagem base com Python 3.10
FROM python:3.10-slim

# Define diretório de trabalho
WORKDIR /app

# Copia os arquivos do projeto para dentro do container
COPY . .

# Instala dependências
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Comando para iniciar o worker
CMD ["python", "agendador.py"]
