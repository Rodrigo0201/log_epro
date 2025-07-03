#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Processador de Arquivos ZIP
===========================
Responsável por extrair e processar arquivos ZIP contendo logs EDI.
"""

import os
import zipfile
import sqlite3
import shutil
from datetime import datetime
from typing import List, Tuple
from config.settings import LOCAL_CONFIG, PROCESSING_CONFIG

class ZipProcessor:
    """Classe responsável pelo processamento de arquivos ZIP."""
    
    def __init__(self):
        self.extracted_files = []
        self.processed_zips = []
        self.errors = []
        
    def find_zip_files(self, base_dir: str) -> List[str]:
        """Encontra todos os arquivos ZIP que contêm logs EDI com padrão ConsoleEDI_."""
        zip_files = []
        print(f"🔍 Procurando arquivos ZIP com padrão '{PROCESSING_CONFIG['log_file_pattern']}' em: {base_dir}")
        
        try:
            for root, _, files in os.walk(base_dir):
                for file in files:
                    # Verificar se o arquivo começa com 'ConsoleEDI_' e termina com '.Log.zip'
                    if (file.startswith(PROCESSING_CONFIG['log_file_pattern']) and 
                        file.endswith(PROCESSING_CONFIG['zip_file_extension'])):
                        zip_path = os.path.join(root, file)
                        zip_files.append(zip_path)
                        print(f"  ✓ ZIP encontrado: {file}")
                    else:
                        # Log para arquivos ignorados (opcional, para debug)
                        if file.endswith('.zip') and not file.startswith(PROCESSING_CONFIG['log_file_pattern']):
                            print(f"  ⚠️ ZIP ignorado (padrão diferente): {file}")
        except Exception as e:
            print(f"✗ Erro ao procurar arquivos ZIP: {e}")
            self.errors.append(f"Erro na busca de ZIPs: {e}")
            
        return zip_files
    
    def extract_zip_files(self, zip_files: List[str]) -> List[str]:
        """Extrai arquivos ZIP e retorna lista de arquivos extraídos."""
        extracted_files = []
        
        for zip_path in zip_files:
            try:
                print(f"📦 Extraindo: {os.path.basename(zip_path)}")
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    # Criar diretório temporário específico para este ZIP
                    zip_name = os.path.splitext(os.path.basename(zip_path))[0]
                    extract_dir = os.path.join(LOCAL_CONFIG['temp_dir'], zip_name)
                    
                    # Verificar se o diretório já existe e limpar se necessário
                    if os.path.exists(extract_dir):
                        print(f"  ⚠️ Diretório já existe, removendo conteúdo anterior...")
                        if os.path.isdir(extract_dir):
                            shutil.rmtree(extract_dir)
                        else:
                            # Se for um arquivo, removê-lo
                            os.remove(extract_dir)
                    
                    os.makedirs(extract_dir, exist_ok=True)
                    
                    # Extrair arquivos
                    zip_ref.extractall(extract_dir)
                    
                    # Verificar arquivos extraídos
                    for extracted_file in zip_ref.namelist():
                        extracted_path = os.path.join(extract_dir, extracted_file)
                        # Verificar se o arquivo extraído tem o padrão correto
                        if (extracted_file.startswith(PROCESSING_CONFIG['log_file_pattern']) and 
                            extracted_file.endswith(PROCESSING_CONFIG['log_file_extension'])):
                            extracted_files.append(extracted_path)
                            print(f"  ✓ Arquivo extraído: {extracted_file}")
                        else:
                            # Log para arquivos ignorados dentro do ZIP
                            if extracted_file.endswith('.Log') and not extracted_file.startswith(PROCESSING_CONFIG['log_file_pattern']):
                                print(f"  ⚠️ Arquivo ignorado no ZIP (padrão diferente): {extracted_file}")
                    
                    self.processed_zips.append(zip_path)
                    # Não marcar como processado para permitir reprocessamento
                    # self._mark_zip_as_processed(zip_path)
                    
            except Exception as e:
                error_msg = f"Erro ao extrair {os.path.basename(zip_path)}: {e}"
                print(f"  ✗ {error_msg}")
                self.errors.append(error_msg)
        
        self.extracted_files = extracted_files
        return extracted_files
    
    def _is_zip_processed(self, zip_path: str) -> bool:
        """Verifica se um arquivo ZIP já foi processado."""
        try:
            conn = sqlite3.connect(LOCAL_CONFIG['local_db'])
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM processed_zips WHERE zip_path = ?", (zip_path,))
            result = cursor.fetchone()
            conn.close()
            
            if result is not None:
                # Verificar se os arquivos extraídos ainda existem
                zip_name = os.path.splitext(os.path.basename(zip_path))[0]
                extract_dir = os.path.join(LOCAL_CONFIG['temp_dir'], zip_name)
                
                if os.path.exists(extract_dir):
                    # Verificar se há arquivos de log no diretório
                    log_files = [f for f in os.listdir(extract_dir) 
                               if f.startswith(PROCESSING_CONFIG['log_file_pattern']) and 
                               f.endswith(PROCESSING_CONFIG['log_file_extension'])]
                    
                    if log_files:
                        print(f"  ℹ️ ZIP já processado e arquivos existem: {os.path.basename(zip_path)}")
                        return True
                    else:
                        print(f"  ⚠️ ZIP marcado como processado mas arquivos não encontrados: {os.path.basename(zip_path)}")
                        return False
                else:
                    print(f"  ⚠️ ZIP marcado como processado mas diretório não existe: {os.path.basename(zip_path)}")
                    return False
            
            return False
            
        except Exception as e:
            print(f"✗ Erro ao verificar ZIP processado: {e}")
            return False
    
    def _mark_zip_as_processed(self, zip_path: str):
        """Marca um arquivo ZIP como processado."""
        try:
            conn = sqlite3.connect(LOCAL_CONFIG['local_db'])
            cursor = conn.cursor()
            cursor.execute("INSERT INTO processed_zips (zip_path, process_date) VALUES (?, ?)", 
                         (zip_path, datetime.now()))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"✗ Erro ao registrar ZIP processado: {e}")
    
    def init_zip_database(self):
        """Inicializa a tabela de controle de arquivos ZIP processados."""
        try:
            conn = sqlite3.connect(LOCAL_CONFIG['local_db'])
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS processed_zips (
                    zip_path TEXT PRIMARY KEY,
                    process_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                    extracted_files_count INTEGER DEFAULT 0
                );
            """)
            conn.commit()
            conn.close()
            print("✓ Banco de dados de ZIPs inicializado com sucesso.")
        except Exception as e:
            print(f"✗ Erro ao inicializar banco de dados de ZIPs: {e}")
            return False
        return True
    
    def get_summary(self) -> dict:
        """Retorna um resumo do processamento de ZIPs."""
        return {
            'zips_processed': len(self.processed_zips),
            'files_extracted': len(self.extracted_files),
            'errors': len(self.errors),
            'error_details': self.errors
        }
    
    def cleanup_temp_files(self):
        """Remove arquivos temporários extraídos."""
        try:
            for file_path in self.extracted_files:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    print(f"🗑️ Removido arquivo temporário: {os.path.basename(file_path)}")
            
            # Remover diretórios vazios
            temp_dirs = [d for d in os.listdir(LOCAL_CONFIG['temp_dir']) 
                        if os.path.isdir(os.path.join(LOCAL_CONFIG['temp_dir'], d))]
            
            for temp_dir in temp_dirs:
                temp_dir_path = os.path.join(LOCAL_CONFIG['temp_dir'], temp_dir)
                if not os.listdir(temp_dir_path):  # Se estiver vazio
                    os.rmdir(temp_dir_path)
                    print(f"🗑️ Removido diretório temporário: {temp_dir}")
                    
        except Exception as e:
            print(f"✗ Erro na limpeza de arquivos temporários: {e}") 