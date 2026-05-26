# =============================================================================
# Configuração do Gunicorn para Produção AriOne
# =============================================================================

import multiprocessing
import os

# Bind - Endereço e porta onde o servidor vai escutar
# Use 0.0.0.0 para aceitar conexões externas
bind = "0.0.0.0:5000"

# Workers - Número de processos workers (recomendado: 2-4 x CPUs)
workers = multiprocessing.cpu_count() * 2 + 1

# Worker Class - Tipo de worker (sync, gevent, eventlet)
worker_class = "sync"

# Threads - Número de threads por worker
threads = 2

# Timeout - Tempo máximo para processar uma requisição (segundos)
timeout = 120

# Keepalive - Tempo para manter conexões persistentes
keepalive = 5

# Max Requests - Reinicia workers após N requisições (previne memory leaks)
max_requests = 1000
max_requests_jitter = 50

# Preload App - Carrega o app antes de forking workers (economiza memória)
preload_app = True

# Access Log - Log de acessos
accesslog = "logs/gunicorn_access.log"

# Error Log - Log de erros
errorlog = "logs/gunicorn_error.log"

# Log Level - Nível de log (debug, info, warning, error, critical)
loglevel = "info"

# Daemon - Rodar como processo background (quando não usando systemd)
daemon = False

# PID File - Arquivo com o PID do processo principal
pidfile = "gunicorn.pid"

# User e Group - Usuário e grupo para rodar o serviço (Linux apenas)
# user = "www-data"
# group = "www-data"

# Raw Environment - Variáveis de ambiente
raw_env = [
    'FLASK_ENV=production',
    'FLASK_DEBUG=0'
]

# Limite de requisições
limit_request_line = 4096
limit_request_fields = 100
limit_request_field_size = 8190
