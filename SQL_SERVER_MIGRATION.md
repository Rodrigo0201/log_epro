# Migração para Microsoft SQL Server

## Mudanças Realizadas

### 1. Dependências
- **Antes**: `mysql-connector-python==8.2.0`
- **Depois**: `pyodbc==4.0.39`

### 2. Configurações de Banco de Dados
As configurações em `config/settings.py` foram atualizadas:

```python
DB_CONFIG = {
    'server': '192.168.2.25',           # Antes: 'host'
    'database': 'sistiju',
    'username': 'contrail',             # Antes: 'user'
    'password': 'contrail',
    'driver': 'ODBC Driver 17 for SQL Server',
    'trusted_connection': 'no'
}
```

### 3. Arquivo do Cliente de Banco
- **Antes**: `db/mysql_client.py`
- **Depois**: `db/sql_server_client.py`

### 4. Principais Alterações no Código

#### Conexão com Banco
- **MySQL**: `mysql.connector.connect(**DB_CONFIG)`
- **SQL Server**: `pyodbc.connect(conn_str)` com string de conexão ODBC

#### Tipos de Dados
- **MySQL**: `VARCHAR(255)`, `TEXT`
- **SQL Server**: `NVARCHAR(255)`, `NVARCHAR(MAX)`

#### Auto Increment
- **MySQL**: `INT AUTO_INCREMENT`
- **SQL Server**: `INT IDENTITY(1,1)`

#### Verificação de Duplicatas
- **MySQL**: `INSERT IGNORE`
- **SQL Server**: `IF NOT EXISTS ... INSERT`

## Instalação do Driver ODBC

### Ubuntu/Debian
```bash
# Instalar driver ODBC para SQL Server
curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
curl https://packages.microsoft.com/config/ubuntu/$(lsb_release -rs)/prod.list > /etc/apt/sources.list.d/mssql-release.list
apt-get update
ACCEPT_EULA=Y apt-get install -y msodbcsql17
apt-get install -y unixodbc-dev

# Instalar dependências Python
pip install -r requirements.txt
```

### Verificar Drivers Disponíveis
```bash
odbcinst -q -d
```

### Testar Conexão
```python
import pyodbc
conn_str = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=192.168.2.25;"
    "DATABASE=sistiju;"
    "UID=contrail;"
    "PWD=contrail;"
    "Trusted_Connection=no;"
)
conn = pyodbc.connect(conn_str)
print("Conexão bem-sucedida!")
```

## Compatibilidade

O código mantém a mesma interface de funções:
- `send_data_to_sql(csv_file)`
- `remove_duplicated_files()`

Todas as funcionalidades existentes foram preservadas, apenas adaptadas para SQL Server. 