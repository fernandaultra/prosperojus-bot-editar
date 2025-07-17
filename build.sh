#!/usr/bin/env bash
# build.sh

echo "🔧 Iniciando instalação das dependências..."

# Garante que falhas sejam detectadas e exibidas
set -e

echo "🚀 Atualizando o pip..."
pip install --upgrade pip

echo "📦 Instalando pacotes do requirements.txt..."
pip install -r requirements.txt

echo "✅ Ambiente configurado com sucesso!"
