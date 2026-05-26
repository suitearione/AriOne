# /app.py
# ----------------- BLOCO: INTEGRAÇÃO MODULAR DO SISTEMA -----------------
print(">>> APP.PY CARREGADO <<<")

import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

from flask import Flask, redirect, url_for
from config import Config
from app.extensions import db, migrate, login_manager

def create_app(config_class=Config):
    # ANOTAÇÃO DE BLOCO: Fábrica do AriOne v1.04.04
    app = Flask(__name__)
    app.config.from_object(config_class)

    # ANOTAÇÃO DE LINHA: Configuração do Banco de Dados
    # Usa DATABASE_URL do ambiente (Render) ou SQLite local
    database_url = os.getenv('DATABASE_URL', 'sqlite:///arione_dev.db')
    # Render usa postgres://, mas SQLAlchemy prefere postgresql://
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://')
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url



    # ----------------- BLOCO: VÍNCULO DE EXTENSÕES ----------------- 
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    
    login_manager.login_view = 'auth.login'
    login_manager.login_message = "Acesso restrito. Por favor, faça login."
    login_manager.login_message_category = "info"

    # ----------------- BLOCO: IMPORTAÇÃO DE MÓDULOS (BLUEPRINTS) ----------------- 
    from routes.auth import auth_bp
    from routes.home_routes import home_bp
    from routes.dashboard import dashboard_bp 
    from routes.painel import painel_bp
    from routes.empresa import empresa_bp
    from app.routes.admgeralOLD import admgeral_bp
    from routes.comercialbk import comercial_bp
    from routes.catalogo import catalogo_bp
    from routes.estoque import estoque_bp
    from routes.producao import producao_bp
    from routes.vendas import venda_bp
    from routes.compras import compra_bp
    from routes.financeiro import financeiro_bp
    from routes.fiscal import fiscal_bp
    from routes.expedicao import expedicao_bp
    from routes.marketing import marketing_bp
    from routes.pessoalOLD import pessoal_bp
    from routes.relatorios import relatorios_bp
    from routes.conexoes import conexoes_bp

    # ----------------- BLOCO: REGISTRO DE ROTAS ATIVAS ----------------- 
    app.register_blueprint(auth_bp)
    app.register_blueprint(home_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(painel_bp)
    app.register_blueprint(empresa_bp)
    app.register_blueprint(admgeral_bp)
    app.register_blueprint(comercial_bp)
    app.register_blueprint(catalogo_bp)
    app.register_blueprint(estoque_bp)
    app.register_blueprint(producao_bp)
    app.register_blueprint(venda_bp)
    app.register_blueprint(compra_bp)
    app.register_blueprint(financeiro_bp)
    app.register_blueprint(fiscal_bp)
    app.register_blueprint(expedicao_bp)
    app.register_blueprint(marketing_bp)
    app.register_blueprint(pessoal_bp)
    app.register_blueprint(relatorios_bp)
    app.register_blueprint(conexoes_bp)

    # ----------------- BLOCO: CONTEXTO GLOBAL JINJA ----------------- 
    @app.context_processor
    def inject_global_vars():
        from datetime import datetime
        return {'agora': datetime.now()}

    # ----------------- BLOCO: CARREGADOR DE USUÁRIO ----------------- 
    @login_manager.user_loader
    def load_user(user_id):
        from models.admgeral.usuarios import Usuario
        return Usuario.query.get(int(user_id))

    # ----------------- BLOCO: TESTE DE DEPURAÇÃO (RAIO-X) ----------------- 
    # ANOTAÇÃO DE LINHA: Força o terminal a listar as rotas ao iniciar
    print("\n--- MAPEAMENTO DE ROTAS ATIVAS ---")
    for rule in app.url_map.iter_rules():
        print(f"Rota: {rule.endpoint} -> {rule}")
    print("----------------------------------\n")
    
    return app