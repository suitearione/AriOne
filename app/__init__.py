# =============================================================================

# Caminho  : app/__init__.py

# Arquivo  : __init__.py

# Função   : Factory da aplicação Flask.

# Descrição: Inicializa extensões (db, migrate, login_manager), registra

#            Blueprints e define rota raiz. Detecta ambiente automaticamente

#            pelo nome da pasta raiz: AriOneDEV=dev, AriOne=produção.

#            IS_DEV e AMBIENTE ficam disponíveis em app.config e nos templates

#            via {{ config.IS_DEV }}.

# =============================================================================



from pathlib import Path

from flask import Flask, redirect, url_for, jsonify, request

from flask_login import current_user

from app.extensions import db, migrate, login_manager

import os



BASE_DIR = Path(__file__).resolve().parent.parent



# ── Imports de models — obrigatório para Flask-Migrate detectar as tabelas ──

from app.models.cadastros.empresa import Empresa

from app.models.usuario import Usuario

from app.models.sistema.versao  import Versao

from app.models.comercial import *

from app.models.gestao.plano_contas import PlanoContas
from app.models.gestao.patrimonio import Patrimonio
from app.models.gestao.lancamento import Lancamento
from app.models.gestao.parametros_financeiros import ParametrosFinanceiros




def create_app():

    app = Flask(

        __name__,

        template_folder=str(BASE_DIR / "templates"),

        static_folder=str(BASE_DIR / "static")

    )



    # ── Configurações ──────────────────────────────────────────────────────

    database_url = os.environ.get('DATABASE_URL', '')

    if database_url:

        if database_url.startswith('postgres://'):

            database_url = database_url.replace('postgres://', 'postgresql://', 1)

        app.config['SQLALCHEMY_DATABASE_URI'] = database_url

        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {

            'connect_args': {'sslmode': 'require'},

            'pool_recycle': 300,

            'pool_pre_ping': True

        }

    else:

        app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{BASE_DIR / 'instance' / 'arione.db'}"

    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'arione_dev_2026_secret')

    app.config['TEMPLATES_AUTO_RELOAD'] = True  # ← PAAv1: força reload de templates sem reiniciar
    app.config['DEBUG'] = True  # ← Força debug mode para reload



    # ✅ Detecção automática de ambiente
    # Local: nome da pasta raiz (AriOneDEV=dev). Render: FLASK_ENV=development=dev
    app.config['IS_DEV']    = (BASE_DIR.name == 'AriOneDEV') or (os.environ.get('FLASK_ENV') == 'development')
    app.config['AMBIENTE']  = 'Desenvolvimento' if app.config['IS_DEV'] else 'Produção'



    # ── Extensões ──────────────────────────────────────────────────────────

    db.init_app(app)

    migrate.init_app(app, db)

    login_manager.init_app(app)

    login_manager.login_view = 'auth.login'



    # ── Blueprints ─────────────────────────────────────────────────────────

    from app.auth.routes      import auth_bp

    from app.routes.setup     import setup_bp

    from app.routes.cadastros import cadastros_bp

    from app.routes.operacoes import operacoes_bp

    from app.routes.gestao    import gestao_bp

    from app.routes.financeiro import financeiro_bp

    from app.routes.fiscal    import fiscal_bp

    from app.routes.patrimonio import patrimonio_bp

    from app.routes.digital   import digital_bp

    from app.routes.relatorios import relatorios_bp

    from app.routes.sistema   import sistema_bp

    from app.routes.imprimir  import imprimir_bp

    from app.routes.developer import developer_bp

    

    

    app.register_blueprint(auth_bp)

    app.register_blueprint(setup_bp)

    app.register_blueprint(cadastros_bp)

    app.register_blueprint(operacoes_bp)

    app.register_blueprint(gestao_bp)

    app.register_blueprint(financeiro_bp)

    app.register_blueprint(fiscal_bp)

    app.register_blueprint(patrimonio_bp)

    app.register_blueprint(digital_bp)

    app.register_blueprint(relatorios_bp)

    app.register_blueprint(sistema_bp)

    app.register_blueprint(imprimir_bp)

    app.register_blueprint(developer_bp)



    # ── DEBUG: Listar todas as rotas registradas ──

    print("\n" + "="*50)

    print("AriOne: ROTAS REGISTRADAS NO FLASK:")

    for rule in app.url_map.iter_rules():

        print(f"{rule.endpoint:30} | {rule.rule}")

    print("="*50 + "\n")



    # ── Background Backup Scheduler (AriOne Automator) ──

    def start_backup_scheduler():

        import threading, time, json

        from datetime import datetime

        from app.utils.backup_manager import BackupManager



        def scheduler_loop():

            time.sleep(20) # Aguarda inicialização completa

            while True:

                try:

                    with app.app_context():

                        config_path = os.path.join(app.instance_path, 'backup_config.json')

                        if os.path.exists(config_path):

                            with open(config_path, 'r') as f: config = json.load(f)

                            now = datetime.now().strftime('%H:%M')

                            if now == config.get('horario_db'):

                                BackupManager().create_snapshot(scope='db', note='Auto DB')

                                BackupManager().auto_cleanup(limit=config.get('limite_retencao', 30))

                                time.sleep(61)

                            elif now == config.get('horario_media'):

                                BackupManager().create_snapshot(scope='media', note='Auto Media')

                                time.sleep(61)

                except: pass

                time.sleep(30)



        threading.Thread(target=scheduler_loop, daemon=True).start()



    start_backup_scheduler()



    # ── Auto-Sync do Banco de Dados ──

    # Cria tabelas no PostgreSQL (Render) ou SQLite (local)

    with app.app_context():

        db.create_all()

        # ── Auto-Seed de Versão ────────────────────────────────────────────────
        # Para lançar nova versão: atualize VERSAO_ATUAL e faça git push.
        # O Render registra automaticamente no banco ao iniciar.
        VERSAO_ATUAL = 'v2.00.02'  # ← SÓ MUDE ESTE NÚMERO A CADA RELEASE

        try:
            ja_existe = Versao.query.filter_by(numero=VERSAO_ATUAL, status='publicada').first()
            if not ja_existe:
                nova = Versao(
                    numero=VERSAO_ATUAL,
                    titulo=f'Release {VERSAO_ATUAL}',
                    status='publicada',
                    data_publicacao=datetime.now(),
                    autor='Sistema'
                )
                db.session.add(nova)
                db.session.commit()
                print(f'[AriOne] ✅ Versão {VERSAO_ATUAL} publicada no banco!')
            else:
                print(f'[AriOne] ℹ️ Versão {VERSAO_ATUAL} já existe.')
        except Exception as e:
            print(f'[AriOne] ⚠️ Erro ao registrar versão: {e}')
            db.session.rollback()

        if not database_url:

            captura_cols = [
                ('slug', 'VARCHAR(100)'),
                ('mensagem_sucesso', 'VARCHAR(250) DEFAULT "Obrigado! Entraremos em contato."')
            ]

            for col, tipo in captura_cols:

                try:

                    db.session.execute(db.text(f'ALTER TABLE capturas ADD COLUMN {col} {tipo}'))

                    db.session.commit()

                except Exception:

                    db.session.rollback()

        # Fix: ajustar coluna senha_hash para 256 chars (scrypt hash é maior que 128)

        if database_url:

            try:

                db.session.execute(db.text('ALTER TABLE usuarios ALTER COLUMN senha_hash TYPE VARCHAR(256)'))

                db.session.commit()

            except Exception:

                db.session.rollback()

            # ── Fix: colunas ausentes em op_compras_pedidos ────────────────────
            _colunas_compras = [
                ('fornecedor_id',       'INTEGER'),
                ('comprador_id',        'INTEGER'),
                ('perfil_compra',       'VARCHAR(50)'),
                ('numero',              'VARCHAR(20)'),
                ('condicoes_pagamento', 'VARCHAR(100)'),
                ('forma_pagamento_id',  'INTEGER'),
                ('valor_desconto',      'NUMERIC(16,2) DEFAULT 0'),
                ('outros_custos',       'NUMERIC(16,2) DEFAULT 0'),
                ('total_frete',         'NUMERIC(16,2) DEFAULT 0'),
                ('total_bruto',         'NUMERIC(16,2) DEFAULT 0'),
                ('total_liquido',       'NUMERIC(16,2) DEFAULT 0'),
                ('forma_envio',         'VARCHAR(50)'),
                ('ent_cep',             'VARCHAR(9)'),
                ('ent_logradouro',      'VARCHAR(150)'),
                ('ent_numero',          'VARCHAR(20)'),
                ('ent_bairro',          'VARCHAR(100)'),
                ('ent_cidade',          'VARCHAR(100)'),
                ('ent_uf',              'VARCHAR(2)'),
                ('ent_complemento',     'VARCHAR(100)'),
                ('rastreamento_api',    'VARCHAR(100)'),
                ('observacoes',         'TEXT'),
            ]
            for _col, _tipo in _colunas_compras:
                try:
                    db.session.execute(db.text(
                        f'ALTER TABLE op_compras_pedidos ADD COLUMN IF NOT EXISTS {_col} {_tipo}'
                    ))
                    db.session.commit()
                except Exception:
                    db.session.rollback()

            # ── Fix: renomear condicoes_pagamento -> condicao_pagamento (alinha model)
            try:
                db.session.execute(db.text(
                    'ALTER TABLE op_compras_pedidos RENAME COLUMN condicoes_pagamento TO condicao_pagamento'
                ))
                db.session.commit()
            except Exception:
                db.session.rollback()

            # ── Fix: colunas ausentes em clientes
            for _col, _tipo in [
                ('data_abertura',   'DATE'),
                ('genero',          'VARCHAR(50)'),
                ('site',            'VARCHAR(255)'),
                ('instagram',       'VARCHAR(100)'),
                ('origem',          'VARCHAR(50)'),
                ('categoria',       'VARCHAR(50)'),
                ('rating',          'VARCHAR(10)'),
                ('cliente_desde',   'DATE'),
                ('end_res_obs',     'VARCHAR(255)'),
                ('end_ent_obs',     'VARCHAR(255)'),
                ('prazo_pagamento', 'VARCHAR(50)'),
                ('forma_pagamento', 'VARCHAR(50)'),
                ('desconto_padrao', 'NUMERIC(5,2) DEFAULT 0'),
                ('limite_compras',  'NUMERIC(16,2) DEFAULT 0'),
                ('tabela_preco',    'VARCHAR(10)'),
                ('banco',           'VARCHAR(150)'),
                ('banco_nome',      'VARCHAR(100)'),
                ('banco_codigo',    'VARCHAR(10)'),
                ('banco_agencia',   'VARCHAR(20)'),
                ('banco_conta',     'VARCHAR(30)'),
                ('banco_tipo',      'VARCHAR(20)'),
                ('pix_chave',       'VARCHAR(150)'),
                ('bloqueio_credito','BOOLEAN DEFAULT FALSE'),
                ('motivo_bloqueio', 'VARCHAR(255)'),
                ('foto',            'VARCHAR(255)'),
            ]:
                try:
                    db.session.execute(db.text(f'ALTER TABLE clientes ADD COLUMN IF NOT EXISTS {_col} {_tipo}'))
                    db.session.commit()
                except Exception:
                    db.session.rollback()

            # ── Fix: colunas ausentes em empresas
            for _col, _tipo in [
                ('area_atuacao_resumo', 'VARCHAR(200)'),
                ('setor_atividade',     'VARCHAR(100)'),
                ('objeto_social',       'VARCHAR(50)'),
                ('logo',                'VARCHAR(255)'),
                ('tipo_pessoa',         'VARCHAR(2)'),
                ('unidade',             'VARCHAR(10)'),
                ('rg',                  'VARCHAR(20)'),
                ('ie',                  'VARCHAR(20)'),
                ('im',                  'VARCHAR(20)'),
                ('data_nascimento',     'DATE'),
                ('profissao',           'VARCHAR(100)'),
                ('pis_pasep',           'VARCHAR(15)'),
                ('email_contato',       'VARCHAR(200)'),
                ('contato_nome',        'VARCHAR(100)'),
                ('contato_tipo',        'VARCHAR(50)'),
                ('slug',                'VARCHAR(100)'),
                ('website',             'VARCHAR(200)'),
                ('instagram',           'VARCHAR(100)'),
                ('facebook',            'VARCHAR(100)'),
                ('end_fat_cep',         'VARCHAR(9)'),
                ('end_fat_logradouro',  'VARCHAR(200)'),
                ('end_fat_numero',      'VARCHAR(20)'),
                ('end_fat_complemento', 'VARCHAR(100)'),
                ('end_fat_bairro',      'VARCHAR(100)'),
                ('end_fat_cidade',      'VARCHAR(100)'),
                ('end_fat_uf',          'VARCHAR(2)'),
                ('end_fat_referencia',  'VARCHAR(200)'),
                ('end_ent_cep',         'VARCHAR(9)'),
                ('end_ent_logradouro',  'VARCHAR(200)'),
                ('end_ent_numero',      'VARCHAR(20)'),
                ('end_ent_complemento', 'VARCHAR(100)'),
                ('end_ent_bairro',      'VARCHAR(100)'),
                ('end_ent_cidade',      'VARCHAR(100)'),
                ('end_ent_uf',          'VARCHAR(2)'),
                ('end_ent_referencia',  'VARCHAR(200)'),
                ('end_cor_cep',         'VARCHAR(9)'),
                ('end_cor_logradouro',  'VARCHAR(200)'),
                ('end_cor_numero',      'VARCHAR(20)'),
                ('end_cor_complemento', 'VARCHAR(100)'),
                ('end_cor_bairro',      'VARCHAR(100)'),
                ('end_cor_cidade',      'VARCHAR(100)'),
                ('end_cor_uf',          'VARCHAR(2)'),
                ('end_cor_referencia',  'VARCHAR(200)'),
                ('data_abertura',       'DATE'),
                ('data_encerramento',   'DATE'),
                ('motivo_encerramento', 'TEXT'),
                ('regime_tributario',   'VARCHAR(50)'),
                ('natureza_juridica',   'VARCHAR(10)'),
                ('cnae_principal',      'VARCHAR(10)'),
                ('cnae_secundario',     'VARCHAR(10)'),
                ('retencao_irrf',       'VARCHAR(50)'),
                ('declaracao_ir',       'VARCHAR(50)'),
                ('nfe_serie',           'VARCHAR(10)'),
                ('nfe_ultimo_numero',   'INTEGER'),
                ('nfe_ambiente',        'VARCHAR(1)'),
                ('danfe_formato',       'VARCHAR(1)'),
            ]:
                try:
                    db.session.execute(db.text(f'ALTER TABLE empresas ADD COLUMN IF NOT EXISTS {_col} {_tipo}'))
                    db.session.commit()
                except Exception:
                    db.session.rollback()

            # ── Fix: colunas ausentes em fornecedores
            for _col, _tipo in [
                ('data_abertura',   'DATE'),
                ('contato_nome',    'VARCHAR(100)'),
                ('contato_cargo',   'VARCHAR(100)'),
                ('website',         'VARCHAR(150)'),
                ('categoria',       'VARCHAR(50)'),
                ('avaliacao',       'VARCHAR(10)'),
                ('prazo_entrega',   'INTEGER'),
                ('prazo_pagamento', 'VARCHAR(50)'),
                ('forma_pagamento', 'VARCHAR(50)'),
                ('moeda',           'VARCHAR(10)'),
                ('banco_nome',      'VARCHAR(100)'),
                ('banco_codigo',    'VARCHAR(10)'),
                ('banco_agencia',   'VARCHAR(20)'),
                ('banco_conta',     'VARCHAR(30)'),
                ('banco_tipo',      'VARCHAR(20)'),
                ('pix_tipo',        'VARCHAR(20)'),
                ('pix_chave',       'VARCHAR(150)'),
                ('is_fp',           'BOOLEAN DEFAULT FALSE'),
            ]:
                try:
                    db.session.execute(db.text(f'ALTER TABLE fornecedores ADD COLUMN IF NOT EXISTS {_col} {_tipo}'))
                    db.session.commit()
                except Exception:
                    db.session.rollback()

            # ── Fix: colunas ausentes em funcionarios
            for _col, _tipo in [
                ('rg_orgao',            'VARCHAR(20)'),
                ('rg_data_emissao',     'DATE'),
                ('pis_pasep',           'VARCHAR(20)'),
                ('nome_mae',            'VARCHAR(100)'),
                ('nome_pai',            'VARCHAR(100)'),
                ('titulo_eleitor',      'VARCHAR(20)'),
                ('reservista',          'VARCHAR(20)'),
                ('cnh',                 'VARCHAR(20)'),
                ('cnh_categoria',       'VARCHAR(10)'),
                ('tipo_sanguineo',      'VARCHAR(5)'),
                ('alergias',            'VARCHAR(255)'),
                ('estado_civil',        'VARCHAR(20)'),
                ('email_pessoal',       'VARCHAR(100)'),
                ('email_corporativo',   'VARCHAR(100)'),
                ('matricula',           'VARCHAR(20)'),
                ('data_demissao',       'DATE'),
                ('tipo_contrato',       'VARCHAR(50)'),
                ('nivel_hierarquico',   'VARCHAR(50)'),
                ('unidade_negocio',     'VARCHAR(100)'),
                ('turno',               'VARCHAR(50)'),
                ('regime_escala',       'VARCHAR(20)'),
                ('ponto_tolerancia',    'INTEGER DEFAULT 5'),
                ('aso_data',            'DATE'),
                ('aso_validade',        'DATE'),
                ('epi_entregues',       'TEXT'),
                ('salario_base',        'NUMERIC(12,2) DEFAULT 0'),
                ('peridiocidade',       'VARCHAR(20)'),
                ('banco',               'VARCHAR(100)'),
                ('tipo_conta',          'VARCHAR(50)'),
                ('agencia',             'VARCHAR(10)'),
                ('conta',               'VARCHAR(20)'),
                ('pix',                 'VARCHAR(100)'),
                ('foto',                'VARCHAR(255)'),
                ('path_documentos',     'VARCHAR(255)'),
            ]:
                try:
                    db.session.execute(db.text(f'ALTER TABLE funcionarios ADD COLUMN IF NOT EXISTS {_col} {_tipo}'))
                    db.session.commit()
                except Exception:
                    db.session.rollback()

            # ── Fix: colunas ausentes em transportadoras
            for _col, _tipo in [
                ('rntrc',               'VARCHAR(20)'),
                ('website',             'VARCHAR(150)'),
                ('modal_transporte',    'VARCHAR(100)'),
                ('tipo_servico',        'VARCHAR(100)'),
                ('prazo_entrega',       'INTEGER'),
                ('avaliacao',           'VARCHAR(1)'),
                ('coleta_origem',       'VARCHAR(3)'),
                ('entrega_final',       'VARCHAR(3)'),
                ('entregador_final',    'VARCHAR(50)'),
                ('coleta_veiculos',     'VARCHAR(100)'),
                ('entrega_veiculos',    'VARCHAR(100)'),
                ('contato_nome',        'VARCHAR(100)'),
                ('contato_cargo',       'VARCHAR(100)'),
                ('parceira_desde',      'DATE'),
                ('rotas_data',          'TEXT'),
                ('logo',                'VARCHAR(255)'),
                ('end_com_cep',         'VARCHAR(9)'),
                ('end_com_logradouro',  'VARCHAR(150)'),
                ('end_com_numero',      'VARCHAR(20)'),
                ('end_com_complemento', 'VARCHAR(100)'),
                ('end_com_bairro',      'VARCHAR(80)'),
                ('end_com_cidade',      'VARCHAR(80)'),
                ('end_com_uf',          'VARCHAR(2)'),
                ('end_ent_cep',         'VARCHAR(9)'),
                ('end_ent_logradouro',  'VARCHAR(150)'),
                ('end_ent_numero',      'VARCHAR(20)'),
                ('end_ent_complemento', 'VARCHAR(100)'),
                ('end_ent_bairro',      'VARCHAR(80)'),
                ('end_ent_cidade',      'VARCHAR(80)'),
                ('end_ent_uf',          'VARCHAR(2)'),
                ('prazo_pagamento',     'VARCHAR(50)'),
                ('forma_pagamento',     'VARCHAR(50)'),
                ('tabela_frete',        'VARCHAR(100)'),
                ('banco_nome',          'VARCHAR(100)'),
                ('banco_codigo',        'VARCHAR(10)'),
                ('banco_agencia',       'VARCHAR(20)'),
                ('banco_conta',         'VARCHAR(20)'),
                ('pix_chave',           'VARCHAR(100)'),
            ]:
                try:
                    db.session.execute(db.text(f'ALTER TABLE transportadoras ADD COLUMN IF NOT EXISTS {_col} {_tipo}'))
                    db.session.commit()
                except Exception:
                    db.session.rollback()

            # ── Fix: colunas ausentes em socios
            for _col, _tipo in [
                ('foto',                'VARCHAR(255)'),
                ('estado_civil',        'VARCHAR(30)'),
                ('nacionalidade',       'VARCHAR(50)'),
                ('profissao',           'VARCHAR(100)'),
                ('email_corporativo',   'VARCHAR(120)'),
                ('pais',                'VARCHAR(50)'),
            ]:
                try:
                    db.session.execute(db.text(f'ALTER TABLE socios ADD COLUMN IF NOT EXISTS {_col} {_tipo}'))
                    db.session.commit()
                except Exception:
                    db.session.rollback()

            # ── Fix: colunas ausentes em investidores
            for _col, _tipo in [
                ('tipo_pessoa',     'VARCHAR(2)'),
                ('nacionalidade',   'VARCHAR(50)'),
                ('estado_civil',    'VARCHAR(30)'),
                ('razao_social',    'VARCHAR(150)'),
                ('nome_fantasia',   'VARCHAR(150)'),
                ('ie',              'VARCHAR(30)'),
                ('responsavel',     'VARCHAR(150)'),
                ('cpf_responsavel', 'VARCHAR(14)'),
                ('email2',          'VARCHAR(120)'),
                ('pais',            'VARCHAR(50)'),
            ]:
                try:
                    db.session.execute(db.text(f'ALTER TABLE investidores ADD COLUMN IF NOT EXISTS {_col} {_tipo}'))
                    db.session.commit()
                except Exception:
                    db.session.rollback()

            # ── Fix: colunas ausentes em op_compras_pedidos
            for _col, _tipo in [
                ('fornecedor_id',       'INTEGER'),
                ('comprador_id',        'INTEGER'),
                ('perfil_compra',       'VARCHAR(50)'),
                ('numero',              'VARCHAR(20)'),
                ('condicao_pagamento',  'VARCHAR(100)'),
                ('forma_pagamento_id',  'INTEGER'),
                ('valor_desconto',      'NUMERIC(16,2) DEFAULT 0'),
                ('outros_custos',       'NUMERIC(16,2) DEFAULT 0'),
                ('total_frete',         'NUMERIC(16,2) DEFAULT 0'),
                ('total_bruto',         'NUMERIC(16,2) DEFAULT 0'),
                ('total_liquido',       'NUMERIC(16,2) DEFAULT 0'),
                ('forma_envio',         'VARCHAR(50)'),
                ('ent_cep',             'VARCHAR(10)'),
                ('ent_logradouro',      'VARCHAR(150)'),
                ('ent_numero',          'VARCHAR(20)'),
                ('ent_bairro',          'VARCHAR(100)'),
                ('ent_cidade',          'VARCHAR(100)'),
                ('ent_uf',              'VARCHAR(2)'),
                ('ent_complemento',     'VARCHAR(150)'),
                ('rastreamento_api',    'VARCHAR(100)'),
                ('observacoes',         'TEXT'),
            ]:
                try:
                    db.session.execute(db.text(f'ALTER TABLE op_compras_pedidos ADD COLUMN IF NOT EXISTS {_col} {_tipo}'))
                    db.session.commit()
                except Exception:
                    db.session.rollback()

            # ── Fix: colunas ausentes em comercial_formas_pagamento
            for _col, _tipo in [
                ('agrupador_operacional',  'VARCHAR(50)'),
                ('baixa_automatica',       'BOOLEAN DEFAULT FALSE'),
                ('tipo',                   'VARCHAR(50)'),
                ('condicao_pagamento',     'VARCHAR(100)'),
                ('intervalo_dias',         'INTEGER DEFAULT 0'),
                ('parcela_minima',         'NUMERIC(16,2) DEFAULT 0'),
                ('taxa_juros',             'NUMERIC(8,2) DEFAULT 0'),
                ('percentual_desconto',    'NUMERIC(8,2) DEFAULT 0'),
                ('icone',                  'VARCHAR(50)'),
                ('cor',                    'VARCHAR(20)'),
            ]:
                try:
                    db.session.execute(db.text(f'ALTER TABLE comercial_formas_pagamento ADD COLUMN IF NOT EXISTS {_col} {_tipo}'))
                    db.session.commit()
                except Exception:
                    db.session.rollback()

            # ── Fix: colunas ausentes em comercial_operadoras_financeiras
            for _col, _tipo in [
                ('nome_fantasia',               'VARCHAR(100)'),
                ('cnpj',                        'VARCHAR(20)'),
                ('site',                        'VARCHAR(255)'),
                ('email_suporte',               'VARCHAR(100)'),
                ('telefone_suporte',            'VARCHAR(20)'),
                ('taxa_debito',                 'NUMERIC(8,4) DEFAULT 0'),
                ('taxa_pix',                    'NUMERIC(8,4) DEFAULT 0'),
                ('taxa_credito_vista',          'NUMERIC(8,4) DEFAULT 0'),
                ('taxa_credito_parcelado',      'NUMERIC(8,4) DEFAULT 0'),
                ('taxa_antecipacao',            'NUMERIC(8,4) DEFAULT 0'),
                ('taxas_parcelamento',          'TEXT'),
                ('formas_pagamento_ids',        'TEXT'),
                ('formas_pagamento_detalhes',   'TEXT'),
                ('icone',                       'VARCHAR(50)'),
                ('cor',                         'VARCHAR(20)'),
            ]:
                try:
                    db.session.execute(db.text(f'ALTER TABLE comercial_operadoras_financeiras ADD COLUMN IF NOT EXISTS {_col} {_tipo}'))
                    db.session.commit()
                except Exception:
                    db.session.rollback()

            # ── Fix: colunas ausentes em cat_produtos
            for _col, _tipo in [
                ('tipo_item',               'VARCHAR(50)'),
                ('cod_barras',              'VARCHAR(14)'),
                ('cod_interno',             'VARCHAR(50)'),
                ('referencia',              'VARCHAR(50)'),
                ('origem_produto',          'VARCHAR(50)'),
                ('dim_comprimento',         'NUMERIC(10,2)'),
                ('dim_largura',             'NUMERIC(10,2)'),
                ('dim_altura',              'NUMERIC(10,2)'),
                ('tags',                    'VARCHAR(255)'),
                ('preco_varejo',            'NUMERIC(16,2) DEFAULT 0'),
                ('preco_atacado',           'NUMERIC(16,2) DEFAULT 0'),
                ('preco_promocional',       'NUMERIC(16,2) DEFAULT 0'),
                ('tipo_estoque',            'VARCHAR(20)'),
                ('saldo_reservado',         'NUMERIC(16,2) DEFAULT 0'),
                ('saldo_previsto',          'NUMERIC(16,2) DEFAULT 0'),
                ('qtd_min_varejo',          'INTEGER DEFAULT 1'),
                ('qtd_min_atacado',         'INTEGER DEFAULT 1'),
                ('deposito',                'VARCHAR(100)'),
                ('prateleira',              'VARCHAR(100)'),
                ('has_composicao',          'BOOLEAN DEFAULT FALSE'),
                ('mov_estoque_composicao',  'BOOLEAN DEFAULT FALSE'),
                ('ncm',                     'VARCHAR(10)'),
                ('cest',                    'VARCHAR(10)'),
                ('cfop',                    'VARCHAR(4)'),
                ('origem',                  'VARCHAR(1)'),
                ('cst',                     'VARCHAR(3)'),
                ('aliq_icms',               'NUMERIC(8,4) DEFAULT 0'),
                ('aliq_pis',                'NUMERIC(8,4) DEFAULT 0'),
                ('aliq_cofins',             'NUMERIC(8,4) DEFAULT 0'),
                ('aliq_ipi',                'NUMERIC(8,4) DEFAULT 0'),
                ('mva',                     'NUMERIC(8,4) DEFAULT 0'),
                ('base_st',                 'NUMERIC(8,4) DEFAULT 0'),
                ('permite_desconto',        'BOOLEAN DEFAULT FALSE'),
                ('desconto_maximo',         'NUMERIC(8,2) DEFAULT 0'),
                ('vender_sem_estoque',      'BOOLEAN DEFAULT FALSE'),
                ('exige_obs_venda',         'BOOLEAN DEFAULT FALSE'),
                ('imprimir_nfe',            'BOOLEAN DEFAULT FALSE'),
                ('grade_cores',             'TEXT'),
                ('grade_tamanhos',          'TEXT'),
                ('grade_label_adicional',   'VARCHAR(50)'),
                ('grade_valores_adicional', 'TEXT'),
                ('grade_matrix',            'TEXT'),
            ]:
                try:
                    db.session.execute(db.text(f'ALTER TABLE cat_produtos ADD COLUMN IF NOT EXISTS {_col} {_tipo}'))
                    db.session.commit()
                except Exception:
                    db.session.rollback()

            # ── Fix: colunas ausentes em cat_insumos
            for _col, _tipo in [
                ('sku',             'VARCHAR(50)'),
                ('estoque_minimo',  'NUMERIC(16,2) DEFAULT 0'),
                ('ponto_pedido',    'NUMERIC(16,2) DEFAULT 0'),
                ('conta_contabil',  'VARCHAR(20)'),
                ('centro_custo',    'VARCHAR(50)'),
                ('foto',            'VARCHAR(255)'),
            ]:
                try:
                    db.session.execute(db.text(f'ALTER TABLE cat_insumos ADD COLUMN IF NOT EXISTS {_col} {_tipo}'))
                    db.session.commit()
                except Exception:
                    db.session.rollback()

            # ── Fix: colunas ausentes em financeiro_caixas
            for _col, _tipo in [
                ('formas_pagamento_ids',      'TEXT'),
                ('formas_pagamento_detalhes', 'TEXT'),
                ('bancos_ids',                'TEXT'),
                ('operadoras_ids',            'TEXT'),
                ('responsavel',               'VARCHAR(100)'),
                ('data_fechamento',           'TIMESTAMP'),
                ('observacoes',               'TEXT'),
            ]:
                try:
                    db.session.execute(db.text(f'ALTER TABLE financeiro_caixas ADD COLUMN IF NOT EXISTS {_col} {_tipo}'))
                    db.session.commit()
                except Exception:
                    db.session.rollback()

            # ── Fix: colunas ausentes em financeiro_lancamentos
            for _col, _tipo in [
                ('numero_documento',    'VARCHAR(50)'),
                ('rateio_multiplo',     'BOOLEAN DEFAULT FALSE'),
                ('data_competencia',    'TIMESTAMP'),
                ('conta_bancaria_id',   'INTEGER'),
            ]:
                try:
                    db.session.execute(db.text(f'ALTER TABLE financeiro_lancamentos ADD COLUMN IF NOT EXISTS {_col} {_tipo}'))
                    db.session.commit()
                except Exception:
                    db.session.rollback()

            # ── Fix: colunas ausentes em sistema_licencas
            for _col, _tipo in [
                ('cnpj_cpf',            'VARCHAR(20)'),
                ('contato_master',      'VARCHAR(100)'),
                ('email_gestao',        'VARCHAR(200)'),
                ('whatsapp_gestor',     'VARCHAR(20)'),
                ('cidade',              'VARCHAR(100)'),
                ('uf',                  'VARCHAR(2)'),
                ('pais',                'VARCHAR(100)'),
                ('tipo_cobranca',       'VARCHAR(50)'),
                ('inicio_cobranca',     'DATE'),
                ('assinatura_url',      'VARCHAR(500)'),
                ('anexos_json',         'TEXT'),
                ('matriz_licenciamento','TEXT'),
            ]:
                try:
                    db.session.execute(db.text(f'ALTER TABLE sistema_licencas ADD COLUMN IF NOT EXISTS {_col} {_tipo}'))
                    db.session.commit()
                except Exception:
                    db.session.rollback()

            # ── Fix: colunas ausentes em sistema_status (Dashboard Postgres antigo)
            _status_cols = [
                ('dashboard_conta', 'BOOLEAN DEFAULT FALSE'),
                ('dashboard_modulo', 'VARCHAR(50)'),
                ('dashboard_indicador', 'VARCHAR(50)')
            ]
            for _col, _tipo in _status_cols:
                try:
                    db.session.execute(db.text(
                        f'ALTER TABLE sistema_status ADD COLUMN IF NOT EXISTS {_col} {_tipo}'
                    ))
                    db.session.commit()
                except Exception:
                    db.session.rollback()


    # Comentado para deploy no Render - seed e migrações SQLite removidas

    # with app.app_context():

    #     from app.models.cadastros import EmpresaContato

    #     from app.models.comercial.models import CanalVenda

    #     db.create_all()

    #     

    #     try:

    #         if not CanalVenda.query.first():

    #             seed_canais = [

    #                 CanalVenda(nome="WHATSAPP SUPORTE OFICIAL", tipo="WhatsApp API", status="ATIVO", departamento="Suporte N1", identificador="+55 (11) 99999-8888", api_token="EAAK_SUPORTE_999", webhook_url="https://api.arione.com/v1/webhook/chatone", ativar_ia="SIM", sla_minutos=15, mensagem_ausencia="Nosso horário de atendimento é de Seg a Sex das 08h às 18h."),

    #                 CanalVenda(nome="WEBCHAT PORTAL MATRIZ", tipo="Webchat", status="ATIVO", departamento="Comercial B2C", identificador="Widget SiteOne (JS)", api_token="EAAK_WEBCHAT_888", webhook_url="https://api.arione.com/v1/webhook/chatone", ativar_ia="SIM", sla_minutos=10, mensagem_ausencia="Nosso horário de atendimento é de Seg a Sex das 08h às 18h."),

    #                 CanalVenda(nome="INSTAGRAM DIRECT SAC", tipo="Instagram", status="QR_CODE", departamento="Geral", identificador="@arione.software", api_token="EAAK_INSTA_777", webhook_url="https://api.arione.com/v1/webhook/chatone", ativar_ia="NAO", sla_minutos=30, mensagem_ausencia="Nosso horário de atendimento é de Seg a Sex das 08h às 18h.")

    #             ]

    #             db.session.bulk_save_objects(seed_canais)

    #             db.session.commit()

    #     except Exception:

    #         db.session.rollback()

    #

    #     # Sincronização manual de colunas para SQLite (ALTER TABLE)

    #     # Comentado para deploy no Render - deve ser executado via migrations

    #     # try:

    #     #     from sqlalchemy import text

    #     #     cols = [

    #     #         ('tipo_pessoa', 'VARCHAR(2) DEFAULT "PJ"'), ('cpf', 'VARCHAR(14)'),

    #     #         ('rg', 'VARCHAR(20)'), ('data_nascimento', 'DATE'),

    #     #         ('profissao', 'VARCHAR(100)'), ('pis_pasep', 'VARCHAR(15)'),

    #     #         ('regime_tributario', 'VARCHAR(50)'), ('natureza_juridica', 'VARCHAR(10)'),

    #     #         ('cnae_principal', 'VARCHAR(10)'), ('cnae_secundario', 'VARCHAR(10)'),

    #     #         ('retencao_irrf', 'VARCHAR(50)'), ('declaracao_ir', 'VARCHAR(50)'),

    #     #         ('setor_id', 'INTEGER'), ('departamento_id', 'INTEGER'), ('cargo_id', 'INTEGER')

    #     #     ]

    #     #     for col, tipo in cols:

    #     #         try:

    #     #             db.session.execute(text(f"ALTER TABLE empresas ADD COLUMN {col} {tipo}"))

    #     #             db.session.commit()

    #     #         except Exception:

    #     #             db.session.rollback()

    #     # 

    #     #     # Sincronização para a tabela usuarios

    #     #     try:

    #     #         db.session.execute(text("ALTER TABLE usuarios ADD COLUMN usuario VARCHAR(50)"))

    #     #         db.session.commit()

    #     #     except Exception:

    #     #         db.session.rollback()

    #     # 

    #     #     # Sincronização para a tabela setores (Hierarquia HCM)

    #     #     cols_setores = [

    #     #         ('codigo', 'VARCHAR(20)'), ('sigla', 'VARCHAR(10)'),

    #     #         ('parent_id', 'INTEGER REFERENCES setores(id)')

    #     #     ]

    #     #     for col, tipo in cols_setores:

    #     #         try:

    #     #             db.session.execute(text(f"ALTER TABLE setores ADD COLUMN {col} {tipo}"))

    #     #             db.session.commit()

    #     #         except Exception:

    #     #             db.session.rollback()

    #     # 

    #     #     # Sincronização para a tabela empresas_contatos

    #     #     cols_contatos = [('setor_id', 'INTEGER'), ('departamento_id', 'INTEGER')]

    #     #     for col, tipo in cols_contatos:

    #     #         try:

    #     #             db.session.execute(text(f"ALTER TABLE empresas_contatos ADD COLUMN {col} {tipo}"))

    #     #             db.session.commit()

    #     #         except Exception:

    #     #             db.session.rollback()

    #     # 

    #     #     # Sincronização para a tabela cargos

    #     #     cols_cargos = [('codigo', 'VARCHAR(20)')]

    #     #     for col, tipo in cols_cargos:

    #     #         try:

    #     #             db.session.execute(text(f"ALTER TABLE cargos ADD COLUMN {col} {tipo}"))

    #     #             db.session.commit()

    #     #         except Exception:

    #     #             db.session.rollback()

    #     # 

    #     #     # Sincronização para a tabela centros_custo

    #     #     try:

    #     #         db.session.execute(text("ALTER TABLE centros_custo ADD COLUMN pix VARCHAR(100)"))

    #     #         db.session.commit()

    #     #     except Exception:

    #     #         db.session.rollback()

    #     # 

    #     #     # Sincronização para a tabela funcionarios

    #     #     cols_func = [

    #     #         ('rg_orgao', 'VARCHAR(20)'), ('rg_data_emissao', 'DATE'),

    #     #         ('pis_pasep', 'VARCHAR(20)'), ('nome_mae', 'VARCHAR(100)'),

    #     #         ('nome_pai', 'VARCHAR(100)'), ('titulo_eleitor', 'VARCHAR(20)'),

    #     #         ('reservista', 'VARCHAR(20)'), ('tipo_sanguineo', 'VARCHAR(5)'),

    #     #         ('alergias', 'VARCHAR(255)'), ('email_corporativo', 'VARCHAR(100)'),

    #     #         ('whatsapp', 'VARCHAR(20)'), ('matricula', 'VARCHAR(20)'),

    #     #         ('cnh', 'VARCHAR(20)'), ('cnh_categoria', 'VARCHAR(10)'),

    #     #         ('tipo_contrato', 'VARCHAR(50)'), ('status', 'VARCHAR(20)'),

    #     #         ('gestor_id', 'INTEGER'), ('nivel_hierarquico', 'VARCHAR(50)'),

    #     #         ('unidade_negocio', 'VARCHAR(100)'), ('turno', 'VARCHAR(50)'),

    #     #         ('regime_escala', 'VARCHAR(20)'), ('ponto_tolerancia', 'INTEGER'),

    #     #         ('centro_custo_id', 'INTEGER'), ('aso_data', 'DATE'),

    #     #         ('aso_validade', 'DATE'), ('epi_entregues', 'TEXT'),

    #     #         ('salario_base', 'NUMERIC'), ('peridiocidade', 'VARCHAR(20)'),

    #     #         ('banco', 'VARCHAR(100)'), ('tipo_conta', 'VARCHAR(50)'),

    #     #         ('agencia', 'VARCHAR(10)'), ('conta', 'VARCHAR(20)'),

    #     #         ('pix', 'VARCHAR(100)'), ('foto', 'VARCHAR(255)'),

    #     #         ('path_documentos', 'VARCHAR(255)'), ('usuario_id', 'INTEGER')

    #     #     ]

    #     #     for col, tipo in cols_func:

    #     #         try:

    #     #             db.session.execute(text(f"ALTER TABLE funcionarios ADD COLUMN {col} {tipo}"))

    #     #             db.session.commit()

    #     #         except Exception:

    #     #             db.session.rollback()

    #     # 

    #     #     # Sincronização para a tabela clientes

    #     #     cols_cli = [

    #     #         ('end_res_obs', 'VARCHAR(255)'), ('end_ent_obs', 'VARCHAR(255)'),

    #     #         ('limite_compras', 'NUMERIC(16, 2) DEFAULT 0.0'), ('banco', 'VARCHAR(150)'),

    #     #         ('foto', 'VARCHAR(255)')

    #     #     ]

    #     #     for col, tipo in cols_cli:

    #     #         try:

    #     #             db.session.execute(text(f"ALTER TABLE clientes ADD COLUMN {col} {tipo}"))

    #     #             db.session.commit()

    #     #         except Exception:

    #     #             db.session.rollback()

    #     # 

    #     #     # Sincronização para a tabela fornecedores

    #     #     cols_forn = [

    #     #         ('pix_tipo', 'VARCHAR(20)'), ('foto', 'VARCHAR(255)')

    #     #     ]

    #     #     for col, tipo in cols_forn:

    #     #         try:

    #     #             db.session.execute(text(f"ALTER TABLE fornecedores ADD COLUMN {col} {tipo}"))

    #     #             db.session.commit()

    #     #         except Exception:

    #     #             db.session.rollback()

    #     # 

    #     #     # Sincronização para tabelas comerciais

    #     #     cols_rev = [

    #     #         ('whatsapp', 'VARCHAR(20)'), ('foto', 'VARCHAR(255)'), 

    #     #         ('categoria', 'VARCHAR(50)'), ('tipo_revenda', 'VARCHAR(50)'), 

    #     #         ('comissao', 'FLOAT DEFAULT 0.0'), ('regiao', 'VARCHAR(100)'),

    #     #         ('rating', 'VARCHAR(10)'), ('limite_credito', 'FLOAT DEFAULT 0.0'),

    #     #         ('ativa', 'BOOLEAN DEFAULT 1'), ('created_at', 'DATETIME DEFAULT CURRENT_TIMESTAMP')

    #     #     ]

    #     #     for col, tipo in cols_rev:

    #     #         try:

    #     #             db.session.execute(text(f"ALTER TABLE comercial_revendedores ADD COLUMN {col} {tipo}"))

    #     #             db.session.commit()

    #     #         except Exception: db.session.rollback()

    #     # 

    #     #     cols_inf = [

    #     #         ('handle', 'VARCHAR(50)'), ('nicho', 'VARCHAR(50)'), ('alcance', 'INTEGER'), 

    #     #         ('seguidores', 'VARCHAR(20)'), ('whatsapp', 'VARCHAR(20)'), ('email', 'VARCHAR(100)'), 

    #     #         ('instagram', 'VARCHAR(100)'), ('plataforma', 'VARCHAR(50)'), ('foto', 'VARCHAR(255)'), 

    #     #         ('status_contrato', 'VARCHAR(20) DEFAULT "ATIVO"'),

    #     #         ('ativa', 'BOOLEAN DEFAULT 1'), ('created_at', 'DATETIME DEFAULT CURRENT_TIMESTAMP')

    #     #     ]

    #     #     for col, tipo in cols_inf:

    #     #         try:

    #     #             db.session.execute(text(f"ALTER TABLE comercial_influenciadores ADD COLUMN {col} {tipo}"))

    #     #             db.session.commit()

    #     #         except Exception: db.session.rollback()

    #     # 

    #     #     cols_est = [

    #     #         ('especialidade', 'VARCHAR(100)'), ('portfólio_url', 'VARCHAR(255)'), 

    #     #         ('whatsapp', 'VARCHAR(20)'), ('email', 'VARCHAR(100)'), ('foto', 'VARCHAR(255)'), 

    #     #         ('disponibilidade', 'VARCHAR(50)'),

    #     #         ('ativa', 'BOOLEAN DEFAULT 1'), ('created_at', 'DATETIME DEFAULT CURRENT_TIMESTAMP')

    #     #     ]

    #     #     for col, tipo in cols_est:

    #     #         try:

    #     #             db.session.execute(text(f"ALTER TABLE comercial_estilistas ADD COLUMN {col} {tipo}"))

    #     #             db.session.commit()

    #     #         except Exception: db.session.rollback()

    #     # 

    #     #     # ── SINCRONIZAÇÃO COMERCIAL E VENDAS (CANAIS DE VENDA) ──

    #     #     try:

    #     #         db.session.execute(text("ALTER TABLE comercial_vendedores ADD COLUMN canais_venda VARCHAR(255)"))

    #     #         db.session.commit()

    #     #     except Exception: db.session.rollback()

    #     # 

    #     #     try:

    #     #         db.session.execute(text("ALTER TABLE op_vendas_orcamentos ADD COLUMN canal_venda VARCHAR(100)"))

    #     #         db.session.commit()

    #     #     except Exception: db.session.rollback()

    #     # 

    #     #     try:

    #     #         db.session.execute(text("ALTER TABLE op_vendas_pedidos ADD COLUMN canal_venda VARCHAR(100)"))

    #     #         db.session.commit()

    #     #     except Exception: db.session.rollback()

    #     # 

    #     #     # ── SINCRONIZAÇÃO SERVIÇOS (CATÁLOGOS) ──

    #     #     cols_srv = [

    #     #         ('tipo_item', 'VARCHAR(2) DEFAULT "09"'), ('codigo', 'VARCHAR(50)'),

    #     #         ('observacoes', 'VARCHAR(255)'), ('preco_custo', 'FLOAT DEFAULT 0.0'),

    #     #         ('preco_venda', 'FLOAT DEFAULT 0.0'), ('qtd_minima', 'FLOAT DEFAULT 1.0'),

    #     #         ('tempo_execucao', 'VARCHAR(100)'), ('comissao', 'FLOAT DEFAULT 0.0'),

    #     #         ('descricao_detalhada', 'TEXT'), ('garantia', 'VARCHAR(100)'),

    #     #         ('validade_proposta', 'VARCHAR(100)'), ('forma_pagamento', 'VARCHAR(50)'),

    #     #         ('ncm', 'VARCHAR(10)'), ('cest', 'VARCHAR(10)'),

    #     #         ('codigo_servico', 'VARCHAR(100)')

    #     #     ]

    #     #     for col, tipo in cols_srv:

    #     #         try:

    #     #             db.session.execute(text(f"ALTER TABLE cat_servicos ADD COLUMN {col} {tipo}"))

    #     #             db.session.commit()

    #     #         except Exception: db.session.rollback()

    #     # 

    #     #     # ── SINCRONIZAÇÃO PLANO DE CONTAS (GERENCIAL) ──

    #     #     cols_pc = [

    #     #         ('grupo_gerencial', 'VARCHAR(1)'),

    #     #         ('vida_util_meses', 'INTEGER DEFAULT 0'),

    #     #         ('valor_residual_percent', 'FLOAT DEFAULT 0.0')

    #     #     ]

    #     #     for col, tipo in cols_pc:

    #     #         try:

    #     #             db.session.execute(text(f"ALTER TABLE financeiro_plano_contas ADD COLUMN {col} {tipo}"))

    #     #             db.session.commit()

    #     #         except Exception: db.session.rollback()

    #     # 

    #     # except Exception:

    #     #     pass



    # ── Context Processor para Versão do Sistema ───────────────────────

    @app.context_processor

    def inject_global_utilities():

        from app.utils.sistema_matriz import SISTEMA_MATRIZ

        from app.utils.permissoes import tem_permissao

        from datetime import datetime, date

        v = None

        try:

            from app.models.sistema.versao import Versao

            # Em DEV: mostrar última versão em DEV, ou última publicada se não houver DEV
            # Em PROD: mostrar última versão PUBLICADA
            if app.config['IS_DEV']:
                # Primeiro tenta pegar última versão em DEV
                v = Versao.query.filter_by(status='dev')\
                               .order_by(Versao.id.desc())\
                               .first()
                # Se não houver versão em DEV, pega última publicada
                if not v:
                    v = Versao.query.filter_by(status='publicada')\
                                   .order_by(Versao.data_publicacao.desc())\
                                   .first()
            else:
                v = Versao.query.filter_by(status='publicada')\
                               .order_by(Versao.data_publicacao.desc())\
                               .first()

            if v:

                suffix = " DEV" if v.status != 'publicada' and app.config['IS_DEV'] else ""

                numero = f"{v.numero}{suffix}"

                nome = "AriOne" if v.status == 'publicada' else "AriOneDEV"

            else:

                numero = "v1.0 DEV"

                nome = "AriOneDEV"

        except Exception:

            numero = "v1.0"

            nome = "AriOneDEV"

        

        try:

            from app.utils.progress import get_standardization_progress, is_ari_dev

            progress = get_standardization_progress()

            ari_dev = is_ari_dev()

        except Exception:

            progress = {}

            ari_dev = False

        

        # ── INTEGRITY PULSE GLOBAL (Cálculo Leve) ──

        try:

            from app.models.cadastros.funcionario import Funcionario

            from sqlalchemy import func

            

            issues_count = 0

            dupes = db.session.query(Funcionario.cpf).group_by(Funcionario.cpf).having(func.count(Funcionario.id) > 1).count()

            issues_count += dupes

            

            orfaos = Funcionario.query.filter(Funcionario.empresa_id == None).count()

            if orfaos > 0: issues_count += 1

            

            global_integrity = 100 - (issues_count * 10)

            if global_integrity < 0: global_integrity = 0

        except Exception:

            global_integrity = 100

        

        return dict(

            now=datetime.now,

            date=date,

            sistema_nome=nome,

            sistema_versao=numero,

            sistema_versao_num=v.numero if v else "v1.0",

            sistema_versao_suffix=" DEV" if (v and v.status != 'publicada' and app.config['IS_DEV']) or (not v) else "",

            sistema_status=v.status if v else 'dev',

            ari_progress=progress,

            is_ari_dev=ari_dev,

            global_integrity=global_integrity,

            SISTEMA_MATRIZ=SISTEMA_MATRIZ,

            tem_permissao=tem_permissao

        )



    # ── Health Check (diagnóstico no Render) ────────────────────────────────

    @app.route('/health')

    def health():

        import traceback

        checks = {}

        checks['database_url'] = app.config['SQLALCHEMY_DATABASE_URI'][:30] + '...'

        try:

            db.session.execute(db.text('SELECT 1'))

            checks['db_connection'] = 'OK'

        except Exception as e:

            checks['db_connection'] = f'ERRO: {str(e)}'

        try:

            count = Empresa.query.count()

            checks['empresas_table'] = f'OK ({count} registros)'

        except Exception as e:

            checks['empresas_table'] = f'ERRO: {str(e)}'

        return checks, 200


    @app.route('/fix-compras')
    def fix_compras():
        resultados = {}
        colunas = [
            ('numero',              'VARCHAR(20)'),
            ('fornecedor_id',       'INTEGER'),
            ('comprador_id',        'INTEGER'),
            ('perfil_compra',       'VARCHAR(50)'),
            ('condicao_pagamento',  'VARCHAR(100)'),
            ('forma_pagamento_id',  'INTEGER'),
            ('valor_desconto',      'NUMERIC(16,2) DEFAULT 0'),
            ('outros_custos',       'NUMERIC(16,2) DEFAULT 0'),
            ('total_frete',         'NUMERIC(16,2) DEFAULT 0'),
            ('total_bruto',         'NUMERIC(16,2) DEFAULT 0'),
            ('total_liquido',       'NUMERIC(16,2) DEFAULT 0'),
            ('forma_envio',         'VARCHAR(50)'),
            ('ent_cep',             'VARCHAR(9)'),
            ('ent_logradouro',      'VARCHAR(150)'),
            ('ent_numero',          'VARCHAR(20)'),
            ('ent_bairro',          'VARCHAR(100)'),
            ('ent_cidade',          'VARCHAR(100)'),
            ('ent_uf',              'VARCHAR(2)'),
            ('ent_complemento',     'VARCHAR(100)'),
            ('rastreamento_api',    'VARCHAR(100)'),
            ('observacoes',         'TEXT'),
        ]
        for col, tipo in colunas:
            try:
                db.session.execute(db.text(
                    f'ALTER TABLE op_compras_pedidos ADD COLUMN IF NOT EXISTS {col} {tipo}'
                ))
                db.session.commit()
                resultados[col] = 'OK'
            except Exception as e:
                db.session.rollback()
                resultados[col] = f'ERRO: {str(e)}'
        return jsonify(resultados), 200


    # ── Error Handler (mostra traceback no log) ───────────────────────────

    @app.errorhandler(500)

    def internal_error(e):

        import traceback

        tb = traceback.format_exc()

        print(f"\n{'='*50}\n500 ERROR TRACEBACK:\n{tb}\n{'='*50}\n")

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or \
           request.headers.get('Accept', '').find('application/json') != -1 or \
           request.is_json:
            return jsonify(success=False, error="Erro do Servidor Interno - verifique /health para diagnóstico"), 500

        return f"Internal Server Error - verifique /health para diagnóstico", 500



    # ── Rota raiz ──────────────────────────────────────────────────────────

    @app.route('/')

    def index():

        if not Empresa.query.first():

            return redirect(url_for('setup.index'))

        if not current_user.is_authenticated:

            return redirect(url_for('auth.login'))

        # ✅ Redireciona para o Módulo de Gestão (Dashboard Padrão)

        return redirect(url_for('gestao.abas'))



    return app