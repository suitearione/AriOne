# ============================================================
# 🟪 CONFIGURAÇÃO DO BANCO DE DADOS – ARIONE
# ============================================================

# Importa o módulo os, para criar caminhos seguros e flexíveis
import os

# 🔹 Caminho base do projeto (raiz onde o app está)
basedir = os.path.abspath(os.path.dirname(__file__))

# 🔹 URI de conexão com o SQLite
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, '..', 'arione.db')

# 🔹 Desativa alertas desnecessários do SQLAlchemy
SQLALCHEMY_TRACK_MODIFICATIONS = False

# 🔹 Define a chave secreta do Flask (necessária para sessões e segurança)
SECRET_KEY = 'chave_super_secreta_arione'
