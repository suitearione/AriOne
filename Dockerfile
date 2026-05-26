# =============================================================================
# Dockerfile para AriOne ERP
# =============================================================================
FROM python:3.11-slim

# Define diretório de trabalho
WORKDIR /app

# Instala dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copia requirements e instala dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia código da aplicação
COPY . .

# Cria diretório para logs
RUN mkdir -p logs

# Cria diretório instance para banco de dados
RUN mkdir -p instance

# Define variáveis de ambiente
ENV FLASK_APP=app.app:create_app
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1

# Expõe porta
EXPOSE 5000

# Comando de inicialização
CMD ["gunicorn", "--config", "gunicorn.conf.py", "app.app:create_app()"]
