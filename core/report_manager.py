#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gerenciador de Relatórios
=========================
Responsável por gerar relatórios e estatísticas do processamento EDI.
"""

import os
import sqlite3
import csv
from datetime import datetime, timedelta
from typing import Dict, List, Any
from config.settings import LOCAL_CONFIG

class ReportManager:
    """Classe responsável por gerar relatórios e estatísticas."""
    
    def __init__(self):
        self.reports_dir = "reports"
        os.makedirs(self.reports_dir, exist_ok=True)
    
    def generate_daily_report(self, date: datetime | None = None) -> str:
        """Gera relatório diário de processamento."""
        if date is None:
            date = datetime.now()
        
        report_file = os.path.join(
            self.reports_dir, 
            f"relatorio_diario_{date.strftime('%Y%m%d')}.csv"
        )
        
        try:
            conn = sqlite3.connect(LOCAL_CONFIG['local_db'])
            cursor = conn.cursor()
            
            # Buscar sessões do dia
            start_date = date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = start_date + timedelta(days=1)
            
            cursor.execute("""
                SELECT 
                    session_id,
                    start_time,
                    end_time,
                    zip_files_processed,
                    log_files_processed,
                    csv_files_generated,
                    sql_records_inserted,
                    errors_count
                FROM processing_sessions 
                WHERE start_time >= ? AND start_time < ?
                ORDER BY start_time
            """, (start_date, end_date))
            
            sessions = cursor.fetchall()
            
            # Gerar CSV do relatório
            with open(report_file, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([
                    'Sessão ID', 'Início', 'Fim', 'Duração (min)',
                    'ZIPs Processados', 'Logs Processados', 
                    'CSVs Gerados', 'Registros SQL', 'Erros'
                ])
                
                for session in sessions:
                    start_time = datetime.fromisoformat(session[1])
                    end_time = datetime.fromisoformat(session[2]) if session[2] else None
                    duration = (end_time - start_time).total_seconds() / 60 if end_time else 0
                    
                    writer.writerow([
                        session[0], session[1], session[2], f"{duration:.2f}",
                        session[3], session[4], session[5], session[6], session[7]
                    ])
            
            conn.close()
            print(f"✅ Relatório diário gerado: {os.path.basename(report_file)}")
            return report_file
            
        except Exception as e:
            print(f"❌ Erro ao gerar relatório diário: {e}")
            return ""
    
    def generate_weekly_report(self, start_date: datetime | None = None) -> str:
        """Gera relatório semanal de processamento."""
        if start_date is None:
            # Início da semana atual (segunda-feira)
            today = datetime.now()
            start_date = today - timedelta(days=today.weekday())
            start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        
        end_date = start_date + timedelta(days=7)
        
        report_file = os.path.join(
            self.reports_dir, 
            f"relatorio_semanal_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.csv"
        )
        
        try:
            conn = sqlite3.connect(LOCAL_CONFIG['local_db'])
            cursor = conn.cursor()
            
            # Estatísticas por dia
            cursor.execute("""
                SELECT 
                    DATE(start_time) as data,
                    COUNT(*) as sessoes,
                    SUM(zip_files_processed) as total_zips,
                    SUM(log_files_processed) as total_logs,
                    SUM(csv_files_generated) as total_csvs,
                    SUM(sql_records_inserted) as total_sql,
                    SUM(errors_count) as total_erros
                FROM processing_sessions 
                WHERE start_time >= ? AND start_time < ?
                GROUP BY DATE(start_time)
                ORDER BY data
            """, (start_date, end_date))
            
            daily_stats = cursor.fetchall()
            
            # Gerar CSV do relatório
            with open(report_file, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([
                    'Data', 'Sessões', 'ZIPs Processados', 'Logs Processados',
                    'CSVs Gerados', 'Registros SQL', 'Erros'
                ])
                
                for stat in daily_stats:
                    writer.writerow(stat)
            
            conn.close()
            print(f"✅ Relatório semanal gerado: {os.path.basename(report_file)}")
            return report_file
            
        except Exception as e:
            print(f"❌ Erro ao gerar relatório semanal: {e}")
            return None
    
    def get_processing_statistics(self, days: int = 30) -> Dict[str, Any]:
        """Retorna estatísticas gerais do processamento."""
        try:
            conn = sqlite3.connect(LOCAL_CONFIG['local_db'])
            cursor = conn.cursor()
            
            # Período
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # Estatísticas gerais
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_sessoes,
                    SUM(zip_files_processed) as total_zips,
                    SUM(log_files_processed) as total_logs,
                    SUM(csv_files_generated) as total_csvs,
                    SUM(sql_records_inserted) as total_sql,
                    SUM(errors_count) as total_erros,
                    AVG((julianday(end_time) - julianday(start_time)) * 24 * 60) as avg_duration_min
                FROM processing_sessions 
                WHERE start_time >= ?
            """, (start_date,))
            
            general_stats = cursor.fetchone()
            
            # Última sessão
            cursor.execute("""
                SELECT start_time, end_time, zip_files_processed, log_files_processed,
                       csv_files_generated, sql_records_inserted, errors_count
                FROM processing_sessions 
                ORDER BY session_id DESC LIMIT 1
            """)
            
            last_session = cursor.fetchone()
            
            # Arquivos processados
            cursor.execute("SELECT COUNT(*) FROM processed_zips")
            total_zips_processed = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM processed_logs")
            total_logs_processed = cursor.fetchone()[0]
            
            conn.close()
            
            stats = {
                'periodo_dias': days,
                'data_inicio': start_date.strftime('%d/%m/%Y'),
                'data_fim': end_date.strftime('%d/%m/%Y'),
                'total_sessoes': general_stats[0] or 0,
                'total_zips': general_stats[1] or 0,
                'total_logs': general_stats[2] or 0,
                'total_csvs': general_stats[3] or 0,
                'total_sql': general_stats[4] or 0,
                'total_erros': general_stats[5] or 0,
                'duracao_media_min': round(general_stats[6] or 0, 2),
                'total_zips_historico': total_zips_processed,
                'total_logs_historico': total_logs_processed,
                'ultima_sessao': {
                    'inicio': last_session[0] if last_session else None,
                    'fim': last_session[1] if last_session else None,
                    'zips': last_session[2] if last_session else 0,
                    'logs': last_session[3] if last_session else 0,
                    'csvs': last_session[4] if last_session else 0,
                    'sql': last_session[5] if last_session else 0,
                    'erros': last_session[6] if last_session else 0
                } if last_session else None
            }
            
            return stats
            
        except Exception as e:
            print(f"❌ Erro ao obter estatísticas: {e}")
            return {}
    
    def print_statistics(self, days: int = 30):
        """Exibe estatísticas formatadas."""
        stats = self.get_processing_statistics(days)
        
        if not stats:
            print("❌ Não foi possível obter estatísticas.")
            return
        
        print(f"\n📊 ESTATÍSTICAS DOS ÚLTIMOS {days} DIAS")
        print("=" * 50)
        print(f"📅 Período: {stats['data_inicio']} a {stats['data_fim']}")
        print(f"🔄 Total de sessões: {stats['total_sessoes']}")
        print(f"📦 ZIPs processados: {stats['total_zips']}")
        print(f"📄 Logs processados: {stats['total_logs']}")
        print(f"📊 CSVs gerados: {stats['total_csvs']}")
        print(f"🗄️ Registros SQL: {stats['total_sql']}")
        print(f"❌ Total de erros: {stats['total_erros']}")
        print(f"⏱️ Duração média: {stats['duracao_media_min']} minutos")
        
        print(f"\n📈 HISTÓRICO TOTAL:")
        print(f"   - ZIPs processados: {stats['total_zips_historico']}")
        print(f"   - Logs processados: {stats['total_logs_historico']}")
        
        if stats['ultima_sessao']:
            print(f"\n🕐 ÚLTIMA SESSÃO:")
            last = stats['ultima_sessao']
            print(f"   - Início: {last['inicio']}")
            print(f"   - Fim: {last['fim']}")
            print(f"   - ZIPs: {last['zips']}")
            print(f"   - Logs: {last['logs']}")
            print(f"   - CSVs: {last['csvs']}")
            print(f"   - SQL: {last['sql']}")
            print(f"   - Erros: {last['erros']}")
    
    def cleanup_old_reports(self, days_to_keep: int = 30):
        """Remove relatórios antigos."""
        try:
            cutoff_date = datetime.now().timestamp() - (days_to_keep * 24 * 60 * 60)
            
            for report_file in os.listdir(self.reports_dir):
                if report_file.endswith('.csv'):
                    file_path = os.path.join(self.reports_dir, report_file)
                    if os.path.getmtime(file_path) < cutoff_date:
                        os.remove(file_path)
                        print(f"🗑️ Removido relatório antigo: {report_file}")
                        
        except Exception as e:
            print(f"❌ Erro na limpeza de relatórios: {e}") 