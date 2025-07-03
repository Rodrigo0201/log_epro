#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Processador de Arquivos CSV
===========================
Responsável por converter logs EDI para CSV e aplicar filtros.
"""

import os
import re
import csv
import sqlite3
from datetime import datetime
from typing import List, Optional
from config.settings import LOCAL_CONFIG, PROCESSING_CONFIG

class CsvProcessor:
    """Classe responsável pelo processamento de arquivos CSV."""
    
    def __init__(self):
        self.converted_files = []
        self.filtered_files = []
        self.errors = []
        
    def find_log_files(self, base_dir: str) -> List[str]:
        """Encontra todos os arquivos de log EDI com padrão ConsoleEDI_ (não ZIP) apenas na pasta raiz."""
        log_files = []
        print(f"🔍 Procurando arquivos de log com padrão '{PROCESSING_CONFIG['log_file_pattern']}' apenas na raiz de: {base_dir}")
        try:
            for file in os.listdir(base_dir):
                file_path = os.path.join(base_dir, file)
                if os.path.isfile(file_path):
                    if (file.startswith(PROCESSING_CONFIG['log_file_pattern']) and 
                        file.endswith(PROCESSING_CONFIG['log_file_extension'])):
                        log_files.append(file_path)
                        print(f"  ✓ Log encontrado: {file}")
                    else:
                        if file.endswith('.Log') and not file.startswith(PROCESSING_CONFIG['log_file_pattern']):
                            print(f"  ⚠️ Log ignorado (padrão diferente): {file}")
        except Exception as e:
            print(f"✗ Erro ao procurar arquivos de log: {e}")
            self.errors.append(f"Erro na busca de logs: {e}")
        return log_files
    
    def convert_logs_to_csv(self, log_files: List[str]) -> List[str]:
        """Converte arquivos de log para CSV (sempre processa todos, sem pular)."""
        converted_files = []
        
        for log_file in log_files:
            try:
                print(f"📄 Convertendo: {os.path.basename(log_file)}")
                csv_file = self._convert_single_log_to_csv(log_file)
                if csv_file:
                    converted_files.append(csv_file)
                    self.converted_files.append(csv_file)
                    # Não marcar como processado, sempre processa tudo
            except Exception as e:
                error_msg = f"Erro ao converter {os.path.basename(log_file)}: {e}"
                print(f"  ✗ {error_msg}")
                self.errors.append(error_msg)
        
        return converted_files
    
    def _convert_single_log_to_csv(self, log_file: str) -> Optional[str]:
        """Converte um único arquivo de log para CSV."""
        try:
            output_file = os.path.join(
                LOCAL_CONFIG['output_dir'], 
                f"{os.path.basename(log_file).replace(PROCESSING_CONFIG['log_file_extension'], '.csv')}"
            )
            
            with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Data', 'Formato do Processo de EDI', 'Nome do Arquivo'])
                
                with open(log_file, 'r', encoding='utf-8') as infile:
                    content = infile.read()
                    blocks = re.split(f"{PROCESSING_CONFIG['separator_line']}\n", content)
                    
                    for block in blocks:
                        date_match = re.search(r"Data:\s+(\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2})", block)
                        date = date_match.group(1) if date_match else None
                        
                        process_match = re.search(r"Formato do Processo de EDI:\s+(.+)", block)
                        process = process_match.group(1) if process_match else None
                        
                        file_matches = re.findall(r"Nome do Arquivo:\s+(.+)", block)
                        
                        if date and process and file_matches:
                            for file_name in file_matches:
                                writer.writerow([date, process, file_name])
            
            print(f"  ✓ CSV gerado: {os.path.basename(output_file)}")
            return output_file
            
        except Exception as e:
            print(f"  ✗ Erro ao converter {log_file}: {e}")
            return None
    
    def filter_csv_files(self, csv_files: List[str]) -> List[str]:
        """Aplica filtros nos arquivos CSV."""
        filtered_files = []
        
        for csv_file in csv_files:
            try:
                print(f"🔍 Filtrando: {os.path.basename(csv_file)}")
                filtered_file = self._filter_single_csv(csv_file)
                if filtered_file:
                    filtered_files.append(filtered_file)
                    self.filtered_files.append(filtered_file)
            except Exception as e:
                error_msg = f"Erro ao filtrar {os.path.basename(csv_file)}: {e}"
                print(f"  ✗ {error_msg}")
                self.errors.append(error_msg)
        
        return filtered_files
    
    def _filter_single_csv(self, csv_file: str) -> Optional[str]:
        """Aplica filtros em um único arquivo CSV."""
        try:
            filtered_file = csv_file.replace('.csv', '_filtrado.csv')
            palavras_chave = ['Upload de FTP', 'Envio de e-mail por SMTP']
            
            with open(csv_file, 'r', encoding='utf-8') as infile, \
                 open(filtered_file, 'w', newline='', encoding='utf-8') as outfile:
                
                reader = csv.reader(infile)
                writer = csv.writer(outfile)
                
                header = next(reader)
                writer.writerow(header)
                
                filtered_count = 0
                for row in reader:
                    if any(palavra in row[1] for palavra in palavras_chave):
                        writer.writerow(row)
                        filtered_count += 1
            
            print(f"  ✓ CSV filtrado gerado: {os.path.basename(filtered_file)} ({filtered_count} registros)")
            return filtered_file
            
        except Exception as e:
            print(f"  ✗ Erro ao filtrar {csv_file}: {e}")
            return None
    
    def _is_log_processed(self, log_path: str) -> bool:
        """Verifica se um arquivo de log já foi processado baseado no tamanho e timestamp."""
        try:
            if not os.path.exists(log_path):
                return False
                
            # Obter informações atuais do arquivo
            current_size = os.path.getsize(log_path)
            current_mtime = os.path.getmtime(log_path)
            
            conn = sqlite3.connect(LOCAL_CONFIG['local_db'])
            cursor = conn.cursor()
            cursor.execute("""
                SELECT file_size, file_mtime FROM processed_logs 
                WHERE log_path = ?
            """, (log_path,))
            result = cursor.fetchone()
            conn.close()
            
            if result is None:
                # Arquivo nunca foi processado
                return False
            
            stored_size, stored_mtime = result
            
            # Se o arquivo mudou (tamanho ou timestamp), precisa reprocessar
            if current_size != stored_size or current_mtime != stored_mtime:
                print(f"  🔄 Arquivo modificado, reprocessando: {os.path.basename(log_path)}")
                print(f"     Tamanho anterior: {stored_size}, atual: {current_size}")
                return False
            
            return True
            
        except Exception as e:
            print(f"✗ Erro ao verificar log processado: {e}")
            return False
    
    def _mark_log_as_processed(self, log_path: str):
        """Marca um arquivo de log como processado com informações de tamanho e timestamp."""
        try:
            if not os.path.exists(log_path):
                return
                
            # Obter informações atuais do arquivo
            current_size = os.path.getsize(log_path)
            current_mtime = os.path.getmtime(log_path)
            
            conn = sqlite3.connect(LOCAL_CONFIG['local_db'])
            cursor = conn.cursor()
            
            # Usar INSERT OR REPLACE para atualizar se já existir
            cursor.execute("""
                INSERT OR REPLACE INTO processed_logs 
                (log_path, process_date, file_size, file_mtime) 
                VALUES (?, ?, ?, ?)
            """, (log_path, datetime.now(), current_size, current_mtime))
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"✗ Erro ao registrar log processado: {e}")
    
    def init_csv_database(self):
        """Inicializa a tabela de controle de arquivos de log processados."""
        try:
            conn = sqlite3.connect(LOCAL_CONFIG['local_db'])
            cursor = conn.cursor()
            
            # Verificar se a tabela existe
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='processed_logs'
            """)
            table_exists = cursor.fetchone()
            
            if table_exists:
                # Verificar se as colunas file_size e file_mtime existem
                cursor.execute("PRAGMA table_info(processed_logs)")
                columns = [column[1] for column in cursor.fetchall()]
                
                if 'file_size' not in columns:
                    cursor.execute("ALTER TABLE processed_logs ADD COLUMN file_size INTEGER")
                    print("  ✓ Coluna file_size adicionada")
                
                if 'file_mtime' not in columns:
                    cursor.execute("ALTER TABLE processed_logs ADD COLUMN file_mtime REAL")
                    print("  ✓ Coluna file_mtime adicionada")
            else:
                # Criar tabela com as novas colunas
                cursor.execute("""
                    CREATE TABLE processed_logs (
                        log_path TEXT PRIMARY KEY,
                        process_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                        file_size INTEGER,
                        file_mtime REAL,
                        csv_generated TEXT,
                        csv_filtered TEXT
                    );
                """)
                print("  ✓ Tabela processed_logs criada com controle de modificação")
            
            conn.commit()
            conn.close()
            print("✓ Banco de dados de logs inicializado com sucesso.")
        except Exception as e:
            print(f"✗ Erro ao inicializar banco de dados de logs: {e}")
            return False
        return True
    
    def get_summary(self) -> dict:
        """Retorna um resumo do processamento de CSV."""
        return {
            'logs_processed': len(self.converted_files),
            'csvs_generated': len(self.converted_files),
            'csvs_filtered': len(self.filtered_files),
            'errors': len(self.errors),
            'error_details': self.errors
        }
    
    def cleanup_old_csvs(self, days_to_keep: int = 7):
        """Remove arquivos CSV antigos."""
        try:
            cutoff_date = datetime.now().timestamp() - (days_to_keep * 24 * 60 * 60)
            
            for csv_file in os.listdir(LOCAL_CONFIG['output_dir']):
                if csv_file.endswith('.csv'):
                    file_path = os.path.join(LOCAL_CONFIG['output_dir'], csv_file)
                    if os.path.getmtime(file_path) < cutoff_date:
                        os.remove(file_path)
                        print(f"🗑️ Removido CSV antigo: {csv_file}")
                        
        except Exception as e:
            print(f"✗ Erro na limpeza de CSVs antigos: {e}") 