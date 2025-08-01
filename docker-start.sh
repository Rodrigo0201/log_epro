#!/bin/bash

# Script de inicialização do Processador de Logs EDI
# ================================================

set -e

echo "🚀 Iniciando Processador de Logs EDI com Docker..."

# Verificar se o arquivo .env existe
if [ ! -f .env ]; then
    echo "⚠️  Arquivo .env não encontrado. Criando arquivo .env com configurações padrão..."
    cat > .env << 'EOF'
# Configurações do Banco de Dados SQL Server
DB_SERVER=192.168.2.15
DB_DATABASE=SISCNTRHC
DB_USERNAME=SISCNTRHC
DB_PASSWORD=CtEp@2023

# Configurações do Compartilhamento SMB
SMB_HOST=192.168.2.15
SMB_SHARE="Servico Integra"
SMB_USERNAME=rodrigo.cesarino
SMB_PASSWORD=R0drigo@147

# Configurações do Container
TZ=America/Sao_Paulo
EOF
    echo "📝 Arquivo .env criado. Edite as configurações se necessário."
fi

# Verificar se os diretórios necessários existem
echo "📁 Criando diretórios necessários..."
mkdir -p logs processed_csvs reports temp_unzipped_logs /mnt/smb_integra
chmod 777 /mnt/smb_integra

# Verificar conectividade com o banco de dados
echo "🔍 Verificando conectividade com o banco de dados..."
source .env
if command -v nc &> /dev/null; then
    if nc -z $DB_SERVER 1433 2>/dev/null; then
        echo "✅ Conexão com banco de dados OK"
    else
        echo "⚠️  Não foi possível conectar ao banco de dados em $DB_SERVER:1433"
        echo "   Verifique se o servidor está acessível e as configurações estão corretas."
    fi
else
    echo "⚠️  Comando 'nc' não disponível. Pulando verificação de conectividade."
fi

# Construir e iniciar os containers
echo "🔨 Construindo containers..."
docker-compose build

echo "🚀 Iniciando serviços..."
docker-compose up -d

echo "📊 Status dos serviços:"
docker-compose ps

echo ""
echo "📋 Comandos úteis:"
echo "  docker-compose logs -f log-processor    # Ver logs do processador"
echo "  docker-compose logs -f smb-mounter      # Ver logs do montador SMB"
echo "  docker-compose exec log-processor python cli/main.py --status  # Ver status"
echo "  docker-compose exec log-processor python cli/main.py --config  # Ver configurações"
echo "  docker-compose down                     # Parar serviços"
echo "  docker-compose restart log-processor    # Reiniciar apenas o processador"
echo ""
echo "✅ Processador de Logs EDI iniciado com sucesso!" 