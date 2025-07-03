import os
import re
import csv
from config.settings import LOCAL_CONFIG, PROCESSING_CONFIG

def convert_log_to_csv(log_file):
    """Converte arquivo de log para CSV."""
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

def filter_csv(csv_file):
    """Gera um novo CSV apenas com linhas contendo 'Upload de FTP' ou 'Envio de e-mail por SMTP'."""
    filtered_file = csv_file.replace('.csv', '_filtrado.csv')
    palavras_chave = ['Upload de FTP', 'Envio de e-mail por SMTP']
    try:
        with open(csv_file, 'r', encoding='utf-8') as infile, \
             open(filtered_file, 'w', newline='', encoding='utf-8') as outfile:
            reader = csv.reader(infile)
            writer = csv.writer(outfile)
            header = next(reader)
            writer.writerow(header)
            for row in reader:
                if any(palavra in row[1] for palavra in palavras_chave):
                    writer.writerow(row)
        print(f"  ✓ CSV filtrado gerado: {os.path.basename(filtered_file)}")
        return filtered_file
    except Exception as e:
        print(f"  ✗ Erro ao filtrar {csv_file}: {e}")
        return None
