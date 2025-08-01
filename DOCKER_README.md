# Processador de Logs EDI - Docker

Este documento explica como executar o Processador de Logs EDI usando Docker.

## 📋 Pré-requisitos

- Docker
- Docker Compose
- Acesso à rede onde está o servidor SQL Server (192.168.2.15)
- Acesso ao compartilhamento SMB (192.168.2.15/Servico Integra)

## 🚀 Início Rápido

### 1. Configuração Inicial

```bash
# Copiar arquivo de configuração
cp docker.env.example .env

# Editar configurações (se necessário)
nano .env
```

### 2. Iniciar com Script Automático

```bash
# Executar script de inicialização
./docker-start.sh
```

### 3. Iniciar Manualmente

```bash
# Construir e iniciar
docker-compose up -d

# Ver logs
docker-compose logs -f log-processor
```

## 🔧 Configurações

### Variáveis de Ambiente (.env)

```bash
# Banco de Dados SQL Server
DB_SERVER=192.168.2.15
DB_DATABASE=SISCNTRHC
DB_USERNAME=SISCNTRHC
DB_PASSWORD=CtEp@2023

# Compartilhamento SMB
SMB_HOST=192.168.2.15
SMB_SHARE=Servico Integra
SMB_USERNAME=rodrigo.cesarino
SMB_PASSWORD=R0drigo@147

# Configurações do Container
TZ=America/Sao_Paulo
```

## 📁 Estrutura de Volumes

```
./logs/                    # Logs da aplicação
./processed_csvs/          # CSVs processados
./reports/                 # Relatórios gerados
./temp_unzipped_logs/      # Arquivos temporários
./processed_files.db       # Banco SQLite local
/mnt/smb_integra          # Compartilhamento SMB (dentro do container)
```

## 🛠️ Comandos Úteis

### Gerenciamento de Containers

```bash
# Ver status dos serviços
docker-compose ps

# Ver logs em tempo real
docker-compose logs -f log-processor
docker-compose logs -f smb-mounter

# Parar serviços
docker-compose down

# Reiniciar apenas o processador
docker-compose restart log-processor

# Reconstruir containers
docker-compose build --no-cache
```

### Executar Comandos no Container

```bash
# Ver status do processamento
docker-compose exec log-processor python cli/main.py --status

# Ver configurações
docker-compose exec log-processor python cli/main.py --config

# Ver estatísticas
docker-compose exec log-processor python cli/main.py --stats

# Gerar relatório diário
docker-compose exec log-processor python cli/main.py --report-daily

# Limpeza de arquivos temporários
docker-compose exec log-processor python cli/main.py --cleanup

# Reset completo
docker-compose exec log-processor python cli/main.py --reset
```

## 🔍 Solução de Problemas

### Problema: Compartilhamento SMB não monta

```bash
# Verificar se o serviço SMB está rodando
docker-compose logs smb-mounter

# Testar conectividade manualmente
docker-compose exec log-processor ping 192.168.2.15

# Verificar credenciais no arquivo .env
cat .env
```

### Problema: Não consegue conectar ao banco

```bash
# Verificar conectividade
docker-compose exec log-processor nc -zv 192.168.2.15 1433

# Verificar logs do processador
docker-compose logs log-processor | grep -i "database\|connection"
```

### Problema: Permissões de arquivo

```bash
# Ajustar permissões dos diretórios
sudo chown -R $USER:$USER logs processed_csvs reports temp_unzipped_logs
chmod -R 755 logs processed_csvs reports temp_unzipped_logs
```

## 📊 Monitoramento

### Verificar Uso de Recursos

```bash
# Uso de CPU e memória
docker stats log-processor

# Espaço em disco
docker system df
```

### Logs Detalhados

```bash
# Logs do processador
docker-compose logs log-processor

# Logs do montador SMB
docker-compose logs smb-mounter

# Logs de todos os serviços
docker-compose logs
```

## 🔄 Atualizações

### Atualizar Código

```bash
# Parar serviços
docker-compose down

# Reconstruir com novo código
docker-compose build --no-cache

# Reiniciar
docker-compose up -d
```

### Atualizar Configurações

```bash
# Editar .env
nano .env

# Reiniciar serviços
docker-compose restart
```

## 🚨 Segurança

- **Nunca** commite o arquivo `.env` no Git
- Use credenciais fortes para o banco de dados
- Considere usar secrets do Docker para senhas
- Mantenha o Docker e as imagens atualizados

## 📞 Suporte

Para problemas específicos do Docker:

1. Verifique os logs: `docker-compose logs`
2. Teste conectividade: `docker-compose exec log-processor ping 192.168.2.15`
3. Verifique configurações: `docker-compose exec log-processor python cli/main.py --config`
4. Consulte a documentação principal do projeto 