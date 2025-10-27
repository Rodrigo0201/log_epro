#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Utilitários FTP para o Processador de Logs EDI
==============================================
Substitui as funcionalidades SMB por conexão FTP.
"""

import os
import tempfile
from ftplib import FTP
from typing import List, Optional
from config.settings import FTP_CONFIG

class FTPClient:
    """Cliente FTP para acessar arquivos de log."""
    
    def __init__(self):
        self.ftp = None
        self.connected = False
        self.temp_dir = None
        
    def connect(self) -> bool:
        """Conecta ao servidor FTP."""
        try:
            print(f"🔗 Conectando ao servidor FTP: {FTP_CONFIG['host']}:{FTP_CONFIG['port']}")
            
            self.ftp = FTP()
            self.ftp.connect(
                host=FTP_CONFIG['host'],
                port=FTP_CONFIG['port'],
                timeout=FTP_CONFIG['timeout']
            )
            
            # Login
            self.ftp.login(
                user=FTP_CONFIG['username'],
                passwd=FTP_CONFIG['password']
            )
            
            # Configurar modo passivo se necessário
            if FTP_CONFIG.get('passive_mode', True):
                self.ftp.set_pasv(True)
            
            # Navegar para o diretório especificado
            if FTP_CONFIG.get('remote_dir'):
                self.ftp.cwd(FTP_CONFIG['remote_dir'])
                print(f"✓ Diretório remoto: {FTP_CONFIG['remote_dir']}")
            
            self.connected = True
            print(f"✓ Conexão FTP estabelecida com sucesso")
            print(f"✓ Servidor: {self.ftp.getwelcome()}")
            
            return True
            
        except Exception as e:
            print(f"✗ Erro ao conectar ao FTP: {e}")
            self.connected = False
            return False
    
    def disconnect(self):
        """Desconecta do servidor FTP."""
        if self.ftp and self.connected:
            try:
                self.ftp.quit()
                print("✓ Conexão FTP encerrada")
            except Exception as e:
                print(f"⚠ Aviso: Erro ao desconectar FTP: {e}")
            finally:
                self.ftp = None
                self.connected = False
    
    def list_files(self, pattern: str = None) -> List[str]:
        """Lista arquivos no diretório atual, opcionalmente filtrados por padrão."""
        if not self.connected:
            print("✗ Não conectado ao servidor FTP")
            return []
        
        try:
            files = []
            self.ftp.retrlines('LIST', lambda x: files.append(x.split()[-1]))
            
            if pattern:
                # Filtrar por padrão (ex: ConsoleEDI_)
                filtered_files = [f for f in files if pattern in f]
                print(f"📁 Encontrados {len(filtered_files)} arquivos com padrão '{pattern}'")
                return filtered_files
            else:
                print(f"📁 Total de arquivos: {len(files)}")
                return files
                
        except Exception as e:
            print(f"✗ Erro ao listar arquivos: {e}")
            return []
    
    def download_file(self, remote_file: str, local_path: str) -> bool:
        """Baixa um arquivo do servidor FTP."""
        if not self.connected:
            print(f"✗ Não conectado ao servidor FTP")
            return False
        
        try:
            print(f"⬇️ Baixando: {remote_file}")
            
            with open(local_path, 'wb') as local_file:
                self.ftp.retrbinary(f'RETR {remote_file}', local_file.write)
            
            print(f"✓ Arquivo baixado: {local_path}")
            return True
            
        except Exception as e:
            print(f"✗ Erro ao baixar {remote_file}: {e}")
            return False
    
    def download_files(self, file_pattern: str, local_dir: str) -> List[str]:
        """Baixa múltiplos arquivos que correspondem ao padrão."""
        if not self.connected:
            print("✗ Não conectado ao servidor FTP")
            return []
        
        # Listar arquivos que correspondem ao padrão
        remote_files = self.list_files(file_pattern)
        if not remote_files:
            print(f"ℹ️ Nenhum arquivo encontrado com padrão '{file_pattern}'")
            return []
        
        # Criar diretório local se não existir
        os.makedirs(local_dir, exist_ok=True)
        
        downloaded_files = []
        for remote_file in remote_files:
            local_file = os.path.join(local_dir, remote_file)
            
            if self.download_file(remote_file, local_file):
                downloaded_files.append(local_file)
        
        print(f"✅ Total de arquivos baixados: {len(downloaded_files)}")
        return downloaded_files
    
    def get_file_size(self, filename: str) -> Optional[int]:
        """Obtém o tamanho de um arquivo remoto."""
        if not self.connected:
            return None
        
        try:
            size = self.ftp.size(filename)
            return size
        except Exception as e:
            print(f"⚠ Não foi possível obter tamanho de {filename}: {e}")
            return None
    
    def file_exists(self, filename: str) -> bool:
        """Verifica se um arquivo existe no servidor."""
        if not self.connected:
            return False
        
        try:
            size = self.ftp.size(filename)
            return size is not None and size >= 0
        except:
            return False

def connect_ftp():
    """Função de conveniência para conectar ao FTP."""
    client = FTPClient()
    if client.connect():
        return client
    return None

def disconnect_ftp(client: FTPClient):
    """Função de conveniência para desconectar do FTP."""
    if client:
        client.disconnect()
