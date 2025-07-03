#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste de Conexões - Processador de Logs EDI
===========================================

Script para testar as conexões SMB e MySQL antes de executar o processamento principal.
"""

import os
import subprocess
import mysql.connector
from config import DB_CONFIG, SMB_CONFIG


def test_smb_connection():
    """Testa a conexão com o compartilhamento SMB."""
    print("🔗 Testando conexão SMB...")
    
    try:
        # Testar conectividade com o host
        ping_cmd = ['ping', '-c', '1', SMB_CONFIG['host']]
        result = subprocess.run(ping_cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"✗ Não foi possível conectar ao host SMB: {SMB_CONFIG['host']}")
            return False
        
        print(f"✓ Host SMB acessível: {SMB_CONFIG['host']}")
        
        # Testar montagem temporária
        test_mount_point = '/tmp/test_smb_mount'
        
        if not os.path.exists(test_mount_point):
            os.makedirs(test_mount_point)
        
        mount_cmd = [
            'sudo', 'mount', '-t', 'cifs',
            f"//{SMB_CONFIG['host']}/{SMB_CONFIG['share']}",
            test_mount_point,
            '-o', f"username={SMB_CONFIG['username']},password={SMB_CONFIG['password']},iocharset=utf8"
        ]
        
        result = subprocess.run(mount_cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✓ Compartilhamento SMB acessível: //{SMB_CONFIG['host']}/{SMB_CONFIG['share']}")
            
            # Listar conteúdo
            try:
                files = os.listdir(test_mount_point)
                print(f"✓ Conteúdo do compartilhamento: {len(files)} itens encontrados")
            except Exception as e:
                print(f"⚠ Não foi possível listar conteúdo: {e}")
            
            # Desmontar
            subprocess.run(['sudo', 'umount', test_mount_point], check=True)
            os.rmdir(test_mount_point)
            
            return True
        else:
            print(f"✗ Erro ao montar compartilhamento: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"✗ Erro ao testar conexão SMB: {e}")
        return False


def test_mysql_connection():
    """Testa a conexão com o banco MySQL."""
    print("\n🗄️ Testando conexão MySQL...")
    
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Testar consulta simples
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()[0]
        print(f"✓ Conexão MySQL estabelecida")
        print(f"✓ Versão do MySQL: {version}")
        
        # Testar acesso ao database
        cursor.execute(f"USE {DB_CONFIG['database']}")
        print(f"✓ Database acessível: {DB_CONFIG['database']}")
        
        # Verificar se a tabela existe
        cursor.execute(f"""
        SELECT COUNT(*)
        FROM information_schema.tables
        WHERE table_schema = '{DB_CONFIG['database']}' AND table_name = 'edi_logs';
        """)
        
        table_exists = cursor.fetchone()[0]
        if table_exists:
            print("✓ Tabela 'edi_logs' existe")
            
            # Contar registros
            cursor.execute("SELECT COUNT(*) FROM edi_logs")
            count = cursor.fetchone()[0]
            print(f"✓ Registros na tabela: {count}")
        else:
            print("ℹ Tabela 'edi_logs' não existe (será criada automaticamente)")
        
        cursor.close()
        conn.close()
        return True
        
    except mysql.connector.Error as e:
        print(f"✗ Erro de conexão MySQL: {e}")
        return False
    except Exception as e:
        print(f"✗ Erro inesperado MySQL: {e}")
        return False


def test_local_directories():
    """Testa a criação dos diretórios locais."""
    print("\n📁 Testando diretórios locais...")
    
    from config import LOCAL_CONFIG
    
    try:
        # Testar criação de diretórios
        os.makedirs(LOCAL_CONFIG['temp_dir'], exist_ok=True)
        os.makedirs(LOCAL_CONFIG['output_dir'], exist_ok=True)
        
        print(f"✓ Diretório temporário: {LOCAL_CONFIG['temp_dir']}")
        print(f"✓ Diretório de saída: {LOCAL_CONFIG['output_dir']}")
        
        # Testar permissões de escrita
        test_file = os.path.join(LOCAL_CONFIG['temp_dir'], 'test.txt')
        with open(test_file, 'w') as f:
            f.write('test')
        os.remove(test_file)
        
        print("✓ Permissões de escrita OK")
        return True
        
    except Exception as e:
        print(f"✗ Erro ao testar diretórios locais: {e}")
        return False


def main():
    """Função principal de teste."""
    print("🧪 TESTE DE CONEXÕES - PROCESSADOR DE LOGS EDI")
    print("=" * 50)
    
    tests = [
        ("SMB", test_smb_connection),
        ("MySQL", test_mysql_connection),
        ("Diretórios Locais", test_local_directories)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"✗ Erro no teste {test_name}: {e}")
            results[test_name] = False
    
    # Resumo final
    print("\n" + "=" * 50)
    print("📋 RESUMO DOS TESTES")
    print("=" * 50)
    
    all_passed = True
    for test_name, result in results.items():
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{test_name}: {status}")
        if not result:
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 TODOS OS TESTES PASSARAM!")
        print("✅ O sistema está pronto para processamento")
    else:
        print("⚠️ ALGUNS TESTES FALHARAM")
        print("❌ Verifique as configurações antes de executar o processamento")
    
    print("=" * 50)


if __name__ == "__main__":
    main() 