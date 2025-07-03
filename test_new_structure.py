#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste da Nova Estrutura do Processador EDI
==========================================
Script para verificar se todos os módulos estão funcionando corretamente.
"""

import sys
import os
import sqlite3
from datetime import datetime

# Adicionar o diretório atual ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Testa se todos os módulos podem ser importados."""
    print("🔍 Testando importações...")
    
    try:
        from config.settings import (
            DB_CONFIG, SMB_CONFIG, LOCAL_CONFIG, 
            PROCESSING_CONFIG, CSV_FILTER_CONFIG
        )
        print("✅ Configurações importadas com sucesso")
    except Exception as e:
        print(f"❌ Erro ao importar configurações: {e}")
        return False
    
    try:
        from core.zip_processor import ZipProcessor
        print("✅ ZipProcessor importado com sucesso")
    except Exception as e:
        print(f"❌ Erro ao importar ZipProcessor: {e}")
        return False
    
    try:
        from core.csv_processor import CsvProcessor
        print("✅ CsvProcessor importado com sucesso")
    except Exception as e:
        print(f"❌ Erro ao importar CsvProcessor: {e}")
        return False
    
    try:
        from core.processor import LogProcessor
        print("✅ LogProcessor importado com sucesso")
    except Exception as e:
        print(f"❌ Erro ao importar LogProcessor: {e}")
        return False
    
    try:
        from core.report_manager import ReportManager
        print("✅ ReportManager importado com sucesso")
    except Exception as e:
        print(f"❌ Erro ao importar ReportManager: {e}")
        return False
    
    return True

def test_database_creation():
    """Testa a criação dos bancos de dados."""
    print("\n🗄️ Testando criação de bancos de dados...")
    
    try:
        from config.settings import LOCAL_CONFIG
        
        # Criar diretórios
        os.makedirs(LOCAL_CONFIG['temp_dir'], exist_ok=True)
        os.makedirs(LOCAL_CONFIG['output_dir'], exist_ok=True)
        os.makedirs('reports', exist_ok=True)
        print("✅ Diretórios criados com sucesso")
        
        # Testar criação do banco principal
        conn = sqlite3.connect(LOCAL_CONFIG['local_db'])
        cursor = conn.cursor()
        
        # Tabela de sessões
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
        
        # Tabela de ZIPs processados
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS processed_zips (
                zip_path TEXT PRIMARY KEY,
                process_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                extracted_files_count INTEGER DEFAULT 0
            );
        """)
        
        # Tabela de logs processados
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS processed_logs (
                log_path TEXT PRIMARY KEY,
                process_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                csv_generated TEXT,
                csv_filtered TEXT
            );
        """)
        
        conn.commit()
        conn.close()
        print("✅ Tabelas criadas com sucesso")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao criar bancos de dados: {e}")
        return False

def test_processors():
    """Testa a inicialização dos processadores."""
    print("\n⚙️ Testando inicialização dos processadores...")
    
    try:
        from core.zip_processor import ZipProcessor
        from core.csv_processor import CsvProcessor
        from core.processor import LogProcessor
        from core.report_manager import ReportManager
        
        # Testar ZipProcessor
        zip_proc = ZipProcessor()
        if zip_proc.init_zip_database():
            print("✅ ZipProcessor inicializado com sucesso")
        else:
            print("❌ Erro ao inicializar ZipProcessor")
            return False
        
        # Testar CsvProcessor
        csv_proc = CsvProcessor()
        if csv_proc.init_csv_database():
            print("✅ CsvProcessor inicializado com sucesso")
        else:
            print("❌ Erro ao inicializar CsvProcessor")
            return False
        
        # Testar LogProcessor
        log_proc = LogProcessor()
        print("✅ LogProcessor inicializado com sucesso")
        
        # Testar ReportManager
        report_mgr = ReportManager()
        print("✅ ReportManager inicializado com sucesso")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao testar processadores: {e}")
        return False

def test_configurations():
    """Testa se as configurações estão corretas."""
    print("\n⚙️ Testando configurações...")
    
    try:
        from config.settings import (
            DB_CONFIG, SMB_CONFIG, LOCAL_CONFIG, 
            PROCESSING_CONFIG, CSV_FILTER_CONFIG
        )
        
        # Verificar configurações obrigatórias
        required_configs = [
            ('DB_CONFIG', DB_CONFIG, ['server', 'database', 'username', 'password']),
            ('SMB_CONFIG', SMB_CONFIG, ['host', 'share', 'username', 'password', 'mount_point']),
            ('LOCAL_CONFIG', LOCAL_CONFIG, ['temp_dir', 'output_dir', 'table_name', 'local_db']),
            ('PROCESSING_CONFIG', PROCESSING_CONFIG, ['log_file_pattern', 'log_file_extension', 'zip_file_extension']),
        ]
        
        for config_name, config, required_keys in required_configs:
            for key in required_keys:
                if key not in config:
                    print(f"❌ Chave '{key}' ausente em {config_name}")
                    return False
            print(f"✅ {config_name} configurado corretamente")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao testar configurações: {e}")
        return False

def test_report_generation():
    """Testa a geração de relatórios."""
    print("\n📊 Testando geração de relatórios...")
    
    try:
        from core.report_manager import ReportManager
        
        report_mgr = ReportManager()
        
        # Testar estatísticas
        stats = report_mgr.get_processing_statistics(7)
        print(f"✅ Estatísticas obtidas: {len(stats)} campos")
        
        # Testar relatório diário
        daily_report = report_mgr.generate_daily_report()
        if daily_report:
            print(f"✅ Relatório diário gerado: {daily_report}")
        else:
            print("⚠️ Relatório diário não gerado (sem dados)")
        
        # Testar relatório semanal
        weekly_report = report_mgr.generate_weekly_report()
        if weekly_report:
            print(f"✅ Relatório semanal gerado: {weekly_report}")
        else:
            print("⚠️ Relatório semanal não gerado (sem dados)")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao testar relatórios: {e}")
        return False

def main():
    """Executa todos os testes."""
    print("🧪 TESTE DA NOVA ESTRUTURA DO PROCESSADOR EDI")
    print("=" * 50)
    
    tests = [
        ("Importações", test_imports),
        ("Configurações", test_configurations),
        ("Bancos de Dados", test_database_creation),
        ("Processadores", test_processors),
        ("Relatórios", test_report_generation),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 Executando teste: {test_name}")
        if test_func():
            passed += 1
            print(f"✅ {test_name}: PASSOU")
        else:
            print(f"❌ {test_name}: FALHOU")
    
    print("\n" + "=" * 50)
    print(f"📊 RESULTADO DOS TESTES: {passed}/{total} PASSARAM")
    
    if passed == total:
        print("🎉 TODOS OS TESTES PASSARAM! A nova estrutura está funcionando.")
        print("\n🚀 Você pode agora usar os comandos:")
        print("   python cli/main.py --status")
        print("   python cli/main.py --stats")
        print("   python cli/main.py --report-daily")
        print("   python cli/main.py --cleanup")
    else:
        print("⚠️ Alguns testes falharam. Verifique os erros acima.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 