# Processador de Logs EDI

Sistema automatizado para processamento de logs EDI, com separação clara entre processamento de arquivos ZIP e CSV, além de recursos avançados de relatórios e monitoramento.

## 🚀 Funcionalidades

### Processamento Direto
- **Processamento de Logs**: Conversão direta de arquivos de log para CSV
- **Processamento de CSVs**: Filtragem e processamento de dados
- **Rastreamento Individual**: Controle separado de arquivos processados

### Filtro de Arquivos
- **Padrão ConsoleEDI_**: Processa apenas arquivos que começam com `ConsoleEDI_`
- **Sem ZIPs**: Processamento de arquivos ZIP foi desabilitado
- **Filtro Rigoroso**: Ignora automaticamente arquivos com outros padrões
- **Logs Detalhados**: Mostra quais arquivos foram processados e quais foram ignorados

### Conexão FTP
- **Acesso Remoto**: Conecta ao servidor FTP para baixar arquivos de log
- **Download Automático**: Baixa automaticamente arquivos com padrão ConsoleEDI_
- **Modo Passivo**: Suporte a firewalls corporativos
- **Segurança**: Autenticação por usuário e senha

### Relatórios e Estatísticas
- Relatórios diários e semanais em CSV
- Estatísticas detalhadas de processamento
- Histórico completo de sessões
- Monitoramento de performance

### Gestão Avançada
- Limpeza automática de arquivos temporários
- Controle de versões de arquivos processados
- Sistema de logs estruturado
- Configurações flexíveis

## 📁 Estrutura do Projeto

```
edi_epro/
├── cli/                    # Interface de linha de comando
│   ├── main.py            # CLI principal
│   └── remove_duplicates.py
├── config/                # Configurações
│   └── settings.py        # Configurações centralizadas
├── core/                  # Núcleo do sistema
│   ├── processor.py       # Processador principal (coordenador)
│   ├── zip_processor.py   # Processamento de arquivos ZIP
│   ├── csv_processor.py   # Processamento de arquivos CSV
│   ├── report_manager.py  # Gerenciador de relatórios
│   ├── csv_utils.py       # Utilitários CSV (legado)
│   └── smb_utils.py       # Utilitários SMB
├── db/                    # Camada de banco de dados
│   └── sql_server_client.py
├── processed_csvs/        # CSVs processados
├── reports/               # Relatórios gerados
├── temp_unzipped_logs/    # Arquivos temporários
└── requirements.txt
```

## 🛠️ Instalação

1. **Clone o repositório**:
```bash
git clone <repository-url>
cd edi_epro
```

2. **Crie um ambiente virtual**:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows
```

3. **Instale as dependências**:
```bash
pip install -r requirements.txt
```

4. **Configure as credenciais**:
Edite `config/settings.py` com suas credenciais de SMB e SQL Server.

## 📖 Uso

### Comandos Principais

```bash
# Processamento completo
python cli/main.py

# Ver status do sistema
python cli/main.py --status

# Ver configurações
python cli/main.py --config

# Ver estatísticas (últimos 30 dias)
python cli/main.py --stats

# Ver estatísticas (últimos 7 dias)
python cli/main.py --stats --stats-days 7

# Gerar relatório diário
python cli/main.py --report-daily

# Gerar relatório semanal
python cli/main.py --report-weekly

# Limpeza de arquivos
python cli/main.py --cleanup

# Reset completo do processamento
python cli/main.py --reset

# Limpar apenas duplicatas
python cli/main.py --clean-duplicates
```

### Fluxo de Processamento

1. **Montagem SMB**: Conecta ao compartilhamento de rede
2. **Processamento ZIP**: 
   - Encontra arquivos ZIP não processados
   - Extrai arquivos de log
   - Registra ZIPs processados
3. **Processamento CSV**:
   - Encontra arquivos de log (incluindo extraídos)
   - Converte para CSV
   - Aplica filtros
   - Registra logs processados
4. **Envio SQL Server**: Envia dados filtrados
5. **Limpeza**: Remove arquivos temporários
6. **Relatório**: Gera relatório diário

## ⚙️ Configurações

### Configurações Principais

```python
# config/settings.py

# Banco de Dados
DB_CONFIG = {
    'server': '192.168.2.15',
    'database': 'SISCNTRHC',
    'username': 'SISCNTRHC',
    'password': 'CtEp@2023',
    # ...
}

# Servidor FTP (substitui SMB)
FTP_CONFIG = {
    'host': '192.168.2.15',
    'port': 21,
    'username': 'rodrigo.cesarino',
    'password': 'R0drigo@147',
    'remote_dir': '/logs',
    'passive_mode': True,
    # ...
}
```

### Configurações de Processamento

```python
PROCESSING_CONFIG = {
    'log_file_pattern': 'ConsoleEDI_',
    'log_file_extension': '.Log',
    'zip_file_extension': '.Log.zip',
    'batch_size': 1000,
    'max_workers': 4,
    # ...
}
```

## 📊 Relatórios

### Relatório Diário
- Sessões do dia
- Arquivos processados por tipo
- Duração de cada sessão
- Erros encontrados

### Relatório Semanal
- Estatísticas agregadas por dia
- Total de arquivos processados
- Performance média

### Estatísticas em Tempo Real
```bash
python cli/main.py --stats --stats-days 7
```

## 🔧 Manutenção

### Limpeza Automática
```bash
python cli/main.py --cleanup
```

Remove:
- Arquivos CSV antigos (>7 dias)
- Relatórios antigos (>30 dias)
- Arquivos temporários
- Diretórios vazios

### Verificação de Status
```bash
python cli/main.py --status
```

Mostra:
- Arquivos processados (total)
- Última sessão
- Configurações ativas
- Status das conexões

## 🐛 Troubleshooting

### Problema: Erro "File exists" durante extração de ZIPs

**Sintomas:**
- Erro `[Errno 17] File exists: 'temp_unzipped_logs/ConsoleEDI_XXXXXX.Log'`
- Muitos arquivos ZIP encontrados mas erros na extração
- Inconsistência entre arquivos temporários e banco de dados

**Causa:**
Arquivos ZIP já foram extraídos anteriormente mas não foram marcados corretamente como processados no banco de dados.

**Solução:**
```bash
# Opção 1: Limpar apenas duplicatas (recomendado)
python cli/main.py --clean-duplicates

# Opção 2: Reset completo (remove todos os dados)
python cli/main.py --reset

# Opção 3: Usar script específico
python cli/remove_duplicates.py clean
```

### Problema: Conexão FTP falha

**Solução:**
```bash
# Verificar conectividade
ping 192.168.2.15

# Testar conexão FTP
python test_ftp_connection.py

# Verificar porta FTP
telnet 192.168.2.15 21
```

### Problema: Conexão SQL Server falha

**Solução:**
```bash
# Verificar driver ODBC
odbcinst -q -d

# Instalar driver se necessário
sudo apt-get install msodbcsql17 unixodbc-dev
```

### Verificar Status do Sistema

```bash
# Status geral
python cli/main.py --status

# Estatísticas detalhadas
python cli/main.py --stats

# Status específico
python cli/remove_duplicates.py status

# Testar conexão FTP
python test_ftp_connection.py
```

## 📈 Monitoramento

### Métricas Importantes
- **Taxa de sucesso**: Arquivos processados vs. erros
- **Performance**: Tempo médio de processamento
- **Volume**: Quantidade de arquivos por dia
- **Qualidade**: Registros válidos enviados ao SQL Server

### Alertas
- Monitorar erros consecutivos
- Verificar espaço em disco
- Acompanhar performance degradada

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 📞 Suporte

Para suporte técnico ou dúvidas, entre em contato com a equipe de desenvolvimento.# log_epro
