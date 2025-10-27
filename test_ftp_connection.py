#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste de Conexão FTP - Processador de Logs EDI
==============================================

Script para testar a conexão FTP antes de executar o processamento principal.
"""

import os
import sys
from ftplib import FTP
from config.settings import FTP_CONFIG


def test_ftp_connection():
    """Testa a conexão com o servidor FTP."""
    print("🔗 Testando conexão FTP...")
    
    try:
        # Criar cliente FTP
        ftp = FTP()
        
        # Conectar ao servidor
        print(f"📡 Conectando a {FTP_CONFIG['host']}:{FTP_CONFIG['port']}...")
        ftp.connect(
            host=FTP_CONFIG['host'],
            port=FTP_CONFIG['port'],
            timeout=FTP_CONFIG['timeout']
        )
        
        # Login
        print(f"🔐 Fazendo login com usuário: {FTP_CONFIG['username']}")
        ftp.login(
            user=FTP_CONFIG['username'],
            passwd=FTP_CONFIG['password']
        )
        
        # Configurar modo passivo se necessário
        if FTP_CONFIG.get('passive_mode', True):
            ftp.set_pasv(True)
            print("✓ Modo passivo ativado")
        
        # Obter mensagem de boas-vindas
        welcome_msg = ftp.getwelcome()
        print(f"✓ Servidor FTP: {welcome_msg}")
        
        # Navegar para o diretório especificado
        if FTP_CONFIG.get('remote_dir'):
            print(f"📁 Navegando para diretório: {FTP_CONFIG['remote_dir']}")
            ftp.cwd(FTP_CONFIG['remote_dir'])
            current_dir = ftp.pwd()
            print(f"✓ Diretório atual: {current_dir}")
        
        # Listar arquivos
        print("\n📋 Listando arquivos no diretório atual...")
        files = []
        ftp.retrlines('LIST', lambda x: files.append(x))
        
        if files:
            print(f"✓ Total de arquivos: {len(files)}")
            print("\n📁 Primeiros 10 arquivos:")
            for i, file_info in enumerate(files[:10]):
                print(f"   {i+1:2d}. {file_info}")
            
            if len(files) > 10:
                print(f"   ... e mais {len(files) - 10} arquivos")
        else:
            print("ℹ️ Diretório está vazio")
        
        # Procurar por arquivos ConsoleEDI_
        print(f"\n🔍 Procurando por arquivos com padrão '{FTP_CONFIG.get('log_file_pattern', 'ConsoleEDI_')}'...")
        console_edi_files = []
        ftp.retrlines('LIST', lambda x: console_edi_files.append(x.split()[-1]) if 'ConsoleEDI_' in x else None)
        
        if console_edi_files:
            print(f"✓ Encontrados {len(console_edi_files)} arquivos ConsoleEDI_:")
            for i, filename in enumerate(console_edi_files[:5]):
                print(f"   {i+1:2d}. {filename}")
            
            if len(console_edi_files) > 5:
                print(f"   ... e mais {len(console_edi_files) - 5} arquivos")
        else:
            print("ℹ️ Nenhum arquivo ConsoleEDI_ encontrado")
        
        # Testar download de um arquivo pequeno
        if console_edi_files:
            test_file = console_edi_files[0]
            print(f"\n⬇️ Testando download de: {test_file}")
            
            # Criar diretório temporário
            test_dir = 'temp_ftp_test'
            os.makedirs(test_dir, exist_ok=True)
            
            local_path = os.path.join(test_dir, test_file)
            
            try:
                with open(local_path, 'wb') as local_file:
                    ftp.retrbinary(f'RETR {test_file}', local_file.write)
                
                file_size = os.path.getsize(local_path)
                print(f"✓ Download bem-sucedido: {file_size} bytes")
                
                # Limpar arquivo de teste
                os.remove(local_path)
                os.rmdir(test_dir)
                
            except Exception as e:
                print(f"⚠ Erro no download de teste: {e}")
                # Tentar limpar mesmo com erro
                if os.path.exists(local_path):
                    os.remove(local_path)
                if os.path.exists(test_dir):
                    os.rmdir(test_dir)
        
        # Fechar conexão
        ftp.quit()
        print("\n✅ Teste de conexão FTP concluído com sucesso!")
        return True
        
    except Exception as e:
        print(f"\n❌ Erro ao testar conexão FTP: {e}")
        return False


def test_local_directories():
    """Testa se os diretórios locais necessários existem."""
    print("\n📁 Testando diretórios locais...")
    
    required_dirs = [
        FTP_CONFIG.get('local_download_dir', 'temp_unzipped_logs'),
        'processed_csvs',
        'reports',
        'logs'
    ]
    
    for dir_path in required_dirs:
        if os.path.exists(dir_path):
            print(f"✓ Diretório existe: {dir_path}")
        else:
            try:
                os.makedirs(dir_path, exist_ok=True)
                print(f"✓ Diretório criado: {dir_path}")
            except Exception as e:
                print(f"✗ Erro ao criar diretório {dir_path}: {e}")
                return False
    
    return True


def main():
    """Função principal de teste."""
    print("🧪 TESTE DE CONEXÃO FTP - PROCESSADOR DE LOGS EDI")
    print("=" * 60)
    
    # Testar diretórios locais
    if not test_local_directories():
        print("\n❌ Falha na verificação de diretórios locais")
        sys.exit(1)
    
    # Testar conexão FTP
    if not test_ftp_connection():
        print("\n❌ Falha na conexão FTP")
        sys.exit(1)
    
    print("\n🎉 Todos os testes passaram! O sistema FTP está funcionando corretamente.")
    print("\n💡 Próximos passos:")
    print("   1. Execute: python cli/main.py")
    print("   2. Ou use Docker: docker-compose up --build")


if __name__ == "__main__":
    main()
