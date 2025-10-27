# Migração de SMB para FTP - Processador de Logs EDI

## 📋 Resumo da Migração

Este documento descreve a migração do sistema de **SMB/CIFS** para **FTP** no processador de logs EDI.

## 🔄 O que Mudou

### **Antes (SMB)**
- Montagem de compartilhamento de rede via `mount -t cifs`
- Acesso direto aos arquivos via sistema de arquivos
- Requer privilégios de root para montagem
- Dependência de `cifs-utils` e comandos de sistema

### **Depois (FTP)**
- Conexão direta ao servidor FTP
- Download automático de arquivos para processamento local
- Não requer privilégios especiais
- Biblioteca padrão Python (`ftplib`)

## 🆕 Novos Arquivos

### **`core/ftp_utils.py`**
- Cliente FTP completo
- Gerenciamento de conexões
- Download de arquivos
- Listagem de diretórios

### **`test_ftp_connection.py`**
- Teste de conectividade FTP
- Validação de credenciais
- Teste de download
- Verificação de diretórios

## ⚙️ Configurações Atualizadas

### **`config/settings.py`**
```python
# NOVO - Configurações FTP
FTP_CONFIG = {
    'host': '192.168.2.15',
    'port': 21,
    'username': 'rodrigo.cesarino',
    'password': 'R0drigo@147',
    'remote_dir': '/logs',
    'timeout': 30,
    'passive_mode': True,
    'retry_attempts': 3,
    'local_download_dir': 'temp_unzipped_logs'
}

# LEGADO - Configurações SMB (pode ser removido)
SMB_CONFIG = {
    'host': '192.168.2.15',
    'share': 'Servico Integra',
    'username': 'rodrigo.cesarino',
    'password': 'R0drigo@147',
    'mount_point': '/mnt/smb_integra',
    'timeout': 30,
    'retry_attempts': 3
}
```

## 🐳 Docker Atualizado

### **Dockerfile**
- Removido `cifs-utils` e `mount`
- Não requer privilégios especiais
- Mais leve e seguro

### **docker-compose.yml**
- Variáveis de ambiente FTP
- Comando de inicialização simplificado
- Sem necessidade de montagem de volumes

## 🚀 Como Usar

### **1. Testar Conexão FTP**
```bash
python test_ftp_connection.py
```

### **2. Executar Processamento**
```bash
python cli/main.py
```

### **3. Docker**
```bash
docker-compose up --build
```

## ✅ Vantagens da Migração

1. **Segurança**: Não requer privilégios de root
2. **Portabilidade**: Funciona em qualquer ambiente Python
3. **Simplicidade**: Sem dependências de sistema
4. **Firewall**: Suporte a modo passivo
5. **Padrão**: Protocolo FTP amplamente suportado

## ⚠️ Considerações

1. **Credenciais**: Usuário e senha FTP devem estar configurados
2. **Diretório Remoto**: Verificar se o diretório `/logs` existe no servidor
3. **Permissões**: Usuário FTP deve ter acesso de leitura aos logs
4. **Rede**: Porta 21 deve estar acessível

## 🔧 Troubleshooting

### **Erro de Conexão**
```bash
# Verificar conectividade
ping 192.168.2.15

# Testar porta FTP
telnet 192.168.2.15 21

# Executar teste completo
python test_ftp_connection.py
```

### **Erro de Autenticação**
- Verificar usuário e senha em `config/settings.py`
- Confirmar se o usuário tem acesso ao diretório remoto
- Verificar se o servidor FTP está configurado corretamente

### **Erro de Download**
- Verificar espaço em disco local
- Confirmar permissões de escrita no diretório de download
- Verificar se os arquivos existem no servidor remoto

## 📚 Documentação Adicional

- [Python ftplib](https://docs.python.org/3/library/ftplib.html)
- [FTP Protocol](https://tools.ietf.org/html/rfc959)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)

## 🤝 Suporte

Para dúvidas sobre a migração, consulte:
1. Este documento
2. README.md atualizado
3. Arquivo de teste FTP
4. Logs do sistema
