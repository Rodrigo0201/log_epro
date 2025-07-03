# Filtro de Arquivos ConsoleEDI_

## Alterações Realizadas

O sistema foi modificado para processar **apenas** arquivos que começam com o padrão `ConsoleEDI_` na pasta da rede `Servico Integra`.

**IMPORTANTE**: O processamento de arquivos ZIP foi **desabilitado**. O sistema agora processa apenas arquivos de log `ConsoleEDI_` diretamente.

**REPROCESSAMENTO INTELIGENTE**: O sistema detecta automaticamente quando um arquivo `ConsoleEDI_` foi modificado (novos dados adicionados) e o reprocessa automaticamente.

### Modificações Principais

#### 1. **core/zip_processor.py**
- **Método `find_zip_files()`**: Agora procura apenas arquivos ZIP que começam com `ConsoleEDI_` e terminam com `.Log.zip`
- **Método `extract_zip_files()`**: Verifica se os arquivos extraídos dos ZIPs também seguem o padrão `ConsoleEDI_`
- **Logs melhorados**: Mostra quais arquivos foram encontrados e quais foram ignorados

#### 2. **core/csv_processor.py**
- **Método `find_log_files()`**: Procura apenas arquivos de log que começam com `ConsoleEDI_` e terminam com `.Log`
- **Logs melhorados**: Indica claramente o padrão de busca e arquivos ignorados

#### 3. **core/processor.py**
- **Métodos de processamento**: Agora especificam claramente que processam apenas arquivos com padrão `ConsoleEDI_`
- **Mensagens informativas**: Mostra o padrão de busca e diretório sendo processado

#### 4. **core/csv_processor.py**
- **Controle de reprocessamento**: Detecta mudanças no tamanho/timestamp dos arquivos
- **Reprocessamento automático**: Reprocessa arquivos quando novos dados são adicionados
- **Banco de dados atualizado**: Armazena informações de tamanho e timestamp dos arquivos

#### 5. **config/settings.py**
- **Comentários explicativos**: Adicionados comentários para deixar claro o comportamento
- **Configuração `strict_pattern_matching`**: Nova configuração para forçar verificação rigorosa
- **Configuração `enable_reprocessing`**: Controla reprocessamento inteligente
- **Configuração `check_file_changes`**: Verifica mudanças nos arquivos

### Comportamento Atual

✅ **Arquivos PROCESSADOS:**
- `ConsoleEDI_20240701.Log`
- `ConsoleEDI_20240702.Log`

❌ **Arquivos IGNORADOS:**
- `ConsoleEDI_20240701.Log.zip` (ZIPs não são mais processados)
- `ConsoleEDI_20240702.Log.zip` (ZIPs não são mais processados)
- `OutroLog_20240701.Log`
- `OutroLog_20240701.Log.zip`
- `EDI_20240701.Log`
- `EDI_20240701.Log.zip`

### Como Usar

O sistema continua funcionando da mesma forma, mas agora processa apenas os arquivos desejados:

```bash
# Execução normal - processa apenas ConsoleEDI_* (com reprocessamento inteligente)
python3 cli/main.py

# Ver status
python3 cli/main.py --status

# Ver configurações
python3 cli/main.py --config

# Forçar reprocessamento de todos os arquivos
python3 cli/main.py --force-reprocess

# Reset completo (remove todos os dados)
python3 cli/main.py --reset
```

### Logs de Saída

Durante a execução, você verá mensagens como:

```
📦 PULANDO PROCESSAMENTO DE ARQUIVOS ZIP
ℹ️ Processando apenas arquivos de log 'ConsoleEDI_' diretamente...

🔍 Procurando arquivos de log com padrão 'ConsoleEDI_' em: /mnt/smb_integra
  ✓ Log encontrado: ConsoleEDI_20240701.Log
  ⚠️ Log ignorado (padrão diferente): OutroLog_20240701.Log

📄 Convertendo: ConsoleEDI_20240701.Log
  ✓ CSV gerado: ConsoleEDI_20240701.csv

⏭️ Pulando arquivo já processado: ConsoleEDI_20240701.Log

🔄 Arquivo modificado, reprocessando: ConsoleEDI_20240701.Log
   Tamanho anterior: 1024, atual: 2048
```

### Configuração

O padrão está definido em `config/settings.py`:

```python
PROCESSING_CONFIG = {
    'log_file_pattern': 'ConsoleEDI_',  # Apenas arquivos que começam com 'ConsoleEDI_'
    'log_file_extension': '.Log',
    'zip_file_extension': '.Log.zip',
    # ... outras configurações
}
```

Para alterar o padrão, modifique o valor de `log_file_pattern`. 