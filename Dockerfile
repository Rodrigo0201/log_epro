# Usar Python 3.11 slim como base
FROM python:3.11-slim

# Definir variáveis de ambiente
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV ODBCSYSINI=/etc
ENV ODBCINI=/etc/odbc.ini

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    curl \
    wget \
    gnupg2 \
    # cifs-utils e mount removidos - não mais necessários para FTP \
    && rm -rf /var/lib/apt/lists/*

# Adicionar chave Microsoft e repositório SQL Server (método correto para Debian 12)
RUN wget -qO- https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor -o /usr/share/keyrings/microsoft-archive-keyring.gpg \
    && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/microsoft-archive-keyring.gpg] https://packages.microsoft.com/debian/12/prod bookworm main" > /etc/apt/sources.list.d/mssql-release.list

# Instalar driver ODBC do SQL Server (removendo pacotes conflitantes primeiro)
RUN apt-get update \
    && apt-get remove -y unixodbc unixodbc-dev libodbc2 libodbccr2 libodbcinst2 unixodbc-common \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql18 unixodbc unixodbc-dev \
    && ln -sfn /opt/microsoft/msodbcsql18/lib64/libmsodbcsql-18.*.so.* /opt/microsoft/msodbcsql18/lib64/libmsodbcsql-18.so \
    && rm -rf /var/lib/apt/lists/*

# Definir diretório de trabalho
WORKDIR /app


# Copiar requirements primeiro para aproveitar cache do Docker
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY . .

# Criar diretório de logs e de montagem SMB
RUN mkdir -p logs /mnt/smb_integra

# Configurar ODBC apenas para o driver 18
RUN echo "[ODBC Driver 18 for SQL Server]" > /etc/odbcinst.ini \
    && echo "Description=Microsoft ODBC Driver 18 for SQL Server" >> /etc/odbcinst.ini \
    && echo "Driver=/opt/microsoft/msodbcsql18/lib64/libmsodbcsql-18.so" >> /etc/odbcinst.ini \
    && echo "UsageCount=1" >> /etc/odbcinst.ini

# Comando padrão
CMD ["python", "cli/main.py"] 