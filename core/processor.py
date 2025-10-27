#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Processador Principal de Logs EDI
=================================
Coordena o processamento de arquivos ZIP e CSV de forma separada.
"""

import os
import sqlite3
from datetime import datetime
from typing import List, Dict, Any
from config.settings import LOCAL_CONFIG, SMB_CONFIG, PROCESSING_CONFIG, FTP_CONFIG
from core.zip_processor import ZipProcessor
from core.csv_processor import CsvProcessor
from core.ftp_utils import connect_ftp, disconnect_ftp
from db.sql_server_client import send_data_to_sql, remove_duplicated_files

class LogProcessor:
    """Classe principal para coordenação do processamento de logs EDI."""
    
    def __init__(self):
        self.zip_processor = ZipProcessor()
        self.csv_processor = CsvProcessor()
        self.start_time = None
        self.ftp_client = None
        self.sql_success_count = 0
        self.sql_error_count = 0

    def init_databases(self):
        """Inicializa todos os bancos de dados necessários."""
        print("🔧 Inicializando bancos de dados...")
        
        # Criar diretórios necessários
        os.makedirs(LOCAL_CONFIG['temp_dir'], exist_ok=True)
        os.makedirs(LOCAL_CONFIG['output_dir'], exist_ok=True)
        
        # Inicializar banco principal
        try:
            conn = sqlite3.connect(LOCAL_CONFIG['local_db'])
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS processing_sessions (
                    session_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    start_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                    end_time DATETIME,
                    zip_files_processed INTEGER DEFAULT 0,
                    log_files_processed INTEGER DEFAULT 0,
                    csv_files_generated INTEGER DEFAULT 0,
                    sql_records_inserted INTEGER DEFAULT 0,
                    errors_count INTEGER DEFAULT 0
                );
            """)
            conn.commit()
            conn.close()
            print("✓ Banco de dados principal inicializado.")
        except Exception as e:
            print(f"✗ Erro ao inicializar banco principal: {e}")
            return False
        
        # Inicializar bancos específicos
        if not self.zip_processor.init_zip_database():
            return False
        if not self.csv_processor.init_csv_database():
            return False
            
        return True

    def process_zip_files(self) -> List[str]:
        """Processa arquivos ZIP com padrão ConsoleEDI_ e retorna lista de arquivos extraídos."""
        print("\n📦 PROCESSAMENTO DE ARQUIVOS ZIP")
        print("=" * 50)
        print(f"🎯 Padrão de busca: '{PROCESSING_CONFIG['log_file_pattern']}'")
        print(f"📁 Servidor FTP: {FTP_CONFIG['host']}:{FTP_CONFIG['port']}")
        
        if not self.ftp_client:
            print("✗ Cliente FTP não está conectado")
            return []
        
        # Encontrar arquivos ZIP via FTP
        zip_files = self.ftp_client.list_files(PROCESSING_CONFIG['log_file_pattern'] + '*.zip')
        
        if not zip_files:
            print("ℹ Nenhum arquivo ZIP com padrão 'ConsoleEDI_' encontrado.")
            return []
        
        print(f"\n📊 Encontrados {len(zip_files)} arquivos ZIP com padrão 'ConsoleEDI_' para processar.")
        
        # Extrair arquivos ZIP
        extracted_files = self.zip_processor.extract_zip_files(zip_files)
        
        print(f"\n✅ Processamento de ZIPs concluído:")
        zip_summary = self.zip_processor.get_summary()
        print(f"   - ZIPs processados: {zip_summary['zips_processed']}")
        print(f"   - Arquivos extraídos: {zip_summary['files_extracted']}")
        print(f"   - Erros: {zip_summary['errors']}")
        
        return extracted_files

    def process_csv_files(self, log_files: List[str]) -> List[str]:
        """Processa arquivos de log com padrão ConsoleEDI_ e gera CSVs filtrados."""
        print("\n📄 PROCESSAMENTO DE ARQUIVOS CSV")
        print("=" * 50)
        print(f"🎯 Padrão de busca: '{PROCESSING_CONFIG['log_file_pattern']}'")
        
        if not log_files:
            print("ℹ Nenhum arquivo de log com padrão 'ConsoleEDI_' para processar.")
            return []
        
        print(f"\n📊 Processando {len(log_files)} arquivos de log com padrão 'ConsoleEDI_'...")
        
        # Converter logs para CSV
        csv_files = self.csv_processor.convert_logs_to_csv(log_files)
        
        if not csv_files:
            print("ℹ Nenhum CSV foi gerado.")
            return []
        
        print(f"\n📊 Aplicando filtros em {len(csv_files)} arquivos CSV...")
        
        # Aplicar filtros nos CSVs
        filtered_files = self.csv_processor.filter_csv_files(csv_files)
        
        print(f"\n✅ Processamento de CSVs concluído:")
        csv_summary = self.csv_processor.get_summary()
        print(f"   - Logs processados: {csv_summary['logs_processed']}")
        print(f"   - CSVs gerados: {csv_summary['csvs_generated']}")
        print(f"   - CSVs filtrados: {csv_summary['csvs_filtered']}")
        print(f"   - Erros: {csv_summary['errors']}")
        
        return filtered_files

    def send_to_sql_server(self, csv_files: List[str]):
        """Envia dados dos CSVs para o SQL Server."""
        print("\n🗄️ ENVIANDO DADOS PARA SQL SERVER")
        print("=" * 50)
        
        if not csv_files:
            print("ℹ Nenhum arquivo CSV para enviar ao SQL Server.")
            return
        
        print(f"\n📊 Enviando {len(csv_files)} arquivos CSV para o SQL Server...")
        
        for i, csv_file in enumerate(csv_files, 1):
            print(f"\n[{i}/{len(csv_files)}] Enviando: {os.path.basename(csv_file)}")
            
            if send_data_to_sql(csv_file):
                self.sql_success_count += 1
                print(f"  ✅ Enviado com sucesso")
            else:
                self.sql_error_count += 1
                print(f"  ❌ Erro no envio")

    def run_processing(self):
        """Executa o processamento completo."""
        self.start_time = datetime.now()
        print(f"\n🚀 INICIANDO PROCESSAMENTO EDI")
        print(f"⏰ Início: {self.start_time.strftime('%d/%m/%Y %H:%M:%S')}")
        print("=" * 60)
        
        # Conectar ao servidor FTP
        self.ftp_client = connect_ftp()
        if not self.ftp_client:
            print("✗ Não foi possível conectar ao servidor FTP. Abortando.")
            return False
        
        try:
            # Inicializar bancos de dados
            if not self.init_databases():
                return False
            
            # PULAR processamento de arquivos ZIP - processar apenas arquivos de log diretamente
            print("\n📦 PULANDO PROCESSAMENTO DE ARQUIVOS ZIP")
            print("ℹ️ Processando apenas arquivos de log 'ConsoleEDI_' diretamente...")
            extracted_files = []
            
            # Encontrar e baixar arquivos de log com padrão ConsoleEDI_ via FTP
            print("\n📄 PROCESSANDO ARQUIVOS DE LOG COM PADRÃO 'ConsoleEDI_' VIA FTP")
            print("ℹ️ Baixando logs que começam com 'ConsoleEDI_'...")
            
            # Baixar arquivos via FTP
            downloaded_files = self.ftp_client.download_files(
                PROCESSING_CONFIG['log_file_pattern'],
                FTP_CONFIG['local_download_dir']
            )
            
            if not downloaded_files:
                print("ℹ️ Nenhum arquivo foi baixado via FTP")
                return False
            
            # Usar arquivos baixados para processamento
            all_log_files = downloaded_files
            
            # Processar arquivos CSV
            filtered_csv_files = self.process_csv_files(all_log_files)
            
            # Enviar para SQL Server (com controle de duplicatas)
            print("\n🗄️ ENVIANDO DADOS PARA SQL SERVER")
            print("ℹ️ Garantindo registros únicos...")
            self.send_to_sql_server(filtered_csv_files)
            
            # Remover duplicatas (garantir unicidade)
            print("\n🧹 Garantindo unicidade dos registros...")
            remove_duplicated_files()
            
            # Limpeza (apenas CSVs, sem arquivos temporários de ZIP)
            print("\n🧹 Realizando limpeza...")
            self.csv_processor.cleanup_old_csvs()
            
            # Salvar sessão
            self._save_processing_session()
            
            # Exibir resumo
            self.print_summary()
            
            return True
            
        except Exception as e:
            print(f"\n❌ Erro durante o processamento: {e}")
            return False
        finally:
            if self.ftp_client:
                disconnect_ftp(self.ftp_client)

    def _save_processing_session(self):
        """Salva informações da sessão de processamento."""
        try:
            end_time = datetime.now()
            zip_summary = self.zip_processor.get_summary()
            csv_summary = self.csv_processor.get_summary()
            
            conn = sqlite3.connect(LOCAL_CONFIG['local_db'])
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO processing_sessions 
                (start_time, end_time, zip_files_processed, log_files_processed, 
                 csv_files_generated, sql_records_inserted, errors_count)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                self.start_time,
                end_time,
                zip_summary['zips_processed'],
                csv_summary['logs_processed'],
                csv_summary['csvs_filtered'],
                self.sql_success_count,
                zip_summary['errors'] + csv_summary['errors'] + self.sql_error_count
            ))
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"✗ Erro ao salvar sessão: {e}")

    def print_summary(self):
        """Exibe resumo detalhado do processamento."""
        end_time = datetime.now()
        duration = end_time - self.start_time if self.start_time else None
        
        zip_summary = self.zip_processor.get_summary()
        csv_summary = self.csv_processor.get_summary()
        
        print("\n" + "=" * 60)
        print("📋 RESUMO DETALHADO DO PROCESSAMENTO")
        print("=" * 60)
        print(f"⏰ Início: {self.start_time.strftime('%d/%m/%Y %H:%M:%S')}")
        print(f"⏰ Fim: {end_time.strftime('%d/%m/%Y %H:%M:%S')}")
        if duration:
            print(f"⏱️ Duração: {duration}")
        
        print("\n📦 PROCESSAMENTO DE ZIPs:")
        print(f"   - ZIPs processados: 0 (processamento de ZIPs desabilitado)")
        print(f"   - Arquivos extraídos: 0 (processamento direto de logs)")
        print(f"   - Erros: 0")
        
        print("\n📄 PROCESSAMENTO DE CSVs:")
        print(f"   - Logs processados: {csv_summary['logs_processed']}")
        print(f"   - CSVs gerados: {csv_summary['csvs_generated']}")
        print(f"   - CSVs filtrados: {csv_summary['csvs_filtered']}")
        print(f"   - Erros: {csv_summary['errors']}")
        
        print("\n🗄️ ENVIO PARA SQL SERVER:")
        print(f"   - Arquivos enviados com sucesso: {self.sql_success_count}")
        print(f"   - Arquivos com erro: {self.sql_error_count}")
        
        total_errors = zip_summary['errors'] + csv_summary['errors'] + self.sql_error_count
        print(f"\n❌ TOTAL DE ERROS: {total_errors}")
        
        if zip_summary['error_details'] or csv_summary['error_details']:
            print("\n🔍 DETALHES DOS ERROS:")
            for error in zip_summary['error_details']:
                print(f"   - ZIP: {error}")
            for error in csv_summary['error_details']:
                print(f"   - CSV: {error}")
        
        print("=" * 60)

    def show_status(self):
        """Exibe status detalhado do sistema."""
        print("\n📊 STATUS DETALHADO DO SISTEMA")
        print("=" * 50)
        
        # Status do banco local
        try:
            conn = sqlite3.connect(LOCAL_CONFIG['local_db'])
            cursor = conn.cursor()
            
            # Contar ZIPs processados
            cursor.execute("SELECT COUNT(*) FROM processed_zips")
            zips_processed = cursor.fetchone()[0]
            
            # Contar logs processados
            cursor.execute("SELECT COUNT(*) FROM processed_logs")
            logs_processed = cursor.fetchone()[0]
            
            # Última sessão
            cursor.execute("""
                SELECT start_time, end_time, zip_files_processed, log_files_processed, 
                       csv_files_generated, sql_records_inserted, errors_count
                FROM processing_sessions 
                ORDER BY session_id DESC LIMIT 1
            """)
            last_session = cursor.fetchone()
            
            conn.close()
            
            print(f"📦 ZIPs processados (total): {zips_processed}")
            print(f"📄 Logs processados (total): {logs_processed}")
            
            if last_session:
                print(f"\n🕐 ÚLTIMA SESSÃO:")
                print(f"   - Início: {last_session[0]}")
                print(f"   - Fim: {last_session[1]}")
                print(f"   - ZIPs processados: {last_session[2]}")
                print(f"   - Logs processados: {last_session[3]}")
                print(f"   - CSVs gerados: {last_session[4]}")
                print(f"   - Registros SQL: {last_session[5]}")
                print(f"   - Erros: {last_session[6]}")
                
        except Exception as e:
            print(f"❌ Erro ao verificar banco local: {e}")
        
        # Status do sistema
        print(f"\n🔧 CONFIGURAÇÕES DO SISTEMA:")
        print(f"   - Host SMB: {SMB_CONFIG['host']}")
        print(f"   - Compartilhamento: {SMB_CONFIG['share']}")
        print(f"   - Ponto de montagem: {SMB_CONFIG['mount_point']}")
        print(f"   - Diretório temporário: {LOCAL_CONFIG['temp_dir']}")
        print(f"   - Diretório de saída: {LOCAL_CONFIG['output_dir']}")
        print(f"   - Banco local: {LOCAL_CONFIG['local_db']}")
        
        # Status do SQL Server
        try:
            from config.settings import DB_CONFIG
            import mysql.connector
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute(f"SELECT COUNT(*) FROM {LOCAL_CONFIG['table_name']}")
            total_records = cursor.fetchone()[0]
            conn.close()
            print(f"   - Registros no SQL Server: {total_records}")
        except Exception as e:
            print(f"   - Erro ao conectar SQL Server: {e}")

    def show_config(self):
        """Exibe configurações atuais."""
        from config.settings import DB_CONFIG
        print("\n⚙️ CONFIGURAÇÕES ATUAIS")
        print("=" * 40)
        print(f"Host SMB: {SMB_CONFIG['host']}")
        print(f"Compartilhamento SMB: {SMB_CONFIG['share']}")
        print(f"Ponto de montagem: {SMB_CONFIG['mount_point']}")
        print(f"Usuário SMB: {SMB_CONFIG['username']}")
        print(f"Diretório temporário: {LOCAL_CONFIG['temp_dir']}")
        print(f"Diretório de saída: {LOCAL_CONFIG['output_dir']}")
        print(f"Banco de dados local: {LOCAL_CONFIG['local_db']}")
        print(f"Tabela remota: {LOCAL_CONFIG['table_name']}")
        print(f"Host do banco remoto: {DB_CONFIG['server']}")
        print(f"Database remoto: {DB_CONFIG['database']}")
