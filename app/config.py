# ===============================================================
# ⚙️ ARIONEDEV – config.py
# 📂 Local: /AriOneDEV/config.py
# ---------------------------------------------------------------
# RESPONSABILIDADES:
# - Carregar variáveis de ambiente (.env)
# - Definir configurações globais do Flask (Chave Secreta, Banco de Dados, etc.)
# ===============================================================

# 📦 IMPORTAÇÕES NECESSÁRIAS
from dotenv import load_dotenv # Função para carregar .env
from app.config import Config                 # Módulo para interagir com o sistema operacional

# ===============================================================
# 🔹 CARREGAMENTO DE VARIÁVEIS DE AMBIENTE
# ===============================================================
load_dotenv() # Carrega as variáveis do arquivo .env

# ===============================================================
# ⚙️ CLASSE DE CONFIGURAÇÃO (Padrão Flask recomendado)
# ===============================================================
class Config:
    """
    Classe base para configurações do aplicativo AriOne.
    Todas as configurações do Flask e extensões devem estar aqui.
    """

    # -----------------------------------------------------------
    # 🔑 CONFIGURAÇÕES DE SEGURANÇA
    # -----------------------------------------------------------
    # Chave Secreta para assinar cookies e sessões. Lê do .env
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'fallback-super-secreto' 
    # Token interno para rotas de dev. Lê do .env
    TOKEN_SISTEMA = os.environ.get('TOKEN_SISTEMA') or 'arione123' 

    # -----------------------------------------------------------
    # 🗄️ CONFIGURAÇÕES DO BANCO DE DADOS (SQLAlchemy)
    # -----------------------------------------------------------
    # Define o caminho absoluto para o projeto
    BASE_DIR = os.path.abspath(os.path.dirname(__file__)) 
    # Define o caminho para o arquivo do banco de dados SQLite
    DB_PATH = os.path.join(BASE_DIR, "arione_dev.db") 

    # String de conexão com o banco de dados (SQLite)
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{DB_PATH}" 
    # Desabilita o rastreamento de modificações para otimização
    SQLALCHEMY_TRACK_MODIFICATIONS = False 

    # ── CONFIGURAÇÕES DE UPLOAD ──
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")

# ==================== FIM DO ARQUIVO ===========================