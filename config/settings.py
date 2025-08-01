#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configurações do Processador de Logs EDI
========================================
"""

# Configurações do Banco de Dados SQL Server
DB_CONFIG = {
    'server': '192.168.2.15',
    'database': 'SISCNTRHC',
    'username': 'SISCNTRHC',
    'password': 'CtEp@2023',
    'driver': 'ODBC Driver 18 for SQL Server',
    'trusted_connection': 'no',
    'timeout': 30,
    'charset': 'utf8',
    'encrypt': 'no',  # Desabilitar criptografia SSL
    'trust_server_certificate': 'yes'  # Confiar em certificados auto-assinados
}

# Configurações do Compartilhamento SMB
# O sistema irá processar apenas arquivos com padrão 'ConsoleEDI_' nesta pasta
SMB_CONFIG = {
    'host': '192.168.2.15',
    'share': 'Servico Integra',
    'username': 'rodrigo.cesarino',
    'password': 'R0drigo@147',
    'mount_point': '/mnt/smb_integra',
    'timeout': 30,
    'retry_attempts': 3
}

# Configurações Locais
LOCAL_CONFIG = {
    'temp_dir': 'temp_unzipped_logs',
    'output_dir': 'processed_csvs',
    'reports_dir': 'reports',
    'table_name': 'EDI_LOGS',
    'local_db': 'processed_files.db',
    'log_level': 'INFO',
    'max_file_size_mb': 100
}

# Configurações de Processamento
PROCESSING_CONFIG = {
    'log_file_pattern': 'ConsoleEDI_',  # Apenas arquivos que começam com 'ConsoleEDI_'
    'log_file_extension': '.Log',
    'zip_file_extension': '.Log.zip',
    'separator_line': '-' * 70,
    'batch_size': 1000,
    'max_workers': 4,
    'retry_failed_files': True,
    'max_retries': 3,
    'strict_pattern_matching': True,  # Força verificação rigorosa do padrão
    'enable_reprocessing': True,  # Permite reprocessamento quando arquivo é modificado
    'check_file_changes': True  # Verifica mudanças no tamanho/timestamp do arquivo
}

# Configurações de Filtros CSV
CSV_FILTER_CONFIG = {
    'keywords': ['Upload de FTP', 'Envio de e-mail por SMTP'],
    'case_sensitive': False,
    'include_headers': True,
    'output_encoding': 'utf-8'
}

# Configurações de Limpeza
CLEANUP_CONFIG = {
    'keep_csv_days': 7,
    'keep_reports_days': 30,
    'cleanup_temp_files': True,
    'cleanup_empty_dirs': True
}

# Configurações de Relatórios
REPORT_CONFIG = {
    'auto_generate_daily': True,
    'auto_generate_weekly': False,
    'include_error_details': True,
    'report_format': 'csv',
    'timezone': 'America/Sao_Paulo'
}

# Configurações de Logging
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'file': 'edi_processor.log',
    'max_size_mb': 10,
    'backup_count': 5
}

# Configurações de Performance
PERFORMANCE_CONFIG = {
    'max_memory_usage_mb': 512,
    'chunk_size': 1000,
    'enable_parallel_processing': True,
    'max_concurrent_files': 4
}

# Configurações de Segurança
SECURITY_CONFIG = {
    'encrypt_passwords': False,
    'mask_sensitive_data': True,
    'log_sensitive_operations': False,
    'session_timeout_minutes': 30
}
