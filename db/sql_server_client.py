import csv
import sqlite3
from datetime import datetime
import os
try:
    import pyodbc
    PYODBC_AVAILABLE = True
except ImportError:
    print("⚠️ pyodbc não disponível - modo de processamento local apenas")
    PYODBC_AVAILABLE = False
from config.settings import DB_CONFIG, LOCAL_CONFIG

def send_data_to_sql(csv_file):
    """Envia dados CSV para banco de dados SQL Server ou SQLite local."""
    if not PYODBC_AVAILABLE:
        print(f"  ⚠️ pyodbc não disponível - salvando dados localmente em SQLite: {os.path.basename(csv_file)}")
        return send_data_to_sqlite(csv_file)
        
    try:
        # Construir string de conexão para SQL Server
        conn_str = (
            f"DRIVER={{{DB_CONFIG['driver']}}};"
            f"SERVER={DB_CONFIG['server']};"
            f"DATABASE={DB_CONFIG['database']};"
            f"UID={DB_CONFIG['username']};"
            f"PWD={DB_CONFIG['password']};"
            f"Trusted_Connection={DB_CONFIG['trusted_connection']};"
        )
        
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        
        # Verifica se a tabela existe
        check_table_query = f"""
        SELECT COUNT(*)
        FROM INFORMATION_SCHEMA.TABLES
        WHERE TABLE_SCHEMA = 'dbo' AND TABLE_NAME = '{LOCAL_CONFIG['table_name']}';
        """
        cursor.execute(check_table_query)
        table_exists = cursor.fetchone()[0]
        
        # Cria a tabela se ela não existir
        if table_exists == 0:
            create_table_query = f"""
            CREATE TABLE {LOCAL_CONFIG['table_name']} (
                id INT IDENTITY(1,1) PRIMARY KEY,
                data DATETIME2,
                formato_processo NVARCHAR(255),
                nome_arquivo NVARCHAR(MAX)
            );
            
            CREATE UNIQUE INDEX idx_unique_log
            ON {LOCAL_CONFIG['table_name']} (data, formato_processo, nome_arquivo);
            """
            cursor.execute(create_table_query)
            print(f"  ✓ Tabela {LOCAL_CONFIG['table_name']} criada no banco de dados.")
        
        # Inserção de dados no banco
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader)  # Pular o cabeçalho
            insert_query = f"""
            IF NOT EXISTS (
                SELECT 1 FROM {LOCAL_CONFIG['table_name']} 
                WHERE data = ? AND formato_processo = ? AND nome_arquivo = ?
            )
            INSERT INTO {LOCAL_CONFIG['table_name']} (data, formato_processo, nome_arquivo) 
            VALUES (?, ?, ?)
            """
            inserted_count = 0
            for row in reader:
                try:
                    # Converter data para formato SQL Server
                    converted_date = datetime.strptime(row[0], '%d/%m/%Y %H:%M:%S').strftime('%Y-%m-%d %H:%M:%S')
                    cursor.execute(insert_query, (converted_date, row[1], row[2], converted_date, row[1], row[2]))
                    if cursor.rowcount > 0:
                        inserted_count += 1
                except ValueError as e:
                    print(f"    ⚠ Erro ao converter data: {row[0]} - {e}")
                    continue
        
        conn.commit()
        cursor.close()
        conn.close()
        print(f"  ✓ {inserted_count} registros inseridos no banco de dados.")
        return True
    except Exception as e:
        print(f"  ✗ Erro ao enviar dados para banco: {e}")
        return False

def remove_duplicated_files():
    """Remove registros duplicados na tabela edi_logs, mantendo apenas o menor id para cada combinação única."""
    if not PYODBC_AVAILABLE:
        print("  ⚠️ pyodbc não disponível - remoção de duplicatas no SQLite local")
        return remove_duplicated_files_sqlite()
        
    try:
        print("  🔄 Conectando ao SQL Server para remoção de duplicatas...")
        # Construir string de conexão para SQL Server
        conn_str = (
            f"DRIVER={{{DB_CONFIG['driver']}}};"
            f"SERVER={DB_CONFIG['server']};"
            f"DATABASE={DB_CONFIG['database']};"
            f"UID={DB_CONFIG['username']};"
            f"PWD={DB_CONFIG['password']};"
            f"Trusted_Connection={DB_CONFIG['trusted_connection']};"
        )
        
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        
        # Contar registros antes da remoção
        cursor.execute(f"SELECT COUNT(*) FROM {LOCAL_CONFIG['table_name']}")
        records_before = cursor.fetchone()[0]
        
        print(f"  📊 Registros antes da limpeza: {records_before}")
        
        # Query otimizada para remover duplicatas
        delete_query = f'''
        WITH DuplicatesToRemove AS (
            SELECT id,
                   ROW_NUMBER() OVER (
                       PARTITION BY data, formato_processo, nome_arquivo 
                       ORDER BY id
                   ) as rn
            FROM {LOCAL_CONFIG['table_name']}
        )
        DELETE FROM {LOCAL_CONFIG['table_name']}
        WHERE id IN (
            SELECT id 
            FROM DuplicatesToRemove 
            WHERE rn > 1
        );
        '''
        
        cursor.execute(delete_query)
        deleted_count = cursor.rowcount
        conn.commit()
        
        # Contar registros após a remoção
        cursor.execute(f"SELECT COUNT(*) FROM {LOCAL_CONFIG['table_name']}")
        records_after = cursor.fetchone()[0]
        
        print(f"  ✓ {deleted_count} duplicatas removidas da tabela {LOCAL_CONFIG['table_name']}.")
        print(f"    Registros após limpeza: {records_after}")
        
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"  ✗ Erro ao remover duplicatas: {e}")
        return False

def send_data_to_sqlite(csv_file):
    """Salva dados CSV em banco SQLite local."""
    try:
        # Conectar ao banco SQLite local
        conn = sqlite3.connect(LOCAL_CONFIG['local_db'])
        cursor = conn.cursor()
        
        # Criar tabela se não existir
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS edi_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data TEXT,
                formato_processo TEXT,
                nome_arquivo TEXT,
                UNIQUE(data, formato_processo, nome_arquivo)
            )
        """)
        
        # Inserir dados do CSV
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader)  # Pular cabeçalho
            
            inserted_count = 0
            for row in reader:
                try:
                    cursor.execute("""
                        INSERT OR IGNORE INTO edi_logs (data, formato_processo, nome_arquivo) 
                        VALUES (?, ?, ?)
                    """, (row[0], row[1], row[2]))
                    if cursor.rowcount > 0:
                        inserted_count += 1
                except Exception as e:
                    print(f"    ⚠ Erro ao inserir linha: {row} - {e}")
                    continue
        
        conn.commit()
        conn.close()
        
        print(f"  ✓ {inserted_count} registros salvos no banco SQLite local.")
        return True
        
    except Exception as e:
        print(f"  ✗ Erro ao salvar dados no SQLite: {e}")
        return False

def remove_duplicated_files_sqlite():
    """Remove registros duplicados na tabela edi_logs do SQLite local."""
    try:
        # Conectar ao banco SQLite local
        conn = sqlite3.connect(LOCAL_CONFIG['local_db'])
        cursor = conn.cursor()
        
        # Contar registros antes da remoção
        cursor.execute("SELECT COUNT(*) FROM edi_logs")
        records_before = cursor.fetchone()[0]
        
        # Remover duplicatas mantendo apenas o menor id para cada combinação única
        delete_query = '''
        DELETE FROM edi_logs 
        WHERE id NOT IN (
            SELECT MIN(id)
            FROM edi_logs
            GROUP BY data, formato_processo, nome_arquivo
        );
        '''
        cursor.execute(delete_query)
        deleted_count = cursor.rowcount
        conn.commit()
        
        # Contar registros após a remoção
        cursor.execute("SELECT COUNT(*) FROM edi_logs")
        records_after = cursor.fetchone()[0]
        
        print(f"  ✓ {deleted_count} duplicatas removidas da tabela SQLite local.")
        print(f"    Registros antes: {records_before} | Registros após: {records_after}")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"  ✗ Erro ao remover duplicatas no SQLite: {e}")
        return False
