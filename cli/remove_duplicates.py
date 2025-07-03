#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para Remover Duplicatas e Resetar Processamento
=====================================================
Resolve problemas de arquivos duplicados e reset do banco de dados.
"""

import os
import sqlite3
import shutil
from datetime import datetime

def reset_processing():
    """Reseta completamente o processamento, removendo arquivos temporários e resetando banco."""
    print("🔄 RESETANDO PROCESSAMENTO EDI")
    print("=" * 50)
    
    # 1. Limpar arquivos temporários
    print("🧹 Limpando arquivos temporários...")
    temp_dir = "temp_unzipped_logs"
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
        os.makedirs(temp_dir)
        print(f"✅ Diretório {temp_dir} limpo e recriado")
    
    # 2. Limpar CSVs processados
    print("🧹 Limpando CSVs processados...")
    csv_dir = "processed_csvs"
    if os.path.exists(csv_dir):
        for file in os.listdir(csv_dir):
            if file.endswith('.csv'):
                os.remove(os.path.join(csv_dir, file))
        print(f"✅ CSVs em {csv_dir} removidos")
    
    # 3. Resetar banco de dados
    print("🗄️ Resetando banco de dados...")
    try:
        conn = sqlite3.connect('processed_files.db')
        cursor = conn.cursor()
        
        # Limpar tabelas
        cursor.execute("DELETE FROM processed_zips")
        cursor.execute("DELETE FROM processed_logs")
        cursor.execute("DELETE FROM processing_sessions")
        
        conn.commit()
        conn.close()
        print("✅ Banco de dados resetado")
        
    except Exception as e:
        print(f"❌ Erro ao resetar banco: {e}")
        return False
    
    print("\n✅ Reset completo realizado!")
    print("📝 Próxima execução processará todos os arquivos novamente.")
    return True

def clean_duplicates_only():
    """Remove apenas arquivos duplicados, mantendo processamento."""
    print("🧹 REMOVENDO APENAS DUPLICATAS")
    print("=" * 50)
    
    # 1. Limpar arquivos temporários
    print("🧹 Limpando arquivos temporários...")
    temp_dir = "temp_unzipped_logs"
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
        os.makedirs(temp_dir)
        print(f"✅ Diretório {temp_dir} limpo e recriado")
    
    # 2. Resetar apenas tabela de ZIPs
    print("🗄️ Resetando controle de ZIPs...")
    try:
        conn = sqlite3.connect('processed_files.db')
        cursor = conn.cursor()
        cursor.execute("DELETE FROM processed_zips")
        conn.commit()
        conn.close()
        print("✅ Controle de ZIPs resetado")
        
    except Exception as e:
        print(f"❌ Erro ao resetar controle: {e}")
        return False
    
    print("\n✅ Limpeza de duplicatas realizada!")
    print("📝 Próxima execução reprocessará apenas ZIPs.")
    return True

def force_reprocess_logs():
    """Força reprocessamento de todos os arquivos de log ConsoleEDI_."""
    print("🔄 FORÇANDO REPROCESSAMENTO DE LOGS")
    print("=" * 50)
    
    try:
        conn = sqlite3.connect('processed_files.db')
        cursor = conn.cursor()
        
        # Limpar apenas a tabela de logs processados
        cursor.execute("DELETE FROM processed_logs")
        conn.commit()
        conn.close()
        
        print("✅ Controle de logs resetado - todos os arquivos serão reprocessados")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao forçar reprocessamento: {e}")
        return False

def show_status():
    """Mostra status atual do sistema."""
    print("📊 STATUS ATUAL DO SISTEMA")
    print("=" * 50)
    
    # Verificar arquivos temporários
    temp_dir = "temp_unzipped_logs"
    if os.path.exists(temp_dir):
        temp_files = len([f for f in os.listdir(temp_dir) if f.endswith('.Log')])
        print(f"📁 Arquivos temporários: {temp_files}")
    else:
        print("📁 Diretório temporário: Não existe")
    
    # Verificar CSVs processados
    csv_dir = "processed_csvs"
    if os.path.exists(csv_dir):
        csv_files = len([f for f in os.listdir(csv_dir) if f.endswith('.csv')])
        print(f"📄 CSVs processados: {csv_files}")
    else:
        print("📄 Diretório de CSVs: Não existe")
    
    # Verificar banco de dados
    try:
        conn = sqlite3.connect('processed_files.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM processed_zips")
        zips_processed = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM processed_logs")
        logs_processed = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM processing_sessions")
        sessions = cursor.fetchone()[0]
        
        conn.close()
        
        print(f"🗄️ ZIPs processados (DB): {zips_processed}")
        print(f"🗄️ Logs processados (DB): {logs_processed}")
        print(f"🗄️ Sessões registradas: {sessions}")
        
    except Exception as e:
        print(f"❌ Erro ao verificar banco: {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "reset":
            reset_processing()
        elif command == "clean":
            clean_duplicates_only()
        elif command == "status":
            show_status()
        else:
            print("❌ Comando inválido. Use: reset, clean ou status")
    else:
        print("🔄 SCRIPT DE LIMPEZA EDI EPRO")
        print("=" * 40)
        print("Uso:")
        print("  python cli/remove_duplicates.py reset   # Reset completo")
        print("  python cli/remove_duplicates.py clean   # Limpar duplicatas")
        print("  python cli/remove_duplicates.py status  # Ver status")
        print("\n⚠️  ATENÇÃO: Reset completo remove TODOS os dados!") 