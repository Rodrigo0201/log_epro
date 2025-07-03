#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CLI principal do Processador de Logs EDI
"""
import sys
import os
import argparse
from datetime import datetime

# Adicionar o diretório pai ao path para permitir importações
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.processor import LogProcessor
from core.report_manager import ReportManager

def main():
    parser = argparse.ArgumentParser(
        description="Processador de Logs EDI - CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  python cli/main.py                    # Execução manual
  python cli/main.py --status           # Ver status
  python cli/main.py --config           # Ver configurações
  python cli/main.py --stats            # Ver estatísticas
  python cli/main.py --report-daily     # Gerar relatório diário
  python cli/main.py --report-weekly    # Gerar relatório semanal
        """
    )
    
    # Argumentos principais
    parser.add_argument('--config', action='store_true', 
                       help='Mostrar configurações atuais')
    parser.add_argument('--status', action='store_true', 
                       help='Mostrar status do processamento')
    parser.add_argument('--stats', action='store_true', 
                       help='Mostrar estatísticas do processamento')
    
    # Argumentos de relatórios
    parser.add_argument('--report-daily', action='store_true',
                       help='Gerar relatório diário')
    parser.add_argument('--report-weekly', action='store_true',
                       help='Gerar relatório semanal')
    parser.add_argument('--stats-days', type=int, default=30,
                       help='Número de dias para estatísticas (padrão: 30)')
    
    # Argumentos de limpeza
    parser.add_argument('--cleanup', action='store_true',
                       help='Realizar limpeza de arquivos temporários e antigos')
    parser.add_argument('--reset', action='store_true',
                       help='Reset completo do processamento (remove todos os dados)')
    parser.add_argument('--clean-duplicates', action='store_true',
                       help='Limpar apenas duplicatas, mantendo processamento')
    parser.add_argument('--force-reprocess', action='store_true',
                       help='Forçar reprocessamento de todos os arquivos ConsoleEDI_')
    
    args = parser.parse_args()
    
    # Inicializar processadores
    processor = LogProcessor()
    report_manager = ReportManager()
    
    # Executar comandos
    if args.config:
        processor.show_config()
        return
    
    if args.status:
        processor.show_status()
        return
    
    if args.stats:
        report_manager.print_statistics(args.stats_days)
        return
    
    if args.report_daily:
        report_file = report_manager.generate_daily_report()
        if report_file:
            print(f"📊 Relatório salvo em: {report_file}")
        return
    
    if args.report_weekly:
        report_file = report_manager.generate_weekly_report()
        if report_file:
            print(f"📊 Relatório salvo em: {report_file}")
        return
    
    if args.cleanup:
        print("🧹 Iniciando limpeza...")
        processor.zip_processor.cleanup_temp_files()
        processor.csv_processor.cleanup_old_csvs()
        report_manager.cleanup_old_reports()
        print("✅ Limpeza concluída!")
        return
    
    if args.reset:
        print("🔄 Iniciando reset completo...")
        from cli.remove_duplicates import reset_processing
        if reset_processing():
            print("✅ Reset completo realizado!")
        else:
            print("❌ Erro durante reset!")
            sys.exit(1)
        return
    
    if args.clean_duplicates:
        print("🧹 Iniciando limpeza de duplicatas...")
        from cli.remove_duplicates import clean_duplicates_only
        if clean_duplicates_only():
            print("✅ Limpeza de duplicatas realizada!")
        else:
            print("❌ Erro durante limpeza!")
            sys.exit(1)
        return
    
    if args.force_reprocess:
        print("🔄 Forçando reprocessamento de todos os arquivos ConsoleEDI_...")
        from cli.remove_duplicates import force_reprocess_logs
        if force_reprocess_logs():
            print("✅ Reprocessamento forçado realizado!")
        else:
            print("❌ Erro durante reprocessamento!")
            sys.exit(1)
        return
    
    # Execução padrão - processamento completo
    print("🚀 Iniciando processamento EDI...")
    success = processor.run_processing()
    
    if success:
        print("\n✅ Processamento concluído com sucesso!")
        
        # Gerar relatório diário automaticamente
        print("\n📊 Gerando relatório diário...")
        report_file = report_manager.generate_daily_report()
        if report_file:
            print(f"📄 Relatório salvo em: {report_file}")
    else:
        print("\n❌ Processamento falhou!")
        sys.exit(1)

if __name__ == "__main__":
    main()
