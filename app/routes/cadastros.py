# =============================================================================
# Caminho  : app/routes/cadastros.py
# Arquivo  : cadastros.py
# Função   : Rotas de cadastro — Empresa, Sócios, Investidores, Clientes,
#            Fornecedores, Transportadoras, Funcionários e Motoristas.
# Descrição: Gerencia criação e edição via POST com todos os campos dos models.
#            Empresas nunca são excluídas — apenas encerradas (ativa=False)
#            para preservar histórico. Upload de documentos em
#            static/uploads/<entidade>/<id>/. Demais entidades seguem padrão
#            de inativação quando o model estiver disponível.
#            A aba ativa é lida via query string ?aba=<id>, compatível
#            com o macro gerar_abas_arione. Rota principal em /cadastros/.
# =============================================================================

import os
from datetime import date, datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, Response, make_response, session
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app.models.cadastros.empresa import Empresa, EmpresaContato
from app.models.cadastros.socio import Socio, SocioEmpresa
from app.models.cadastros.investidor import Investidor, InvestidorEmpresa
from app.models.cadastros.funcionario import Funcionario, Setor, Cargo
from app.models.cadastros.cliente import Cliente
from app.models.cadastros.fornecedor import Fornecedor
from app.models.cadastros.motorista import Motorista
from app.models.comercial.models import Revendedor, Influenciador, Estilista, Ministerio, ParceriaMinisterial, TabelaPreco, TabelaPrecoItem, PerfilVenda
from app.models.sistema.parametro import ParametroSistema
from app.models.cadastros.transportadora import Transportadora
from app.models.catalogos import Marca, Categoria, Subcategoria, UnidadeMedida, Etiqueta, Insumo, Acessorio, Embalagem, MateriaPrima, Produto, Servico, Deposito, DepositoPrateleira, CorCatalogo, TamanhoCatalogo, GradeModelo, AtributoCatalogo, TipoMateriaPrima
from app.models import PlanoContas, CentroCusto
import json, csv, io
from app import db
from app.utils.progress import is_ari_dev, get_matrix_progress

cadastros_bp = Blueprint('cadastros', __name__, url_prefix='/cadastros')

@cadastros_bp.route('/api/debug/sync-db')
def debug_sync_db():
    from sqlalchemy import text
    columns = [
        ('modal_transporte', 'VARCHAR(100)'),
        ('tipo_servico', 'VARCHAR(100)'),
        ('prazo_entrega', 'INTEGER'),
        ('avaliacao', 'VARCHAR(1)'),
        ('contato_nome', 'VARCHAR(100)'),
        ('contato_cargo', 'VARCHAR(100)'),
        ('parceira_desde', 'DATE'),
        ('end_com_cep', 'VARCHAR(9)'),
        ('end_com_logradouro', 'VARCHAR(150)'),
        ('end_com_numero', 'VARCHAR(20)'),
        ('end_com_complemento', 'VARCHAR(100)'),
        ('end_com_bairro', 'VARCHAR(80)'),
        ('end_com_cidade', 'VARCHAR(80)'),
        ('end_com_uf', 'VARCHAR(2)'),
        ('end_ent_cep', 'VARCHAR(9)'),
        ('end_ent_logradouro', 'VARCHAR(150)'),
        ('end_ent_numero', 'VARCHAR(20)'),
        ('end_ent_complemento', 'VARCHAR(100)'),
        ('end_ent_bairro', 'VARCHAR(80)'),
        ('end_ent_cidade', 'VARCHAR(80)'),
        ('end_ent_uf', 'VARCHAR(2)'),
        ('prazo_pagamento', 'VARCHAR(50)'),
        ('forma_pagamento', 'VARCHAR(50)'),
        ('tabela_frete', 'VARCHAR(100)'),
        ('banco_nome', 'VARCHAR(100)'),
        ('banco_codigo', 'VARCHAR(10)'),
        ('banco_agencia', 'VARCHAR(20)'),
        ('banco_conta', 'VARCHAR(20)'),
        ('pix_chave', 'VARCHAR(100)')
    ]
    logs = []
    for col_name, col_type in columns:
        try:
            db.session.execute(text(f"ALTER TABLE transportadoras ADD COLUMN {col_name} {col_type}"))
            db.session.commit()
            logs.append(f"Coluna {col_name} OK")
        except Exception as e:
            db.session.rollback()
            logs.append(f"Erro {col_name}: {str(e)}")
    return "<br>".join(logs)

# ── Comercial: Ministérios e Parcerias ────────────────────────────────────
from sqlalchemy import text

# Comentado para deploy no Render - migração SQLite não funciona em produção
# @cadastros_bp.before_app_request
# def setup_parametros():
#     """Auto-migração para a tabela de parâmetros."""
#     try:
#         with db.engine.begin() as conn:
#             conn.execute(text("""
#                 CREATE TABLE IF NOT EXISTS sistema_parametros (
#                     id INTEGER PRIMARY KEY,
#                     chave VARCHAR(50) UNIQUE NOT NULL,
#                     valor VARCHAR(255),
#                     descricao TEXT,
#                     grupo VARCHAR(50)
#                 )
#             """))
#             conn.execute(text("""
#                 CREATE TABLE IF NOT EXISTS cat_depositos (
#                     id INTEGER PRIMARY KEY,
#                     nome VARCHAR(100) NOT NULL,
#                     sigla VARCHAR(20),
#                     endereco VARCHAR(255),
#                     tipo VARCHAR(50) DEFAULT 'proprio',
#                     ativa BOOLEAN DEFAULT 1,
#                     created_at DATETIME DEFAULT CURRENT_TIMESTAMP
#                 )
#             """))
#             conn.execute(text("""
#                 CREATE TABLE IF NOT EXISTS cat_depositos_prateleiras (
#                     id INTEGER PRIMARY KEY,
#                     deposito_id INTEGER NOT NULL,
#                     nome VARCHAR(50) NOT NULL,
#                     ativa BOOLEAN DEFAULT 1,
#                     FOREIGN KEY (deposito_id) REFERENCES cat_depositos(id)
#                 )
#             """))
#             conn.execute(text("""
#                 CREATE TABLE IF NOT EXISTS cat_atributos (
#                     id INTEGER PRIMARY KEY,
#                     nome VARCHAR(100) UNIQUE NOT NULL,
#                     descricao VARCHAR(255),
#                     ativa BOOLEAN DEFAULT 1
#                 )
#             """))
#             conn.execute(text("""
#                 CREATE TABLE IF NOT EXISTS cat_materiaprima_tipos (
#                     id INTEGER PRIMARY KEY,
#                     nome VARCHAR(100) UNIQUE NOT NULL,
#                     ativa BOOLEAN DEFAULT 1
#                 )
#             """))
#             conn.execute(text("""
#                 CREATE TABLE IF NOT EXISTS sistema_status (
#                     id INTEGER PRIMARY KEY,
#                     nome VARCHAR(50) NOT NULL,
#                     tipo VARCHAR(50) NOT NULL,
#                     cor VARCHAR(20) DEFAULT '#2980B9',
#                     icone VARCHAR(50) DEFAULT 'fas fa-circle',
#                     ordem INTEGER DEFAULT 0,
#                     ativa BOOLEAN DEFAULT 1,
#                     created_at DATETIME DEFAULT CURRENT_TIMESTAMP
#                 )
#             """))
#             # ── Auto-Migração Inteligente: cat_produtos ──
#             result = conn.execute(text("PRAGMA table_info(cat_produtos)"))
#             cols_existentes = [row[1] for row in result]
#             if 'composicao' not in cols_existentes:
#                 try: conn.execute(text('ALTER TABLE cat_produtos ADD COLUMN composicao JSON'))
#                 except: pass
#             if 'grade_id' not in cols_existentes:
#                 try: conn.execute(text('ALTER TABLE cat_produtos ADD COLUMN grade_id INTEGER REFERENCES cat_grades_modelos(id)'))
#                 except: pass
#             if 'grade_cores' not in cols_existentes:
#                 try: conn.execute(text('ALTER TABLE cat_produtos ADD COLUMN grade_cores JSON'))
#                 except: pass
#             if 'grade_tamanhos' not in cols_existentes:
#                 try: conn.execute(text('ALTER TABLE cat_produtos ADD COLUMN grade_tamanhos JSON'))
#                 except: pass
#             if 'grade_label_adicional' not in cols_existentes:
#                 try: conn.execute(text('ALTER TABLE cat_produtos ADD COLUMN grade_label_adicional VARCHAR(50)'))
#                 except: pass
#             if 'grade_valores_adicional' not in cols_existentes:
#                 try: conn.execute(text('ALTER TABLE cat_produtos ADD COLUMN grade_valores_adicional JSON'))
#                 except: pass
#             if 'cod_interno' not in cols_existentes:
#                 try: conn.execute(text('ALTER TABLE cat_produtos ADD COLUMN cod_interno VARCHAR(50)'))
#                 except: pass
#             if 'referencia' not in cols_existentes:
#                 try: conn.execute(text('ALTER TABLE cat_produtos ADD COLUMN referencia VARCHAR(100)'))
#                 except: pass
#             if 'modelo' not in cols_existentes:
#                 try: conn.execute(text('ALTER TABLE cat_produtos ADD COLUMN modelo VARCHAR(100)'))
#                 except: pass
#             if 'grade_matrix' not in cols_existentes:
#                 try: conn.execute(text('ALTER TABLE cat_produtos ADD COLUMN grade_matrix JSON'))
#                 except: pass
#             if 'origem_produto' not in cols_existentes:
#                 try: conn.execute(text('ALTER TABLE cat_produtos ADD COLUMN origem_produto VARCHAR(50)'))
#                 except: pass
#             if 'regra_cod_interno' not in cols_existentes:
#                 try: conn.execute(text('ALTER TABLE cat_produtos ADD COLUMN regra_cod_interno VARCHAR(20)'))
#                 except: pass
#             if 'tipo_material_id' not in cols_existentes:
#                 try: conn.execute(text('ALTER TABLE cat_produtos ADD COLUMN tipo_material_id INTEGER'))
#                 except: pass
#             if 'categoria_id' not in cols_existentes:
#                 try: conn.execute(text('ALTER TABLE cat_produtos ADD COLUMN categoria_id INTEGER'))
#                 except: pass
#             if 'subcategoria_id' not in cols_existentes:
#                 try: conn.execute(text('ALTER TABLE cat_produtos ADD COLUMN subcategoria_id INTEGER'))
#                 except: pass
#             if 'has_composicao' not in cols_existentes:
#                 try: conn.execute(text('ALTER TABLE cat_produtos ADD COLUMN has_composicao BOOLEAN DEFAULT 0'))
#                 except: pass
#             if 'fornecedor_id' not in cols_existentes:
#                 try: conn.execute(text('ALTER TABLE cat_produtos ADD COLUMN fornecedor_id INTEGER'))
#                 except: pass
# 
#             # ── Auto-Migração Inteligente: cat_materiaprima ──
#             result_mp = conn.execute(text("PRAGMA table_info(cat_materiaprima)"))
#             cols_mp = [row[1] for row in result_mp]
#             if 'tipo_id' not in cols_mp:
#                 try: conn.execute(text('ALTER TABLE cat_materiaprima ADD COLUMN tipo_id INTEGER'))
#                 except: pass
#             # ── Auto-Migração Inteligente: fornecedores ──
#             result_for = conn.execute(text("PRAGMA table_info(fornecedores)"))
#             cols_for = [row[1] for row in result_for]
#             if 'is_fp' not in cols_for:
#                 try: conn.execute(text('ALTER TABLE fornecedores ADD COLUMN is_fp BOOLEAN DEFAULT 0'))
#                 except: pass
# 
#             # ── Auto-Migração Inteligente: Vendas (Nº Documento) ──
#             res_orc = conn.execute(text("PRAGMA table_info(op_vendas_orcamentos)"))
#             cols_orc = [row[1] for row in res_orc]
#             if 'numero' not in cols_orc:
#                 try: conn.execute(text('ALTER TABLE op_vendas_orcamentos ADD COLUMN numero VARCHAR(20)'))
#                 except: pass
#             
#             res_ped = conn.execute(text("PRAGMA table_info(op_vendas_pedidos)"))
#             cols_ped = [row[1] for row in res_ped]
#             if 'numero' not in cols_ped:
#                 try: conn.execute(text('ALTER TABLE op_vendas_pedidos ADD COLUMN numero VARCHAR(20)'))
#                 except: pass
# 
#             # ── DIAGNÓSTICO TEMPORÁRIO ──
#             with open(r'c:\AriOneDEV\brain\da801964-c686-458e-9b7d-456cee1bd16e\scratch\db_log.txt', 'w') as f:
#                 f.write(f"cat_produtos cols: {cols_existentes}\n")
#                 f.write(f"fornecedores cols: {cols_for}\n")
# 
#     except Exception as ex_mig:
#         with open(r'c:\AriOneDEV\brain\da801964-c686-458e-9b7d-456cee1bd16e\scratch\db_log.txt', 'a') as f:
#             f.write(f"MIGRATION ERROR: {str(ex_mig)}\n")

@cadastros_bp.route('/parametros/salvar', methods=['POST'])
@login_required
def salvar_parametros():
    try:
        # Suporte a JSON (AJAX) ou Form convencional
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form.to_dict()

        grupo = data.get('grupo_config')
        
        # Salva todos os parâmetros enviados
        for chave, valor in data.items():
            if chave == 'grupo_config': continue
            # Converte valores booleanos ou específicos para string
            val_str = '1' if valor is True or str(valor).lower() in ['true', 'on', '1'] else str(valor)
            if str(valor).lower() in ['false', 'off', '0']: val_str = '0'
            
            ParametroSistema.set_valor(chave, val_str, grupo=grupo)
        
        # Tratamento especial para checkboxes faltantes (só para request.form)
        if not request.is_json:
            if grupo == 'comercial' and 'ativar_ministerio' not in request.form:
                ParametroSistema.set_valor('ativar_ministerio', '0', grupo='comercial')
                
            if grupo == 'produtos':
                for key in ['PRODUTO_ESTOQUE_NEGATIVO', 'PRODUTO_AVISO_MINIMO', 'PRODUTO_EAN_AUTO', 'PRODUTO_CODINT_SYNC_SKU']:
                    if key not in request.form:
                        ParametroSistema.set_valor(key, '0', grupo='produtos')

            if grupo == 'vendas':
                for key in ['usar_sequencia_automatica_orc', 'usar_sequencia_automatica_ped', 'reiniciar_anual']:
                    if key not in request.form:
                        ParametroSistema.set_valor(key, '0', grupo='vendas')

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.is_json:
            return jsonify({'success': True, 'message': 'Parâmetros salvos com sucesso!'})
            
        flash('Parâmetros salvos com sucesso!', 'success')
    except Exception as e:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'message': str(e)}), 500
        flash(f'Erro ao salvar parâmetros: {str(e)}', 'danger')
    
    return redirect(url_for('cadastros.abas', aba='parametros'))

@cadastros_bp.route('/parametros/get')
@login_required
def get_parametros():
    # Retorna todos os parâmetros do sistema para evitar falhas de sincronização
    # caso algum parâmetro tenha sido criado com grupo=None ou grupo diferente.
    params = ParametroSistema.query.all()
    data = {p.chave: p.valor for p in params}
    
    # 🛡️ AriOne Fallback/Integrity: Garante valores iniciais padronizados caso não existam
    defaults = {
        'ult_orcamento': '5348',
        'ult_pedido': '8210',
        'ult_cotacao': '7281',
        'ult_pedido_compra': '8942',
        'usar_sequencia_automatica_orc': '1',
        'usar_sequencia_automatica_ped': '1',
        'incremento': '1',
        'pref_orc': 'ORV-',
        'pref_ped': 'PV-',
        'reiniciar_anual': '0'
    }
    for chave, def_val in defaults.items():
        val = data.get(chave)
        if val is None or val == '':
            data[chave] = def_val
            # Aproveita para persistir o valor correto no banco
            try:
                grupo_param = 'vendas' if 'orcamento' in chave or 'pedido' in chave else 'compras'
                ParametroSistema.set_valor(chave, def_val, grupo=grupo_param)
            except: pass

    return jsonify(data)

@cadastros_bp.route('/cards/comercial/ministerios', methods=['GET', 'POST'])
@login_required
def card_ministerios():
    try:
        # Comentado para deploy no Render - migração SQLite não funciona em produção
        # # Auto-Migração Inteligente
        # with db.engine.begin() as conn:
        #     result = conn.execute(text("PRAGMA table_info(comercial_ministerios)"))
        #     cols_existentes = [row[1] for row in result]
        #     for col, spec in [
        #         ('email', 'VARCHAR(100)'), ('whatsapp', 'VARCHAR(20)'), ('registro', 'VARCHAR(50)'), ('foto', 'VARCHAR(255)'),
        #         ('tipo', 'VARCHAR(50)'), ('ativa', 'BOOLEAN DEFAULT 1')
        #     ]:
        #         if col not in cols_existentes:
        #             try: conn.execute(text(f'ALTER TABLE comercial_ministerios ADD COLUMN {col} {spec}'))
        #             except: pass
        pass

        if request.method == 'POST':
            min_id = request.form.get('id')
            if min_id:
                ministerio = Ministerio.query.get(min_id)
            else:
                ministerio = Ministerio()

            ministerio.nome = request.form.get('nome')
            ministerio.lider = request.form.get('lider') # Corrigido: era responsavel
            ministerio.registro = request.form.get('registro')
            ministerio.whatsapp = request.form.get('whatsapp')
            ministerio.email = request.form.get('email')
            ministerio.tipo = request.form.get('categoria')
            
            # Upload de Foto / Brasão
            foto = request.files.get('foto')
            if foto and _allowed(foto.filename):
                filename = secure_filename(f"min_{datetime.now().strftime('%Y%H%M%S')}_{foto.filename}")
                pasta = os.path.join('static', 'uploads', 'ministerios')
                os.makedirs(pasta, exist_ok=True)
                foto.save(os.path.join(pasta, filename))
                ministerio.foto = f"uploads/ministerios/{filename}"

            db.session.add(ministerio)
            db.session.commit()
            flash('Ministério salvo com sucesso!', 'success')
            return render_template('cadastros/cards/comercial/ministerios.html', ministerios=Ministerio.query.all())

        ministerios = Ministerio.query.all()
        return render_template('cadastros/cards/comercial/ministerios.html', ministerios=ministerios)
    except Exception as e:
        db.session.rollback()
        return f"Erro Crítico no Card Ministérios: {str(e)}", 500

@cadastros_bp.route('/cards/comercial/parcerias', methods=['GET', 'POST'])
@login_required
def card_parcerias():
    try:
        # Comentado para deploy no Render - migração SQLite não funciona em produção
        # # Auto-Migração Inteligente (Pilar Integridade)
        # with db.engine.begin() as conn:
        #     # Verifica colunas existentes
        #     result = conn.execute(text("PRAGMA table_info(comercial_parcerias_ministeriais)"))
        #     cols_existentes = [row[1] for row in result]
        #     
        #     # Colunas necessárias segundo o modelo
        #     cols_necessarias = [
        #         ('ministerio_id', 'INTEGER'),
        #         ('valor', 'FLOAT DEFAULT 0.0'), 
        #         ('frequencia', 'VARCHAR(50)'),
        #         ('tipo_cobranca', 'VARCHAR(50)'),
        #         ('data_assinatura', 'DATE'),
        #         ('data_inicio', 'DATE'),
        #         ('data_fim', 'DATE'),
        #         ('anexos_json', 'TEXT'),
        #         ('created_at', 'DATETIME')
        #     ]
        #     
        #     for col, spec in cols_necessarias:
        #         if col not in cols_existentes:
        #             try:
        #                 conn.execute(text(f'ALTER TABLE comercial_parcerias_ministeriais ADD COLUMN {col} {spec}'))
        #             except: pass
        pass

        if request.method == 'POST':
            parc_id = request.form.get('id')
            if parc_id:
                parceria = ParceriaMinisterial.query.get(parc_id)
            else:
                parceria = ParceriaMinisterial()

            parceria.titulo = request.form.get('nome')
            val_str = request.form.get('valor', '0').replace('R$', '').replace('.', '').replace(',', '.').strip()
            parceria.valor = float(val_str) if val_str else 0.0
            parceria.frequencia = request.form.get('frequencia')
            parceria.tipo_cobranca = request.form.get('tipo_cobranca')
            parceria.data_assinatura = _parse_date(request.form.get('data_assinatura'))
            parceria.data_inicio = _parse_date(request.form.get('data_inicio'))
            parceria.data_fim = _parse_date(request.form.get('data_fim'))
            
            # Para descrição, guardamos o parceiro se necessário (lógica atual do grid)
            parceiro = request.form.get('parceiro')
            tipo = request.form.get('tipo')
            parceria.descricao = f"Tipo: {tipo} | Parceiro: {parceiro}"

            # 🛡️ Gestão de Anexos (Pilar Integridade AriOne)
            # Recupera anexos já existentes para não sobrescrever
            caminhos_existentes = []
            if parceria.anexos_json:
                try:
                    caminhos_existentes = json.loads(parceria.anexos_json)
                    if not isinstance(caminhos_existentes, list):
                        caminhos_existentes = []
                except:
                    caminhos_existentes = []

            # Processa novos uploads
            novos_arquivos = request.files.getlist('anexos')
            for arq in novos_arquivos:
                if arq and _allowed(arq.filename):
                    filename = secure_filename(f"cont_{datetime.now().strftime('%Y%H%M%S')}_{arq.filename}")
                    pasta = os.path.join('static', 'uploads', 'contratos')
                    os.makedirs(pasta, exist_ok=True)
                    arq.save(os.path.join(pasta, filename))
                    caminhos_existentes.append(f"uploads/contratos/{filename}")
            
            # Salva a lista consolidada (Antigos + Novos)
            parceria.anexos_json = json.dumps(caminhos_existentes)

            db.session.add(parceria)
            db.session.commit()
            flash('Acordo/Parceria salvo com sucesso!', 'success')
            # Puxa fornecedores para o seletor de Parceiro
            fornecedores = Fornecedor.query.order_by(Fornecedor.razao_social).all()
            return render_template('cadastros/cards/comercial/parcerias.html', 
                                   parcerias=ParceriaMinisterial.query.all(),
                                   fornecedores=fornecedores)
        
        parcerias = ParceriaMinisterial.query.all()
        fornecedores = Fornecedor.query.order_by(Fornecedor.razao_social).all()
        return render_template('cadastros/cards/comercial/parcerias.html', 
                               parcerias=parcerias, 
                               fornecedores=fornecedores)
    except Exception as e:
        db.session.rollback()
        return f"Erro Crítico no Card Parcerias: {str(e)}", 500



# (Rotas de Tabela de Preços migradas para operacoes.py)

# ── Upload ─────────────────────────────────────────────────────────────────
UPLOAD_BASE = os.path.join('static', 'uploads', 'empresas')
ALLOWED_EXT = {'pdf', 'png', 'jpg', 'jpeg', 'doc', 'docx', 'xls', 'xlsx'}

def _allowed(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXT

def _pasta_empresa(empresa_id):
    pasta = os.path.join(UPLOAD_BASE, str(empresa_id))
    os.makedirs(pasta, exist_ok=True)
    return pasta

def _parse_date(valor):
    """Converte string 'YYYY-MM-DD' para date, ou None se vazio."""
    try:
        return date.fromisoformat(valor) if valor else None
    except ValueError:
        return None


# ── Abas de Cadastro (tela principal) ──────────────────────────────────────
# ATENÇÃO: rota /<aba> removida — usava path param que capturava rotas de
#          outros blueprints (ex: /cadastros/compras ia para cadastros em vez
#          de operacoes). Agora usa query string ?aba= igual ao operacoes.py.
@cadastros_bp.route('/', methods=['GET', 'POST'])
@cadastros_bp.route('', methods=['GET', 'POST'])
@cadastros_bp.route('/abas', methods=['GET', 'POST'])
def abas():
    # Comentado para deploy no Render - migração SQLite não funciona em produção
    # # 🛡️ Auto-Migração Inteligente AriOne (Pilar Integridade)
    # try:
    #     with db.engine.begin() as conn:
    #         from sqlalchemy import text
    #         result = conn.execute(text("PRAGMA table_info(empresas)"))
    #         cols_existentes = [row[1] for row in result]
    #         for col in ['end_fat_referencia', 'end_ent_referencia', 'end_cor_referencia']:
    #             if col not in cols_existentes:
    #                 try:
    #                     conn.execute(text(f'ALTER TABLE empresas ADD COLUMN {col} VARCHAR(200)'))
    #                 except: pass
    # except Exception as e:
    #     print(f"Erro na auto-migração de empresas (abas): {e}")
    pass

    abas_disponiveis = [
        {'id': 'empresa',            'label': 'Empresa',              'icon': 'business'},
        {'id': 'catalogos',          'label': 'Catálogos',            'icon': 'menu_book'},
        {'id': 'comercial',          'label': 'Comercial',            'icon': 'storefront'},
        {'id': 'pessoas',            'label': 'Pessoas',              'icon': 'group'},
        {'id': 'parametros',         'label': 'Parâmetros',           'icon': 'tune'},
    ]
    ids_validos = [a['id'] for a in abas_disponiveis]
    aba_ativa = request.args.get('aba', 'empresa')
    if aba_ativa not in ids_validos:
        aba_ativa = 'empresa'

    empresas_lista = Empresa.query.order_by(Empresa.razao_social).all()

    return render_template(
        'cadastros/abas_cadastros.html',
        abas=abas_disponiveis,
        aba_ativa=aba_ativa,
        empresas_lista=empresas_lista,
        ParametroSistema=ParametroSistema,
        get_matrix_progress=get_matrix_progress,
        is_ari_dev=is_ari_dev
    )


@cadastros_bp.route('/check-duplicate', methods=['POST'])
@login_required
def check_duplicate():
    """
    Endpoint genérico para verificação de duplicidade AriOne.
    Recebe: model_name, field_name, value, exclude_id
    """
    model_name = request.form.get('model')
    field_name = request.form.get('field')
    value = request.form.get('value', '').strip()
    exclude_id = request.form.get('exclude_id')

    if not model_name or not field_name or not value:
        return jsonify(duplicate=False)

    try:
        from app.models.catalogos import (MateriaPrima, Produto, Servico, Insumo, Acessorio, 
                                          Embalagem, Categoria, Marca, UnidadeMedida, Deposito, 
                                          CorCatalogo, TamanhoCatalogo, Etiqueta, GradeModelo, ModeloCatalogo)
        models_map = {
            'Empresa': Empresa,
            'Socio': Socio,
            'Investidor': Investidor,
            'Setor': Setor,
            'Cargo': Cargo,
            'MateriaPrima': MateriaPrima,
            'Produto': Produto,
            'Servico': Servico,
            'Insumo': Insumo,
            'Acessorio': Acessorio,
            'Embalagem': Embalagem,
            'Categoria': Categoria,
            'Marca': Marca,
            'UnidadeMedida': UnidadeMedida,
            'Deposito': Deposito,
            'CorCatalogo': CorCatalogo,
            'TamanhoCatalogo': TamanhoCatalogo,
            'Etiqueta': Etiqueta,
            'GradeModelo': GradeModelo,
            'ModeloCatalogo': ModeloCatalogo
        }
        
        model_class = models_map.get(model_name)
        if not model_class:
            return jsonify(duplicate=False)

        query = model_class.query.filter(getattr(model_class, field_name) == value)
        if exclude_id and exclude_id != 'new' and exclude_id != 'None':
            query = query.filter(model_class.id != int(exclude_id))
        
        exists = query.first() is not None
        return jsonify(duplicate=exists)
    except Exception as e:
        return jsonify(duplicate=False, error=str(e))


@cadastros_bp.route('/branding', methods=['GET', 'POST'])
@login_required
def form_branding():
    from flask import session
    # Busca a empresa da sessão ou a primeira disponível
    emp_id = session.get('empresa_id')
    empresa = None
    if emp_id:
        empresa = Empresa.query.get(emp_id)
    
    if not empresa:
        empresa = Empresa.query.first()
    
    if request.method == 'POST':
        # Se não existe nenhuma empresa, cria uma básica para suporte à logo
        if not empresa:
            empresa = Empresa(razao_social="Minha Empresa")
            db.session.add(empresa)
            db.session.flush()
        
        logo_file = request.files.get('logo_file')
        if logo_file and logo_file.filename != '':
            # Caminho absoluto na RAIZ do projeto
            logo_dir = os.path.abspath(os.path.join('static', 'img', 'logo'))
            if not os.path.exists(logo_dir):
                os.makedirs(logo_dir, exist_ok=True)
            
            ext = logo_file.filename.rsplit('.', 1)[1].lower()
            nome_logo = f"logo-empresa-{empresa.id}.{ext}"
            caminho_logo = os.path.join(logo_dir, nome_logo)
            
            logo_file.save(caminho_logo)
            empresa.logo = nome_logo
            db.session.commit()
            
            # Atualiza sessão global
            session['empresa_id'] = empresa.id
            session['nome_empresa'] = empresa.razao_social
            session['logo_empresa'] = f"img/logo/{nome_logo}"
            session.modified = True
            
            flash('Identidade Visual atualizada com sucesso!', 'success')
            return redirect(url_for('cadastros.form_branding'))

    return render_template('cadastros/cards/parametros/form_branding.html', empresa=empresa)


# ── Formulário de Empresa ───────────────────────────────────────────────────
@cadastros_bp.route('/empresa/form', methods=['GET', 'POST'])
@cadastros_bp.route('/empresa/form/<int:id>', methods=['GET', 'POST'])
def form_empresa(id=None):
    # Comentado para deploy no Render - migração SQLite não funciona em produção
    # # 🛡️ Auto-Migração Inteligente AriOne (Pilar Integridade)
    # try:
    #     with db.engine.begin() as conn:
    #         from sqlalchemy import text
    #         result = conn.execute(text("PRAGMA table_info(empresas)"))
    #         cols_existentes = [row[1] for row in result]
    #         for col in ['end_fat_referencia', 'end_ent_referencia', 'end_cor_referencia']:
    #             if col not in cols_existentes:
    #                 try:
    #                     conn.execute(text(f'ALTER TABLE empresas ADD COLUMN {col} VARCHAR(200)'))
    #                 except: pass
    # except Exception as e:
    #     print(f"Erro na auto-migração de empresas: {e}")
    pass

    empresa        = Empresa.query.get(id) if id else None
    empresas_lista = Empresa.query.order_by(Empresa.razao_social).all()
    
    # Busca Estrutura Organizacional para as abas
    setores_lista       = Setor.query.filter_by(parent_id=None).order_by(Setor.nome).all()
    departamentos_lista = Setor.query.filter(Setor.parent_id != None).order_by(Setor.nome).all()
    cargos_lista        = Cargo.query.order_by(Cargo.nome).all()

    docs = []
    if empresa:
        pasta = _pasta_empresa(empresa.id)
        if os.path.exists(pasta):
            import json
            for f in os.listdir(pasta):
                if _allowed(f):
                    doc_meta = {}
                    meta_path = os.path.join(pasta, f + '.json')
                    if os.path.exists(meta_path):
                        with open(meta_path, 'r', encoding='utf-8') as mf:
                            doc_meta = json.load(mf)
                    
                    docs.append({
                        'nome_real': f,
                        'nome_limpo': doc_meta.get('nome_original', f),
                        'ext': f.split('.')[-1].lower(),
                        'tipo': doc_meta.get('tipo', 'Outro Documento')
                    })
    
    if request.method == 'POST':
        if empresa is None:
            empresa = Empresa()

        # ── Identificação ──
        empresa.razao_social        = request.form.get('razao_social', '').strip()
        empresa.nome_fantasia       = request.form.get('nome_fantasia', '').strip() or None
        empresa.area_atuacao_resumo = request.form.get('area_atuacao', '').strip() or None
        empresa.objeto_social       = request.form.get('objeto_social', '').strip() or None

        # ── Alocação Organizacional ──
        empresa.setor_id           = request.form.get('setor_id') or None
        empresa.departamento_id    = request.form.get('departamento_id') or None
        empresa.cargo_id           = request.form.get('cargo_id') or None
        empresa.setor_atividade     = request.form.get('setor_atividade', '').strip() or None
        # ── Validação Proativa (CNPJ Único) ──
        novo_cnpj = request.form.get('cnpj', '').strip() or None
        if novo_cnpj:
            existente = Empresa.query.filter(Empresa.cnpj == novo_cnpj).filter(Empresa.id != id).first()
            if existente:
                flash(f"O CNPJ '{novo_cnpj}' já está cadastrado para a empresa '{existente.razao_social}'.", "danger")
                return redirect(url_for('cadastros.form_empresa', id=id) if id else url_for('cadastros.form_empresa'))
        empresa.cnpj = novo_cnpj

        empresa.cpf                 = request.form.get('cpf', '').strip() or None
        empresa.tipo_pessoa         = request.form.get('tipo_pessoa', 'PJ').strip()
        empresa.ie                  = request.form.get('ie', '').strip() or None
        empresa.im                  = request.form.get('im', '').strip() or None
        empresa.telefone            = request.form.get('telefone', '').strip() or None
        empresa.whatsapp            = request.form.get('whatsapp', '').strip() or None
        empresa.email               = request.form.get('email', '').strip() or None
        empresa.email_contato       = request.form.get('email_contato', '').strip() or None
        empresa.contato_nome        = request.form.get('contato_nome', '').strip() or None
        empresa.contato_tipo        = request.form.get('contato_tipo', '').strip() or None

        # ── Dados Fiscais ──
        empresa.regime_tributario = request.form.get('regime_tributario', '').strip() or None
        empresa.natureza_juridica = request.form.get('natureza_juridica', '').strip() or None
        empresa.cnae_principal    = request.form.get('cnae_principal', '').strip() or None
        empresa.cnae_secundario   = request.form.get('cnae_secundario', '').strip() or None
        empresa.profissao         = request.form.get('profissao', '').strip() or None
        empresa.pis_pasep         = request.form.get('pis_pasep', '').strip() or None
        empresa.retencao_irrf     = request.form.get('retencao_irrf', '').strip() or None
        empresa.declaracao_ir     = request.form.get('declaracao_ir', '').strip() or None
        
        # NF-e
        empresa.nfe_serie         = request.form.get('nfe_serie', '').strip() or None
        empresa.nfe_ultimo_numero = request.form.get('nfe_ultimo_numero') or None
        empresa.nfe_ambiente      = request.form.get('nfe_ambiente', '').strip() or None
        empresa.danfe_formato     = request.form.get('danfe_formato', '').strip() or None

        # ── Digital & Redes Sociais ──
        empresa.website   = request.form.get('website', '').strip() or None
        empresa.instagram = request.form.get('instagram', '').strip() or None
        empresa.facebook  = request.form.get('facebook', '').strip() or None

        # ── Validação Proativa de Domínio (Slug) ──
        nova_slug = request.form.get('slug', '').strip() or None
        if nova_slug:
            slug_existe = Empresa.query.filter(Empresa.slug == nova_slug).filter(Empresa.id != id).first()
            if slug_existe:
                flash(f"O domínio '{nova_slug}' já está em uso pela empresa '{slug_existe.razao_social}'. Escolha outro domínio.", "danger")
                return redirect(url_for('cadastros.form_empresa', id=id) if id else url_for('cadastros.form_empresa'))
        empresa.slug = nova_slug

        # ── Endereços (Fat, Ent, Cor) ──
        for prefixo in ['fat', 'ent', 'cor']:
            for campo in ['cep', 'logradouro', 'numero', 'complemento', 'bairro', 'cidade', 'uf', 'referencia']:
                valor = request.form.get(f'end_{prefixo}_{campo}', '').strip() or None
                setattr(empresa, f'end_{prefixo}_{campo}', valor)

        # ── Ciclo de Vida & Dados PF ──
        empresa.data_abertura   = _parse_date(request.form.get('data_abertura', ''))
        empresa.data_nascimento = _parse_date(request.form.get('data_nascimento', ''))
        empresa.rg              = request.form.get('rg', '').strip() or None

        try:
            db.session.add(empresa)
            db.session.flush()

            # ── Salvar Contatos Extras (Aba Contato) ──
            nomes     = request.form.getlist('c_nome[]')
            cargos    = request.form.getlist('c_cargo[]')
            whats     = request.form.getlist('c_whats[]')
            emails    = request.form.getlist('c_email[]')
            setores   = request.form.getlist('c_setor_id[]')
            deptos    = request.form.getlist('c_depto_id[]')

            # Limpa contatos antigos e reinclui (estratégia simples e eficaz para sync)
            EmpresaContato.query.filter_by(empresa_id=empresa.id).delete()
            for i in range(len(nomes)):
                if nomes[i].strip():
                    novo_c = EmpresaContato(
                        empresa_id=empresa.id,
                        nome=nomes[i].strip(),
                        cargo=cargos[i].strip() if i < len(cargos) else None,
                        whatsapp=whats[i].strip() if i < len(whats) else None,
                        email=emails[i].strip() if i < len(emails) else None,
                        setor_id=int(setores[i]) if (i < len(setores) and setores[i] and setores[i].isdigit()) else None,
                        departamento_id=int(deptos[i]) if (i < len(deptos) and deptos[i] and deptos[i].isdigit()) else None
                    )
                    db.session.add(novo_c)

            # ── Salvar Logo da Empresa (CORREÇÃO DE CAMINHO RAIZ) ──
            logo_file = request.files.get('logo_file')
            if logo_file and logo_file.filename != '':
                # Caminho absoluto na RAIZ do projeto
                logo_dir = os.path.abspath(os.path.join('static', 'img', 'logo'))
                if not os.path.exists(logo_dir):
                    os.makedirs(logo_dir, exist_ok=True)
                
                ext = logo_file.filename.rsplit('.', 1)[1].lower()
                nome_logo = f"logo-empresa-{empresa.id}.{ext}"
                caminho_logo = os.path.join(logo_dir, nome_logo)
                
                logo_file.save(caminho_logo)
                empresa.logo = nome_logo

            # ── Salvar Documentos ──
            for arq in request.files.getlist('documentos'):
                if arq and arq.filename and _allowed(arq.filename):
                    arq.save(os.path.join(_pasta_empresa(empresa.id),
                                          secure_filename(arq.filename)))

            db.session.commit()
            flash('Empresa salva com sucesso!', 'success')
            return redirect(url_for('cadastros.form_empresa', id=empresa.id))

        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao salvar: {str(e)}', 'danger')

    # ── Documentos já enviados ──
    docs = []
    if empresa and empresa.id:
        pasta = _pasta_empresa(empresa.id)
        if os.path.isdir(pasta):
            docs = [{'nome': f, 'ext': f.rsplit('.', 1)[-1].lower()}
                    for f in sorted(os.listdir(pasta))]

    return render_template(
        'cadastros/cards/empresa/form_empresa.html',
        empresa=empresa,
        empresas_lista=empresas_lista,
        setores_lista=setores_lista,
        departamentos_lista=departamentos_lista,
        cargos_lista=cargos_lista,
        docs=docs
    )


# ── Encerrar Empresa ────────────────────────────────────────────────────────
@cadastros_bp.route('/empresa/cards/encerrar/<int:id>', methods=['POST'])
def encerrar_empresa(id):
    empresa = Empresa.query.get_or_404(id)
    if not empresa.ativa:
        flash('Esta empresa já está encerrada.', 'warning')
        return redirect(url_for('cadastros.cards.form_empresa', id=id))
    try:
        empresa.ativa               = False
        empresa.data_encerramento   = date.today()
        empresa.motivo_encerramento = request.form.get('motivo', '').strip()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': True, 'message': 'Empresa encerrada com sucesso!'})
        db.session.commit()
        flash(f'Empresa "{empresa.razao_social}" encerrada.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao encerrar: {str(e)}', 'danger')
    return redirect(url_for('cadastros.cards.form_empresa', id=id))


# ── Reativar Empresa ────────────────────────────────────────────────────────
@cadastros_bp.route('/empresa/cards/reativar/<int:id>', methods=['POST'])
def reativar_empresa(id):
    empresa = Empresa.query.get_or_404(id)
    try:
        empresa.ativa             = True
        empresa.data_encerramento = None
        db.session.commit()
        flash(f'Empresa "{empresa.razao_social}" reativada com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao reativar: {str(e)}', 'danger')
    return redirect(url_for('cadastros.cards.form_empresa', id=id))


# ── Gateway de Módulos (Nível 1) ──────────────────────────────────────────
@cadastros_bp.route('/card/gateway/modulos')
@login_required
def gateway_modulos_cadastro():
    return render_template('cadastros/cards/form_gateway_modulos_cadastro.html')


# ── Gateways de Relatórios (Nível 2) ───────────────────────────────────────

@cadastros_bp.route('/card/gateway/relatorios')
@login_required
def gateway_relatorios():
    return render_template('cadastros/cards/form_gateway_relatorios.html')

@cadastros_bp.route('/card/gateway/catalogos')
@login_required
def gateway_rel_catalogos():
    return render_template('cadastros/cards/form_gateway_rel_catalogos.html')

@cadastros_bp.route('/card/gateway/comercial')
@login_required
def gateway_rel_comercial():
    return render_template('cadastros/cards/form_gateway_rel_comercial.html')

@cadastros_bp.route('/card/gateway/pessoas', methods=['GET', 'POST'])
@login_required
def gateway_rel_pessoas():
    resp = make_response(render_template('cadastros/cards/form_gateway_rel_pessoas.html'))
    resp.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate'
    return resp

@cadastros_bp.route('/card/gateway/parametros')
@login_required
def gateway_rel_parametros():
    return render_template('cadastros/cards/form_gateway_rel_parametros.html', is_modal=True)


@cadastros_bp.route('/card/parametros/venda')
@login_required
def card_parametros_venda():
    return render_template('cadastros/cards/parametros/form_par_vendas.html')


@cadastros_bp.route('/card/parametros/compra')
@login_required
def card_parametros_compra():
    return render_template('cadastros/cards/parametros/form_par_compras.html')

@cadastros_bp.route('/parametro-financeiro')
@login_required
def card_parametros_financeiro():
    from app.models.gestao.parametros_financeiros import ParametrosFinanceiros
    empresa_id = getattr(current_user, 'empresa_id', None)
    
    # Auto-Migração para a nova tabela
    try:
        with db.engine.begin() as conn:
            db.create_all()
    except Exception:
        pass
        
    q_pc = PlanoContas.query  
    q_cc = CentroCusto.query  
    
    if empresa_id:
        q_pc = q_pc.filter_by(empresa_id=empresa_id)
        q_cc = q_cc.filter_by(empresa_id=empresa_id)
        
    lista_planos = q_pc.order_by(PlanoContas.codigo).all()
    lista_centros = q_cc.order_by(CentroCusto.codigo).all()
    p = ParametrosFinanceiros.query.filter_by(empresa_id=empresa_id).first() if empresa_id else None
    
    return render_template(
        'cadastros/cards/parametros/form_par_financeiro.html',
        planos_conta=lista_planos,
        centros_custo=lista_centros,
        p=p
    )


@cadastros_bp.route('/card/parametros/producao')
@login_required
def card_parametros_producao():
    return render_template('cadastros/cards/parametros/form_par_producao.html')


@cadastros_bp.route('/card/parametros/fiscal')
@login_required
def card_parametros_fiscal():
    return render_template('cadastros/cards/parametros/form_par_fiscal.html')


@cadastros_bp.route('/card/parametros/comercial')
@login_required
def card_parametros_comercial():
    return render_template('cadastros/cards/parametros/form_par_comercial.html')


@cadastros_bp.route('/card/parametros/produto')
@login_required
def card_parametros_produto():
    return render_template('cadastros/cards/parametros/form_par_produtos.html')


@cadastros_bp.route('/card/parametros/status')
@login_required
def card_status_workflow():
    from app.models.sistema.status import StatusWorkflow
    from sqlalchemy import text
    
    # Comentado para deploy no Render - migração SQLite não funciona em produção
    # # 🛡️ Auto-Migração Inteligente AriOne (Pilar Integridade)
    # try:
    #     with db.engine.begin() as conn:
    #         result = conn.execute(text("PRAGMA table_info(sistema_status)"))
    #         cols = [row[1] for row in result]
    #         if 'dashboard_conta' not in cols:
    #             conn.execute(text("ALTER TABLE sistema_status ADD COLUMN dashboard_conta BOOLEAN DEFAULT 0"))
    #         if 'dashboard_modulo' not in cols:
    #             conn.execute(text("ALTER TABLE sistema_status ADD COLUMN dashboard_modulo VARCHAR(50)"))
    #         if 'dashboard_indicador' not in cols:
    #             conn.execute(text("ALTER TABLE sistema_status ADD COLUMN dashboard_indicador VARCHAR(50)"))
    # except Exception as e:
    #     print(f"Erro na migração de status: {e}")
    pass

    status_lista = StatusWorkflow.query.order_by(
        StatusWorkflow.dashboard_modulo, 
        StatusWorkflow.tipo, 
        StatusWorkflow.ordem
    ).all()
    return render_template('cadastros/cards/parametros/form_status_workflow.html', status_lista=status_lista)

@cadastros_bp.route('/card/parametros/status/salvar', methods=['POST'])
@login_required
def salvar_status_workflow():
    from app.models.sistema.status import StatusWorkflow
    try:
        status_id = request.form.get('id')
        nome = request.form.get('nome', '').upper().strip()
        tipo = request.form.get('tipo', 'VENDAS').upper()
        
        if not nome:
            return jsonify({'success': False, 'message': 'O nome do status é obrigatório.'}), 400

        if status_id and status_id.isdigit():
            status = StatusWorkflow.query.get(int(status_id))
            if not status:
                status = StatusWorkflow()
        else:
            status = StatusWorkflow()
            
        status.nome = nome
        status.tipo = tipo
        status.cor = request.form.get('cor', '#2980B9')
        status.icone = request.form.get('icone', 'fas fa-circle')
        
        try:
            status.ordem = int(request.form.get('ordem', 0))
        except:
            status.ordem = 0
            
        status.ativa = request.form.get('ativa') == 'on' or request.form.get('ativa') == 'true'
        
        # 📊 Integração Dashboard
        status.dashboard_conta = request.form.get('dashboard_conta') == 'on'
        status.dashboard_modulo = request.form.get('dashboard_modulo')
        status.dashboard_indicador = request.form.get('dashboard_indicador')
        
        db.session.add(status)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Status salvo com sucesso!'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Erro ao salvar status: {str(e)}'}), 500

@cadastros_bp.route('/card/parametros/status/excluir/<int:id>', methods=['POST'])
@login_required
def excluir_status_workflow(id):
    from app.models.sistema.status import StatusWorkflow
    status = StatusWorkflow.query.get_or_404(id)
    db.session.delete(status)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Status removido!'})

@cadastros_bp.route('/card/parametros/status/seed', methods=['POST'])
@login_required
def seed_status_workflow():
    from app.models.sistema.status import StatusWorkflow
    try:
        data = [
            # ORÇAMENTOS
            {'nome': 'AG. APROVAÇÃO', 'tipo': 'ORÇAMENTO DE VENDA', 'cor': '#F39C12', 'icone': 'fas fa-clock', 'ordem': 1, 'dashboard_modulo': 'ORCAMENTOS', 'dashboard_indicador': 'Ag. Aprovação', 'dashboard_conta': True},
            {'nome': 'APROVADO', 'tipo': 'ORÇAMENTO DE VENDA', 'cor': '#27AE60', 'icone': 'fas fa-check-double', 'ordem': 2, 'dashboard_modulo': 'ORCAMENTOS', 'dashboard_indicador': 'Aprovados', 'dashboard_conta': True},
            {'nome': 'REPROVADO', 'tipo': 'ORÇAMENTO DE VENDA', 'cor': '#E74C3C', 'icone': 'fas fa-thumbs-down', 'ordem': 3, 'dashboard_modulo': 'ORCAMENTOS', 'dashboard_indicador': 'Reprovados', 'dashboard_conta': True},
            {'nome': 'CANCELADO', 'tipo': 'ORÇAMENTO DE VENDA', 'cor': '#475569', 'icone': 'fas fa-times-circle', 'ordem': 4, 'dashboard_modulo': 'ORCAMENTOS', 'dashboard_indicador': 'Reprovados', 'dashboard_conta': True},

            # VENDAS
            {'nome': 'AGUARDANDO', 'tipo': 'PEDIDO DE VENDA', 'cor': '#64748B', 'icone': 'fas fa-hourglass', 'ordem': 1, 'dashboard_modulo': 'VENDAS', 'dashboard_indicador': 'Aguardando', 'dashboard_conta': True},
            {'nome': 'EM PRODUÇÃO', 'tipo': 'PEDIDO DE VENDA', 'cor': '#E67E22', 'icone': 'fas fa-industry', 'ordem': 2, 'dashboard_modulo': 'VENDAS', 'dashboard_indicador': 'Em Produção', 'dashboard_conta': True},
            {'nome': 'FINALIZADO', 'tipo': 'PEDIDO DE VENDA', 'cor': '#27AE60', 'icone': 'fas fa-check-circle', 'ordem': 3, 'dashboard_modulo': 'VENDAS', 'dashboard_indicador': 'Finalizados', 'dashboard_conta': True},
            {'nome': 'ATRASADO', 'tipo': 'PEDIDO DE VENDA', 'cor': '#C0392B', 'icone': 'fas fa-exclamation-triangle', 'ordem': 4, 'dashboard_modulo': 'VENDAS', 'dashboard_indicador': 'Atrasados', 'dashboard_conta': True},
            {'nome': 'CANCELADO', 'tipo': 'PEDIDO DE VENDA', 'cor': '#475569', 'icone': 'fas fa-ban', 'ordem': 5, 'dashboard_modulo': 'VENDAS', 'dashboard_indicador': 'Cancelados', 'dashboard_conta': True},

            # COMPRAS
            {'nome': 'AG. AUTORIZAÇÃO', 'tipo': 'PEDIDO DE COMPRA', 'cor': '#8E44AD', 'icone': 'fas fa-user-lock', 'ordem': 1, 'dashboard_modulo': 'COMPRAS', 'dashboard_indicador': 'Ag. Autorização', 'dashboard_conta': True},
            {'nome': 'AG. ENTREGA', 'tipo': 'PEDIDO DE COMPRA', 'cor': '#2980B9', 'icone': 'fas fa-truck-loading', 'ordem': 2, 'dashboard_modulo': 'COMPRAS', 'dashboard_indicador': 'Ag. Entrega', 'dashboard_conta': True},
            {'nome': 'RECEBIDO', 'tipo': 'PEDIDO DE COMPRA', 'cor': '#27AE60', 'icone': 'fas fa-boxes', 'ordem': 3, 'dashboard_modulo': 'COMPRAS', 'dashboard_indicador': 'Recebidos', 'dashboard_conta': True},
            {'nome': 'ATRASADO', 'tipo': 'PEDIDO DE COMPRA', 'cor': '#C0392B', 'icone': 'fas fa-shipping-fast', 'ordem': 4, 'dashboard_modulo': 'COMPRAS', 'dashboard_indicador': 'Atrasados', 'dashboard_conta': True},
            {'nome': 'CANCELADO', 'tipo': 'PEDIDO DE COMPRA', 'cor': '#475569', 'icone': 'fas fa-times', 'ordem': 5, 'dashboard_modulo': 'COMPRAS', 'dashboard_indicador': 'Cancelados', 'dashboard_conta': True},

            # PRODUÇÃO
            {'nome': 'EM CORTE', 'tipo': 'ORDEM DE PRODUÇÃO', 'cor': '#E67E22', 'icone': 'fas fa-cut', 'ordem': 1, 'dashboard_modulo': 'PRODUCAO', 'dashboard_indicador': 'Em Corte', 'dashboard_conta': True},
            {'nome': 'PRENSA/PINTURA', 'tipo': 'ORDEM DE PRODUÇÃO', 'cor': '#D35400', 'icone': 'fas fa-palette', 'ordem': 2, 'dashboard_modulo': 'PRODUCAO', 'dashboard_indicador': 'Prensa/Pintura', 'dashboard_conta': True},
            {'nome': 'COSTURA', 'tipo': 'ORDEM DE PRODUÇÃO', 'cor': '#8E44AD', 'icone': 'fas fa-socks', 'ordem': 3, 'dashboard_modulo': 'PRODUCAO', 'dashboard_indicador': 'Costura', 'dashboard_conta': True},
            {'nome': 'ACABAMENTO', 'tipo': 'ORDEM DE PRODUÇÃO', 'cor': '#2980B9', 'icone': 'fas fa-magic', 'ordem': 4, 'dashboard_modulo': 'PRODUCAO', 'dashboard_indicador': 'Acabamento', 'dashboard_conta': True},
            {'nome': 'CANCELADO', 'tipo': 'ORDEM DE PRODUÇÃO', 'cor': '#475569', 'icone': 'fas fa-trash', 'ordem': 5, 'dashboard_modulo': 'PRODUCAO', 'dashboard_indicador': 'Cancelados', 'dashboard_conta': True},
        ]

        for item in data:
            existe = StatusWorkflow.query.filter_by(nome=item['nome'], tipo=item['tipo']).first()
            if existe:
                existe.cor = item['cor']
                existe.icone = item['icone']
                existe.ordem = item['ordem']
            else:
                db.session.add(StatusWorkflow(**item))
        
        db.session.commit()
        return jsonify({'success': True, 'message': 'Padrões "Quiet Luxury" restaurados com sucesso!'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500




@cadastros_bp.route('/card/empresa/relatorios')
@login_required
def card_rel_empresa():
    empresas_lista = Empresa.query.order_by(Empresa.razao_social).all()
    return render_template('cadastros/cards/empresa/form_rel_empresa.html', empresas_lista=empresas_lista)


# ── Central de Relatórios de Cadastros ─────────────────────────────────────
@cadastros_bp.route('/relatorios')
@login_required
def relatorios_cadastros():
    empresas_lista = Empresa.query.order_by(Empresa.razao_social).all()
    # Pega parâmetros de filtro
    empresa_id = request.args.get('empresa_id')
    visao      = request.args.get('visao', 'sintetica')
    tipo       = request.args.get('tipo', 'organograma') # organograma, headcount, cap_table, etc.

    data = {}
    if tipo == 'organograma':
        # Carrega estrutura para o organograma
        data['setores'] = Setor.query.filter_by(parent_id=None).all()
    elif tipo == 'cap_table':
        # Carrega sócios e aportes para gráfico
        if empresa_id:
            emp = Empresa.query.get(empresa_id)
            if emp:
                data['empresa'] = emp
                data['socios']  = emp.socios
    elif tipo == 'headcount':
        # Futura implementação de headcount
        pass
    elif tipo == 'auditoria':
        model_name = request.args.get('entidade')
        record_id = request.args.get('record_id')
        if not is_ari_dev(): # Segurança: Só em dev
             flash("Acesso restrito ao modo Desenvolvimento.", "warning")
             return redirect(url_for('cadastros.abas'))

        models_map = {
            'empresa': Empresa,
            'funcionario': Funcionario,
            'cliente': Cliente,
            'fornecedor': Fornecedor,
            'motorista': Motorista,
            'transportadora': Transportadora,
            'setor': Setor,
            'cargo': Cargo,
            'socio': Socio,
            'investidor': Investidor,
            'revendedor': Revendedor,
            'influenciador': Influenciador,
            'estilista': Estilista,
            'produto': Produto,
            'servico': Servico,
            'marca': Marca,
            'categoria': Categoria,
        }
        
        model_class = models_map.get(model_name)
        if not model_class:
            flash(f"Entidade '{model_name}' não mapeada para auditoria.", "danger")
            return redirect(url_for('cadastros.abas'))

        # Se não informou ID, tenta pegar o primeiro da tabela automaticamente
        record = None
        if record_id:
            record = model_class.query.get(record_id)
        else:
            record = model_class.query.first()
            if record:
                record_id = record.id
        
        if record:
            # Auditoria de Registro (Específico ou o Primeiro encontrado)
            data_audit = {c.name: getattr(record, c.name) for c in record.__table__.columns}
            return render_template('cadastros/relatorios/auditoria_integridade.html', 
                                 entidade=model_name.capitalize(),
                                 record_id=record_id,
                                 nome_registro=getattr(record, 'nome', getattr(record, 'razao_social', 'N/A')),
                                 auditoria_data=data_audit,
                                 is_estrutura=False)
        else:
            # Auditoria de Estrutura Pura (Caso a tabela esteja 100% vazia)
            total_registros = 0
            colunas = [c.name for c in model_class.__table__.columns]
            
            return render_template('cadastros/relatorios/auditoria_integridade.html', 
                                 entidade=model_name.capitalize(),
                                 is_estrutura=True,
                                 total_registros=total_registros,
                                 colunas=colunas)
    
    # Informações de "Saúde Cadastral" para o painel de decisão
    info = {
        'total_departamentos': Setor.query.count(),
        'setores_vazios': Setor.query.filter_by(parent_id=None).count(), # Exemplo: Setores raiz
        'total_socios': Socio.query.count(),
        'total_aportes': "1.250.000,00", # Exemplo estático para o BI
        'investidores_novos': 2,
        'data_alteracao': "15/05/2026",
        'aporte_pendente': True
    }
    
    return render_template(
        'cadastros/relatorios_cadastros.html',
        empresas_lista=empresas_lista,
        tipo_relatorio=tipo,
        visao=visao,
        rel_data=data,
        info=info,
        now=datetime.now
    )


# ── Excluir Documento ───────────────────────────────────────────────────────
@cadastros_bp.route('/empresa/<int:id>/doc/excluir/<nome>', methods=['POST'])
def excluir_doc(id, nome):
    nome_seguro = secure_filename(nome)
    caminho     = os.path.join(_pasta_empresa(id), nome_seguro)
    if os.path.isfile(caminho):
        os.remove(caminho)
        flash(f'Documento "{nome_seguro}" removido.', 'success')
    else:
        flash('Documento não encontrado.', 'warning')
    return redirect(url_for('cadastros.form_empresa', id=id))


# ── Formulário de Sócio ─────────────────────────────────────────────────────
@cadastros_bp.route('/socios/form', methods=['GET', 'POST'])
@cadastros_bp.route('/socios/form/<int:id>', methods=['GET', 'POST'])
def form_socio(id=None):
    socioID = id
    socio = Socio.query.get(id) if id else None
    print(f"DEBUG form_socio: id={id}, socio={socio}, socio.nome={socio.nome if socio else 'None'}")
    lista_socios = Socio.query.order_by(Socio.nome).all()
    empresas_lista = Empresa.query.order_by(Empresa.razao_social).all()

    # Pre-seleção via query string (vindo do form da empresa)
    empresa_id_pre = request.args.get('empresa_id', type=int)

    if request.method == 'POST':
        if socio is None:
            socio = Socio()

        socio.nome = request.form.get('nome', '').strip()
        socio.cpf = request.form.get('cpf', '').strip()
        socio.rg = request.form.get('rg', '').strip() or None
        socio.data_nascimento = _parse_date(request.form.get('data_nascimento', ''))
        socio.estado_civil = request.form.get('estado_civil', '').strip() or None
        socio.nacionalidade = request.form.get('nacionalidade', '').strip() or None
        socio.profissao = request.form.get('profissao', '').strip() or None

        socio.telefone = request.form.get('telefone', '').strip() or None
        socio.whatsapp = request.form.get('whatsapp', '').strip() or None
        socio.email = request.form.get('email', '').strip() or None
        socio.email_corporativo = request.form.get('email_corporativo', '').strip() or None

        socio.cep = request.form.get('cep', '').strip() or None
        socio.logradouro = request.form.get('logradouro', '').strip() or None
        socio.numero = request.form.get('numero', '').strip() or None
        socio.complemento = request.form.get('complemento', '').strip() or None
        socio.bairro = request.form.get('bairro', '').strip() or None
        socio.cidade = request.form.get('cidade', '').strip() or None
        socio.uf = request.form.get('uf', '').strip() or None
        socio.pais = request.form.get('pais', 'Brasil').strip() or None

        try:
            # Verificar CPF duplicado antes de salvar
            if socio.cpf:
                cpf_existente = Socio.query.filter(Socio.cpf == socio.cpf).first()
                if cpf_existente and (socio.id is None or cpf_existente.id != socio.id):
                    flash(f'CPF {socio.cpf} já está cadastrado para outro sócio.', 'danger')
                    return render_template(
                        'cadastros/cards/empresa/form_socio.html',
                        socio=socio,
                        socio_vinc=socio.empresas[0] if socio and socio.empresas else None,
                        lista_socios=Socio.query.order_by(Socio.nome).all(),
                        empresas_lista=Empresa.query.order_by(Empresa.razao_social).all(),
                        empresa_id_pre=empresa_id_pre,
                        getattr=getattr
                    )

            db.session.add(socio)
            db.session.flush()

            # ── Vínculo com Empresa ──
            empresa_id = request.form.get('empresa_id')
            if empresa_id:
                # Buscamos ou criamos o vínculo
                vinc = SocioEmpresa.query.filter_by(socio_id=socio.id, empresa_id=empresa_id).first()
                if not vinc:
                    vinc = SocioEmpresa(socio_id=socio.id, empresa_id=empresa_id)
                
                vinc.tipo_socio = request.form.get('tipo_socio')
                vinc.participacao = request.form.get('participacao') or None
                vinc.data_entrada = _parse_date(request.form.get('data_entrada'))
                vinc.data_saida = _parse_date(request.form.get('data_saida'))
                vinc.capital_integralizado = request.form.get('capital_integralizado') or None
                vinc.cargo = request.form.get('cargo')
                vinc.area_atuacao = request.form.get('area_atuacao')
                vinc.status_socio = request.form.get('status_socio', 'ativo')
                
                # Poderes (checkboxes no model são Boolean)
                vinc.tem_procuracao = request.form.get('tem_procuracao') == 'sim'
                vinc.tipo_procuracao = request.form.get('tipo_procuracao')
                vinc.procuracao_validade = _parse_date(request.form.get('procuracao_validade'))
                vinc.procuracao_obs = request.form.get('procuracao_obs')
                
                vinc.poder_cheques = 'sim' in request.form.get('poder_cheques', '')
                vinc.poder_contratos = 'sim' in request.form.get('poder_contratos', '')
                vinc.poder_representacao = 'sim' in request.form.get('poder_representacao', '')
                vinc.poder_bancario = 'sim' in request.form.get('poder_bancario', '')
                
                db.session.add(vinc)

            db.session.commit()
            flash('Sócio salvo com sucesso!', 'success')
            
            # Se veio de uma empresa e NÃO é modal, volta para o cadastro da empresa
            emp_id = request.form.get('empresa_id')
            if emp_id and not request.args.get('modal'):
                return redirect(url_for('cadastros.form_empresa', id=emp_id, aba='socios'))
                
            return redirect(url_for('cadastros.form_socio', id=socio.id, empresa_id=emp_id if emp_id else ''))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao salvar sócio: {str(e)}', 'danger')

    # Se estiver editando, tentamos carregar o vínculo principal (ou o primeiro)
    socio_vinc = socio.empresas[0] if socio and socio.empresas else None

    return render_template(
        'cadastros/cards/empresa/form_socio.html',
        socio=socio,
        socio_vinc=socio_vinc,
        lista_socios=lista_socios,
        empresas_lista=empresas_lista,
        empresa_id_pre=empresa_id_pre,
        getattr=getattr
    )


# ── Formulário de Investidor ────────────────────────────────────────────────
@cadastros_bp.route('/investidores/form', methods=['GET', 'POST'])
@cadastros_bp.route('/investidores/form/<int:id>', methods=['GET', 'POST'])
def form_investidor(id=None):
    investidor = Investidor.query.get(id) if id else None
    lista_investidores = Investidor.query.order_by(Investidor.nome, Investidor.razao_social).all()
    empresas_lista = Empresa.query.order_by(Empresa.razao_social).all()
    
    # Pre-seleção via query string
    empresa_id_pre = request.args.get('empresa_id', type=int)

    if request.method == 'POST':
        if investidor is None:
            investidor = Investidor()
        
        investidor.tipo_pessoa = request.form.get('tipo_pessoa', 'pf')
        
        if investidor.tipo_pessoa == 'pf':
            investidor.nome = request.form.get('nome', '').strip()
            investidor.cpf = request.form.get('cpf', '').strip()
            investidor.rg = request.form.get('rg', '').strip() or None
            investidor.data_nascimento = _parse_date(request.form.get('data_nascimento', ''))
            investidor.nacionalidade = request.form.get('nacionalidade', '').strip() or None
            investidor.profissao = request.form.get('profissao', '').strip() or None
            investidor.estado_civil = request.form.get('estado_civil', '').strip() or None
        else:
            investidor.razao_social = request.form.get('razao_social', '').strip()
            investidor.nome_fantasia = request.form.get('nome_fantasia', '').strip() or None
            investidor.cnpj = request.form.get('cnpj', '').strip()
            investidor.ie = request.form.get('ie', '').strip() or None
            investidor.responsavel = request.form.get('responsavel', '').strip() or None
            investidor.cpf_responsavel = request.form.get('cpf_responsavel', '').strip() or None

        investidor.telefone = request.form.get('telefone', '').strip() or None
        investidor.whatsapp = request.form.get('whatsapp', '').strip() or None
        investidor.email = request.form.get('email', '').strip() or None
        investidor.email2 = request.form.get('email2', '').strip() or None
        
        investidor.cep = request.form.get('cep', '').strip() or None
        investidor.logradouro = request.form.get('logradouro', '').strip() or None
        investidor.numero = request.form.get('numero', '').strip() or None
        investidor.complemento = request.form.get('complemento', '').strip() or None
        investidor.bairro = request.form.get('bairro', '').strip() or None
        investidor.cidade = request.form.get('cidade', '').strip() or None
        investidor.uf = request.form.get('uf', '').strip() or None
        investidor.pais = request.form.get('pais', 'Brasil').strip() or None

        try:
            # Verificar CPF/CNPJ duplicado antes de salvar
            if investidor.tipo_pessoa == 'pf' and investidor.cpf:
                cpf_existente = Investidor.query.filter(Investidor.cpf == investidor.cpf).first()
                if cpf_existente and (investidor.id is None or cpf_existente.id != investidor.id):
                    flash(f'CPF {investidor.cpf} já está cadastrado para outro investidor.', 'danger')
                    return render_template(
                        'cadastros/cards/empresa/form_investidor.html',
                        investidor=investidor,
                        lista_investidores=Investidor.query.order_by(Investidor.nome, Investidor.razao_social).all(),
                        empresas_lista=Empresa.query.order_by(Empresa.razao_social).all(),
                        empresa_id_pre=empresa_id_pre,
                        getattr=getattr
                    )
            elif investidor.tipo_pessoa == 'pj' and investidor.cnpj:
                cnpj_existente = Investidor.query.filter(Investidor.cnpj == investidor.cnpj).first()
                if cnpj_existente and (investidor.id is None or cnpj_existente.id != investidor.id):
                    flash(f'CNPJ {investidor.cnpj} já está cadastrado para outro investidor.', 'danger')
                    return render_template(
                        'cadastros/cards/empresa/form_investidor.html',
                        investidor=investidor,
                        lista_investidores=Investidor.query.order_by(Investidor.nome, Investidor.razao_social).all(),
                        empresas_lista=Empresa.query.order_by(Empresa.razao_social).all(),
                        empresa_id_pre=empresa_id_pre,
                        getattr=getattr
                    )

            db.session.add(investidor)
            db.session.flush()

            # ── Vínculo com Empresa ──
            empresa_id = request.form.get('empresa_id')
            if empresa_id:
                vinc = InvestidorEmpresa.query.filter_by(investidor_id=investidor.id, empresa_id=empresa_id).first()
                if not vinc:
                    vinc = InvestidorEmpresa(investidor_id=investidor.id, empresa_id=empresa_id)
                
                vinc.participacao = request.form.get('participacao') or None
                vinc.tipo_investimento = request.form.get('tipo_investimento')
                vinc.data_inicio = _parse_date(request.form.get('data_inicio'))
                vinc.data_vencimento = _parse_date(request.form.get('data_vencimento'))
                vinc.status_investimento = request.form.get('status_investimento', 'ativo')
                vinc.obs_investimento = request.form.get('obs_investimento')
                
                vinc.indexador = request.form.get('indexador')
                vinc.taxa_mensal = request.form.get('taxa_mensal') or None
                vinc.taxa_anual = request.form.get('taxa_anual') or None
                vinc.forma_pagamento = request.form.get('forma_pagamento')
                
                db.session.add(vinc)

            db.session.commit()
            flash('Investidor salvo com sucesso!', 'success')
            
            # Se veio de uma empresa e NÃO é modal, volta para o cadastro da empresa
            emp_id = request.form.get('empresa_id')
            if emp_id and not request.args.get('modal'):
                return redirect(url_for('cadastros.form_empresa', id=emp_id, aba='investidores'))

            return redirect(url_for('cadastros.form_investidor', id=investidor.id, empresa_id=emp_id if emp_id else ''))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao salvar investidor: {str(e)}', 'danger')

    # Vínculo principal para exibição no form
    investidor_vinc = investidor.empresas[0] if investidor and investidor.empresas else None

    return render_template(
        'cadastros/cards/empresa/form_investidor.html',
        investidor=investidor,
        investidor_vinc=investidor_vinc,
        lista_investidores=lista_investidores,
        empresas_lista=empresas_lista,
        empresa_id_pre=empresa_id_pre,
        getattr=getattr
    )


# ── Formulário de Cliente ───────────────────────────────────────────────────
@cadastros_bp.route('/clientes/cards/form', methods=['GET', 'POST'])
@cadastros_bp.route('/clientes/cards/form/<int:id>', methods=['GET', 'POST'])
def form_cliente(id=None):
    from app.models.operacoes.vendas import PedidoVenda
    cliente = Cliente.query.get(id) if id else None
    clientes_lista = Cliente.query.order_by(Cliente.nome).all()
    pedidos = PedidoVenda.query.filter_by(cliente_id=cliente.id).order_by(PedidoVenda.data_pedido.desc()).all() if cliente else []

    if request.method == 'POST':
        if cliente is None:
            cliente = Cliente()
        
        # Identificação
        cliente.tipo_pessoa     = request.form.get('tipo_pessoa', 'F')
        cliente.nome            = request.form.get('nome', '').strip()
        cliente.apelido         = request.form.get('apelido', '').strip() or None
        cliente.cpf_cnpj        = request.form.get('cpf_cnpj', '').strip()
        cliente.rg_ie           = request.form.get('rg_ie', '').strip() or None
        cliente.data_nascimento = _parse_date(request.form.get('data_nascimento'))
        cliente.genero          = request.form.get('genero')
        
        # Contato
        cliente.whatsapp = request.form.get('whatsapp', '').strip() or None
        cliente.telefone = request.form.get('telefone', '').strip() or None
        cliente.email    = request.form.get('email', '').strip() or None
        cliente.instagram = request.form.get('instagram', '').strip() or None
        
        # Perfil Comercial
        cliente.origem         = request.form.get('origem')
        cliente.categoria      = request.form.get('categoria')
        cliente.rating         = request.form.get('rating')
        l_cred = request.form.get('limite_credito', '0').replace('.', '').replace(',', '.')
        cliente.limite_credito = float(l_cred) if l_cred else 0.0
        cliente.cliente_desde  = _parse_date(request.form.get('cliente_desde'))
        
        # Endereço Res
        cliente.end_res_cep         = request.form.get('end_res_cep')
        cliente.end_res_logradouro  = request.form.get('end_res_logradouro')
        cliente.end_res_numero      = request.form.get('end_res_numero')
        cliente.end_res_complemento = request.form.get('end_res_complemento')
        cliente.end_res_bairro      = request.form.get('end_res_bairro')
        cliente.end_res_cidade      = request.form.get('end_res_cidade')
        cliente.end_res_uf          = request.form.get('end_res_uf')
        cliente.end_res_obs         = request.form.get('end_res_obs')

        # Endereço Ent
        cliente.end_ent_cep         = request.form.get('end_ent_cep')
        cliente.end_ent_logradouro  = request.form.get('end_ent_logradouro')
        cliente.end_ent_numero      = request.form.get('end_ent_numero')
        cliente.end_ent_complemento = request.form.get('end_ent_complemento')
        cliente.end_ent_bairro      = request.form.get('end_ent_bairro')
        cliente.end_ent_cidade      = request.form.get('end_ent_cidade')
        cliente.end_ent_uf          = request.form.get('end_ent_uf')
        cliente.end_ent_obs         = request.form.get('end_ent_obs')
        
        # Financeiro
        cliente.prazo_pagamento = request.form.get('prazo_pagamento')
        cliente.forma_pagamento = request.form.get('forma_pagamento')
        desc_p = request.form.get('desconto_padrao', '0').replace(',', '.')
        cliente.desconto_padrao = float(desc_p) if desc_p else 0.0
        l_comp = request.form.get('limite_compras', '0').replace('.', '').replace(',', '.')
        cliente.limite_compras  = float(l_comp) if l_comp else 0.0
        cliente.tabela_preco    = request.form.get('tabela_preco', 'Padrão')
        
        # Bancário
        cliente.banco         = request.form.get('banco')
        cliente.banco_nome    = request.form.get('banco_nome')
        cliente.banco_codigo  = request.form.get('banco_codigo')
        cliente.banco_agencia = request.form.get('banco_agencia')
        cliente.banco_conta   = request.form.get('banco_conta')
        cliente.banco_tipo    = request.form.get('banco_tipo')
        cliente.pix_chave     = request.form.get('pix_chave')
        
        # ── Meta
        cliente.observacoes      = request.form.get('observacoes')
        cliente.bloqueio_credito = request.form.get('bloqueio_credito') == '1'
        cliente.motivo_bloqueio  = request.form.get('motivo_bloqueio')
        
        # ── Upload de Foto
        if 'foto' in request.files:
            file = request.files['foto']
            if file and file.filename != '':
                upload_dir = os.path.join('static', 'img', 'clientes')
                os.makedirs(upload_dir, exist_ok=True)
                ext = os.path.splitext(file.filename)[1]
                # Salvamos primeiro sem ID se for novo, depois renomeamos ou usamos o nome seguro
                filename = secure_filename(f"cli_{datetime.now().strftime('%m%d%H%M%S')}{ext}")
                file.save(os.path.join(upload_dir, filename))
                cliente.foto = filename
        
        try:
            db.session.add(cliente)
            db.session.commit()

            # ── Sincroniza Cliente → LeadOne Pipeline ──────────────────────
            try:
                from app.models.digital.lead import Lead
                telefone_lead = cliente.whatsapp or cliente.telefone
                if telefone_lead:
                    # Evita duplicidade por telefone
                    existente = Lead.query.filter(
                        db.or_(Lead.telefone == telefone_lead, Lead.telefone == cliente.telefone)
                    ).first()
                    if not existente:
                        lead = Lead(
                            nome=cliente.nome,
                            email=cliente.email,
                            telefone=telefone_lead,
                            etapa='Contato Feito',
                            origem=cliente.origem or 'Cadastro de Cliente',
                            observacoes=f'Cliente sincronizado do Cadastro (ID: {cliente.id})'
                        )
                        db.session.add(lead)
                        db.session.commit()
            except Exception as sync_err:
                db.session.rollback()
                # Não quebra o fluxo principal; apenas loga
                print(f'[LeadOne Sync] Erro ao criar lead para cliente {cliente.id}: {sync_err}')
            # ─────────────────────────────────────────────────────────────

            # Atualiza pedidos após commit (caso seja novo ou tenha mudado)
            pedidos = PedidoVenda.query.filter_by(cliente_id=cliente.id).order_by(PedidoVenda.data_pedido.desc()).all() if cliente else []
            
            # Feedback de Integridade AriOne
            msg = f'Cliente "{cliente.nome}" salvo com sucesso!'
            if request.args.get('modal'):
                msg = f'Auditoria: Integridade Confirmada. Cliente "{cliente.nome}" registrado.'
            
            flash(msg, 'success')
            
            # Se for AJAX/Modal ou requisição direta, retornamos o template renderizado para manter o contexto
            return render_template('cadastros/cards/pessoas/form_cliente.html', 
                                 cliente=cliente, 
                                 clientes_lista=Cliente.query.order_by(Cliente.nome).all(),
                                 pedidos=pedidos,
                                 hoje=datetime.now().date())
        except Exception as e:
            db.session.rollback()
            flash(f'Erro de Integridade ao salvar: {str(e)}', 'danger')

    resp = make_response(render_template('cadastros/cards/pessoas/form_cliente.html', 
                         cliente=cliente, 
                         clientes_lista=clientes_lista,
                         pedidos=pedidos,
                         hoje=datetime.now().date()))
    resp.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate'
    return resp

@cadastros_bp.route('/clientes/inativar/<int:id>', methods=['POST'])
def inativar_cliente(id):
    cliente = Cliente.query.get_or_404(id)
    try:
        cliente.ativo = False
        db.session.commit()
        flash(f'Cliente "{cliente.nome}" inativado.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao inativar: {str(e)}', 'danger')
    return redirect(url_for('cadastros.form_cliente', id=id))

@cadastros_bp.route('/clientes/reativar/<int:id>', methods=['POST'])
def reativar_cliente(id):
    cliente = Cliente.query.get_or_404(id)
    try:
        cliente.ativo = True
        db.session.commit()
        flash(f'Cliente "{cliente.nome}" reativado.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao reativar: {str(e)}', 'danger')
    return redirect(url_for('cadastros.form_cliente', id=id))

@cadastros_bp.route('/clientes/doc/excluir/<int:id>/<nome>', methods=['POST'])
def excluir_doc_cliente(id, nome):
    # Lógica de exclusão de arquivo similar ao da empresa
    flash('Funcionalidade de exclusão de anexo em desenvolvimento.', 'info')
    return redirect(url_for('cadastros.form_cliente', id=id))


# ── Formulário de Fornecedor ────────────────────────────────────────────────
@cadastros_bp.route('/fornecedores/cards/form', methods=['GET', 'POST'])
@cadastros_bp.route('/fornecedores/cards/form/<int:id>', methods=['GET', 'POST'])
def form_fornecedor(id=None):
    fornecedor = Fornecedor.query.get(id) if id else None
    fornecedores_lista = Fornecedor.query.order_by(Fornecedor.razao_social).all()

    if request.method == 'POST':
        if fornecedor is None:
            fornecedor = Fornecedor()
        
        # Identificação
        fornecedor.tipo_pessoa     = request.form.get('tipo_pessoa', 'J')
        fornecedor.razao_social    = request.form.get('razao_social', '').strip()
        fornecedor.nome_fantasia   = request.form.get('nome_fantasia', '').strip() or None
        fornecedor.cnpj_cpf        = request.form.get('cnpj_cpf', '').strip()
        fornecedor.ie_rg           = request.form.get('ie_rg', '').strip() or None
        fornecedor.data_abertura   = _parse_date(request.form.get('data_abertura'))
        
        # Contato
        fornecedor.contato_nome  = request.form.get('contato_nome', '').strip() or None
        fornecedor.contato_cargo = request.form.get('contato_cargo', '').strip() or None
        fornecedor.whatsapp      = request.form.get('whatsapp', '').strip() or None
        fornecedor.telefone      = request.form.get('telefone', '').strip() or None
        fornecedor.email         = request.form.get('email', '').strip() or None
        fornecedor.website       = request.form.get('website', '').strip() or None
        
        # Perfil
        fornecedor.categoria      = request.form.get('categoria')
        fornecedor.avaliacao      = request.form.get('avaliacao')
        fornecedor.is_fp          = request.form.get('is_fp') == 'on'
        fornecedor.prazo_entrega  = int(request.form.get('prazo_entrega') or 0)
        
        # Endereço
        fornecedor.end_cep         = request.form.get('end_cep')
        fornecedor.end_logradouro  = request.form.get('end_logradouro')
        fornecedor.end_numero      = request.form.get('end_numero')
        fornecedor.end_complemento = request.form.get('end_complemento')
        fornecedor.end_bairro      = request.form.get('end_bairro')
        fornecedor.end_cidade      = request.form.get('end_cidade')
        fornecedor.end_uf          = request.form.get('end_uf')
        
        # Financeiro
        fornecedor.prazo_pagamento = request.form.get('prazo_pagamento')
        fornecedor.forma_pagamento = request.form.get('forma_pagamento')
        fornecedor.moeda           = request.form.get('moeda', 'BRL')
        
        # Bancário
        fornecedor.banco_nome    = request.form.get('banco_nome')
        fornecedor.banco_codigo  = request.form.get('banco_codigo')
        fornecedor.banco_agencia = request.form.get('banco_agencia')
        fornecedor.banco_conta   = request.form.get('banco_conta')
        fornecedor.banco_tipo    = request.form.get('banco_tipo')
        fornecedor.pix_tipo      = request.form.get('pix_tipo')
        fornecedor.pix_chave     = request.form.get('pix_chave')
        
        fornecedor.observacoes   = request.form.get('observacoes')
        
        # ── Upload de Foto
        if 'foto' in request.files:
            file = request.files['foto']
            if file and file.filename != '':
                upload_dir = os.path.join('static', 'img', 'fornecedores')
                os.makedirs(upload_dir, exist_ok=True)
                ext = os.path.splitext(file.filename)[1]
                filename = secure_filename(f"for_{fornecedor.id if fornecedor.id else 'novo'}_{datetime.now().strftime('%m%d%H%M%S')}{ext}")
                file.save(os.path.join(upload_dir, filename))
                fornecedor.foto = filename
        
        try:
            if not fornecedor.id:
                existente = Fornecedor.query.filter_by(cnpj_cpf=fornecedor.cnpj_cpf).first()
                if existente:
                    flash(f'Erro: O CNPJ/CPF {fornecedor.cnpj_cpf} já está cadastrado para "{existente.razao_social}".', 'danger')
                    return render_template('cadastros/cards/pessoas/form_fornecedor.html', 
                                         fornecedor=fornecedor, 
                                         fornecedores_lista=Fornecedor.query.order_by(Fornecedor.razao_social).all())

            db.session.add(fornecedor)
            db.session.commit()
            flash(f'Fornecedor "{fornecedor.razao_social}" salvo!', 'success')
            return render_template('cadastros/cards/pessoas/form_fornecedor.html', 
                                 fornecedor=fornecedor, 
                                 fornecedores_lista=Fornecedor.query.order_by(Fornecedor.razao_social).all())
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao salvar: {str(e)}', 'danger')

    resp = make_response(render_template('cadastros/cards/pessoas/form_fornecedor.html', fornecedor=fornecedor, fornecedores_lista=fornecedores_lista))
    resp.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate'
    return resp

@cadastros_bp.route('/fornecedores/inativar/<int:id>', methods=['POST'])
def inativar_fornecedor(id):
    fornecedor = Fornecedor.query.get_or_404(id)
    try:
        fornecedor.ativo = False
        db.session.commit()
        flash(f'Fornecedor "{fornecedor.razao_social}" inativado.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao inativar: {str(e)}', 'danger')
    return redirect(url_for('cadastros.form_fornecedor', id=id))

@cadastros_bp.route('/fornecedores/reativar/<int:id>', methods=['POST'])
def reativar_fornecedor(id):
    fornecedor = Fornecedor.query.get_or_404(id)
    try:
        fornecedor.ativo = True
        db.session.commit()
        flash(f'Fornecedor "{fornecedor.razao_social}" reativado.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao reativar: {str(e)}', 'danger')
    return redirect(url_for('cadastros.form_fornecedor', id=id))


# ── Formulário de Funcionário ───────────────────────────────────────────────
@cadastros_bp.route('/funcionarios/cards/form', methods=['GET', 'POST'])
@cadastros_bp.route('/funcionarios/cards/form/<int:id>', methods=['GET', 'POST'])
def form_funcionario(id=None):
    from app.models.cadastros.funcionario import Funcionario, Cargo, Setor
    from decimal import Decimal

    from flask import session
    empresa_ativa_id = session.get('empresa_id')

    from sqlalchemy import or_
    
    # Filtro Multi-Empresa: Inclui registros sem empresa_id para evitar "sumiço" de dados antigos (como o ID 1)
    if empresa_ativa_id:
        lista_funcionarios = Funcionario.query.filter(or_(Funcionario.empresa_id == empresa_ativa_id, Funcionario.empresa_id == None)).order_by(Funcionario.nome).all()
        cargos_lista = Cargo.query.filter_by(ativo=True).order_by(Cargo.nome).all()
        setores_lista = Setor.query.filter_by(ativo=True).order_by(Setor.nome).all()
        empresas_lista = Empresa.query.filter_by(ativa=True).order_by(Empresa.razao_social).all()
    else:
        lista_funcionarios = Funcionario.query.order_by(Funcionario.nome).all()
        cargos_lista = Cargo.query.order_by(Cargo.nome).all()
        setores_lista = Setor.query.order_by(Setor.nome).all()
        empresas_lista = Empresa.query.order_by(Empresa.razao_social).all()

    # ── LÓGICA DE REGISTRO PADRÃO ──
    # Se não houver ID na URL, busca o primeiro da lista para preencher os campos automaticamente (Pedido AriOne)
    funcionario = Funcionario.query.get(id) if id else None
    if not funcionario and lista_funcionarios and not request.args.get('novo'):
        funcionario = lista_funcionarios[0]

    # Centros de Custo para o seletor
    from app.models.gestao.centro_custo import CentroCusto
    centros_custos_lista = CentroCusto.query.filter_by(ativo=True).order_by(CentroCusto.codigo).all()

    if request.method == 'POST':
        # ── CAMADA 1: VALIDAÇÃO (O "Antes") ──
        # Regras rigorosas para evitar "lixo" no bando de dados
        nome_form = request.form.get('nome', '').strip()
        cpf_form = request.form.get('cpf', '').replace('.', '').replace('-', '').strip()
        turno_form = request.form.get('turno')
        
        if not nome_form or len(nome_form) < 3:
            flash("Integridade: Nome do funcionário é muito curto ou inválido.", "danger")
            return redirect(url_for('cadastros.form_funcionario', id=id))
            
        if len(cpf_form) != 11:
            flash(f"Integridade AriOne: O CPF deve ter 11 dígitos. Recebido: {len(cpf_form)} dígitos ({cpf_form}).", "danger")
            return redirect(url_for('cadastros.form_funcionario', id=id))

        if not turno_form:
            flash("Integridade: O campo Turno/Escala é obrigatório para produção.", "danger")
            return redirect(url_for('cadastros.form_funcionario', id=id))

        if funcionario is None:
            # 🔍 INTEGRIDADE ARIONE: Pesquisa se o CPF já existe de forma limpa
            existente = Funcionario.query.filter(Funcionario.cpf.like(f"%{cpf_form[-4:]}%")).all()
            for ex in existente:
                clean_ex = ex.cpf.replace('.','').replace('-','')
                if clean_ex == cpf_form:
                    flash(f"IDENTIDADE BLOQUEADA: O CPF '{request.form.get('cpf')}' já pertence a '{ex.nome}' (ID {ex.id}).", "danger")
                    return redirect(url_for('cadastros.form_funcionario'))

            funcionario = Funcionario()
            # Vínculo automático com a empresa ativa no cadastro inicial
            if empresa_ativa_id:
                funcionario.empresa_id = empresa_ativa_id
        
        # ── Identificação ──
        funcionario.nome = request.form.get('nome')
        funcionario.cpf = request.form.get('cpf')
        funcionario.rg = request.form.get('rg')
        funcionario.rg_orgao = request.form.get('rg_orgao')
        
        rg_dt = request.form.get('rg_data_emissao')
        funcionario.rg_data_emissao = datetime.strptime(rg_dt, '%Y-%m-%d').date() if rg_dt else None
        
        funcionario.pis_pasep = request.form.get('pis_pasep')
        funcionario.nome_mae = request.form.get('nome_mae')
        funcionario.nome_pai = request.form.get('nome_pai')
        funcionario.titulo_eleitor = request.form.get('titulo_eleitor')
        funcionario.reservista = request.form.get('reservista')
        funcionario.cnh = request.form.get('cnh')
        funcionario.cnh_categoria = request.form.get('cnh_categoria')
        
        funcionario.tipo_sanguineo = request.form.get('tipo_sanguineo')
        funcionario.alergias = request.form.get('alergias')
        
        dt_nascto = request.form.get('data_nascimento')
        funcionario.data_nascimento = datetime.strptime(dt_nascto, '%Y-%m-%d').date() if dt_nascto else None
        
        funcionario.genero = request.form.get('genero')
        funcionario.estado_civil = request.form.get('estado_civil')
        
        # ── Contato & Endereço ──
        funcionario.email_pessoal = request.form.get('email_pessoal')
        funcionario.email_corporativo = request.form.get('email_corporativo')
        funcionario.telefone = request.form.get('telefone')
        funcionario.whatsapp = request.form.get('whatsapp')
        
        funcionario.cep = request.form.get('cep')
        funcionario.logradouro = request.form.get('logradouro')
        funcionario.numero = request.form.get('numero')
        funcionario.bairro = request.form.get('bairro')
        funcionario.cidade = request.form.get('cidade')
        funcionario.uf = request.form.get('uf')
        funcionario.complemento = request.form.get('complemento')
        
        # ── Contrato & Org ──
        funcionario.empresa_id = request.form.get('empresa_id') or None
        
        # Sanitização da Matrícula: Impede o salvamento do texto "None" ou vázio
        matricula_raw = request.form.get('matricula', '').strip()
        if not matricula_raw or matricula_raw.lower() == 'none':
            funcionario.matricula = None
        else:
            funcionario.matricula = matricula_raw
        funcionario.cargo_id = request.form.get('cargo_id') or None
        funcionario.setor_id = request.form.get('setor_id') or None
        funcionario.data_admissao = _parse_date(request.form.get('data_admissao', ''))
        funcionario.data_demissao = _parse_date(request.form.get('data_demissao', ''))
        funcionario.tipo_contrato = request.form.get('tipo_contrato', 'CLT')
        funcionario.status = request.form.get('status', 'Ativo')
        funcionario.centro_custo_id = request.form.get('centro_custo_id') or None
        
        # ── Hierarquia & Org ──
        funcionario.gestor_id = request.form.get('gestor_id') or None
        funcionario.nivel_hierarquico = request.form.get('nivel_hierarquico')
        funcionario.unidade_negocio = request.form.get('unidade_negocio')
        
        # ── Jornada & Escalas ──
        funcionario.turno = request.form.get('turno')
        funcionario.regime_escala = request.form.get('regime_escala')
        tol = request.form.get('ponto_tolerancia', '5')
        funcionario.ponto_tolerancia = int(tol) if tol.isdigit() else 5
        
        funcionario.jornada_entrada = request.form.get('jornada_entrada')
        funcionario.jornada_saida = request.form.get('jornada_saida')
        funcionario.jornada_intervalo = request.form.get('jornada_intervalo')
        
        # ── SESMT (Saúde) ──
        dt_aso = request.form.get('aso_data')
        funcionario.aso_data = datetime.strptime(dt_aso, '%Y-%m-%d').date() if dt_aso else None
        
        dt_valid = request.form.get('aso_validade')
        funcionario.aso_validade = datetime.strptime(dt_valid, '%Y-%m-%d').date() if dt_valid else None
        
        funcionario.epi_entregues = request.form.get('epi_entregues')

        # ── Upload de Foto HCM ──
        if 'file_foto' in request.files:
            foto_file = request.files['file_foto']
            if foto_file and foto_file.filename != '':
                upload_dir = os.path.join('static', 'img', 'funcionarios')
                os.makedirs(upload_dir, exist_ok=True)
                
                # Nome seguro com ID e Timestamp para evitar cache e conflitos
                ext = os.path.splitext(foto_file.filename)[1]
                filename = secure_filename(f"hcm_{funcionario.id if funcionario.id else 'novo'}_{datetime.now().strftime('%m%d%H%M%S')}{ext}")
                foto_file.save(os.path.join(upload_dir, filename))
                funcionario.foto = filename
        
        # ── Remuneração ──
        sal_base = request.form.get('salario_base', '0').replace('.', '').replace(',', '.')
        funcionario.salario_base = Decimal(sal_base) if sal_base else Decimal('0.00')
        funcionario.peridiocidade = request.form.get('peridiocidade', 'Mensal')
        
        # ── Dados Bancários ──
        funcionario.banco = request.form.get('banco', '').strip() or None
        funcionario.tipo_conta = request.form.get('tipo_conta') # Corrente, Poupança
        funcionario.agencia = request.form.get('agencia', '').strip() or None
        funcionario.conta = request.form.get('conta', '').strip() or None
        funcionario.pix = request.form.get('pix', '').strip() or None

        try:
            db.session.add(funcionario)
            db.session.commit()
            
            # ── CAMADA 3: TESTE DE PERSISTÊNCIA (Leitura pós-gravação) ──
            # Verifica se o que foi salvo no banco é o que deveria estar lá
            db.session.refresh(funcionario) # Força recarga do banco
            if funcionario.id and funcionario.nome == nome_form:
                 flash(f'Auditoria: Integridade de Persistência Confirmada para {funcionario.nome}.', 'success')
            else:
                 raise Exception("Erro de Mapeamento: Os dados gravados divergem do formulário.")
            
            # ── Processamento de Uploads HCM ──
            try:
                from flask import current_app
                upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'funcionarios', str(funcionario.id))
                os.makedirs(upload_dir, exist_ok=True)
                
                # Documentos (RG/CPF)
                if 'file_docs' in request.files:
                    f = request.files['file_docs']
                    if f and f.filename:
                        name = secure_filename(f.filename)
                        f.save(os.path.join(upload_dir, name))
                        funcionario.path_documentos = f"uploads/funcionarios/{funcionario.id}/"
                
                db.session.commit()
            except Exception as up_err:
                print(f"Erro no upload AriOne: {up_err}")

            if request.args.get('modal'):
                flash(f'Audit: Integridade Confirmada. Funcionário "{funcionario.nome}" salvo.', 'success')
                return render_template('cadastros/cards/pessoas/form_funcionario.html', 
                                     funcionario=funcionario, 
                                     lista_funcionarios=Funcionario.query.order_by(Funcionario.nome).all(),
                                     cargos_lista=Cargo.query.filter_by(ativo=True).all(),
                                     setores_lista=Setor.query.filter_by(ativo=True).all(),
                                     empresas_lista=Empresa.query.filter_by(ativa=True).all(),
                                     centros_custos_lista=centros_custos_lista)

            flash(f'Funcionário "{funcionario.nome}" salvo com sucesso!', 'success')
            return redirect(url_for('cadastros.form_funcionario', id=funcionario.id))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao salvar: {str(e)}', 'danger')

    resp = make_response(render_template(
        'cadastros/cards/pessoas/form_funcionario.html',
        funcionario=funcionario,
        lista_funcionarios=lista_funcionarios,
        empresas_lista=empresas_lista,
        cargos_lista=cargos_lista,
        setores_lista=setores_lista,
        centros_custos_lista=centros_custos_lista
    ))
    resp.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate'
    return resp

@cadastros_bp.route('/funcionarios/inativar/<int:id>', methods=['POST'])
def inativar_funcionario(id):
    funcionario = Funcionario.query.get_or_404(id)
    try:
        funcionario.status = 'Desligado'
        funcionario.ativo = False
        funcionario.data_demissao = date.today()
        db.session.commit()
        flash(f'Funcionário "{funcionario.nome}" desligado com sucesso.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao desligar: {str(e)}', 'danger')
    return redirect(url_for('cadastros.abas', aba='pessoas', auto_open='funcionarios'))

@cadastros_bp.route('/funcionarios/excluir/<int:id>', methods=['POST'])
def excluir_funcionario(id):
    funcionario = Funcionario.query.get_or_404(id)
    try:
        nome = funcionario.nome
        db.session.delete(funcionario)
        db.session.commit()
        flash(f'Funcionário "{nome}" removido permanentemente.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao excluir: {str(e)}', 'danger')
    return redirect(url_for('cadastros.abas', aba='pessoas', auto_open='funcionarios'))


@cadastros_bp.route('/funcionarios/org/cargo/add', methods=['POST'])
def add_cargo_ajax():
    from app.models.cadastros.funcionario import Cargo
    nome = request.form.get('nome', '').strip()
    if nome:
        novo = Cargo(nome=nome)
        db.session.add(novo)
        db.session.commit()
        return {"success": True, "id": novo.id, "nome": novo.nome}
    return {"success": False}, 400

@cadastros_bp.route('/funcionarios/org/setor/add', methods=['POST'])
def add_setor_ajax():
    from app.models.cadastros.funcionario import Setor
    nome = request.form.get('nome', '').strip()
    if nome:
        parent_id = request.form.get('parent_id') or None
        prefix = "DEP" if parent_id else "SET"
        
        # Gera código automático se não enviado
        codigo_enviado = request.form.get('codigo', '').strip()
        if not codigo_enviado:
            ultimo = Setor.query.order_by(Setor.id.desc()).first()
            proximo_id = (ultimo.id + 1) if ultimo else 1
            codigo_enviado = f"{prefix}-{proximo_id:03d}"

        novo = Setor(
            nome=nome,
            codigo=codigo_enviado,
            sigla=request.form.get('sigla', '').strip() or None,
            parent_id=parent_id
        )
        db.session.add(novo)
        db.session.commit()
        return {"success": True, "id": novo.id, "nome": novo.nome}
    return {"success": False}, 400


# ── Formulário de Motorista ─────────────────────────────────────────────────
@cadastros_bp.route('/motoristas/cards/form', methods=['GET', 'POST'])
@cadastros_bp.route('/motoristas/cards/form/<int:id>', methods=['GET', 'POST'])
def form_motorista(id=None):
    motorista = Motorista.query.get(id) if id else None
    motoristas_lista = Motorista.query.order_by(Motorista.nome).all()
    transportadoras_lista = Transportadora.query.order_by(Transportadora.razao_social).all()

    if request.method == 'POST':
        if motorista is None:
            motorista = Motorista()
        
        motorista.nome            = request.form.get('nome', '').strip()
        motorista.cpf             = request.form.get('cpf', '').strip()
        motorista.rg              = request.form.get('rg', '').strip() or None
        motorista.data_nascimento = _parse_date(request.form.get('data_nascimento'))
        
        motorista.cnh_numero    = request.form.get('cnh_numero')
        motorista.cnh_categoria = request.form.get('cnh_categoria')
        motorista.cnh_validade  = _parse_date(request.form.get('cnh_validade'))
        motorista.mopp          = request.form.get('mopp') == '1'
        
        motorista.tipo_vinculo = request.form.get('tipo_vinculo')
        motorista.transportadora_id = request.form.get('transportadora_id') or None
        
        motorista.whatsapp = request.form.get('whatsapp', '').strip() or None
        motorista.telefone = request.form.get('telefone', '').strip() or None
        motorista.email    = request.form.get('email', '').strip() or None
        
        motorista.end_cep         = request.form.get('end_cep')
        motorista.end_logradouro  = request.form.get('end_logradouro')
        motorista.end_numero      = request.form.get('end_numero')
        motorista.end_complemento = request.form.get('end_complemento')
        motorista.end_bairro      = request.form.get('end_bairro')
        motorista.end_cidade      = request.form.get('end_cidade')
        motorista.end_uf          = request.form.get('end_uf')
        
        motorista.observacoes   = request.form.get('observacoes')
        
        # ── Upload de Foto
        if 'foto' in request.files:
            file = request.files['foto']
            if file and file.filename != '':
                upload_dir = os.path.join('static', 'img', 'motoristas')
                os.makedirs(upload_dir, exist_ok=True)
                ext = os.path.splitext(file.filename)[1]
                filename = secure_filename(f"mot_{motorista.id if motorista.id else 'novo'}_{datetime.now().strftime('%m%d%H%M%S')}{ext}")
                file.save(os.path.join(upload_dir, filename))
                motorista.foto = filename
        
        try:
            db.session.add(motorista)
            db.session.commit()
            flash(f'Motorista "{motorista.nome}" salvo!', 'success')
            return render_template('cadastros/cards/pessoas/form_motorista.html', 
                                 motorista=motorista, 
                                 motoristas_lista=Motorista.query.order_by(Motorista.nome).all(),
                                 transportadoras_lista=Transportadora.query.order_by(Transportadora.razao_social).all())
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao salvar: {str(e)}', 'danger')

    resp = make_response(render_template(
        'cadastros/cards/pessoas/form_motorista.html',
        motorista=motorista,
        motoristas_lista=motoristas_lista,
        transportadoras_lista=transportadoras_lista
    ))
    resp.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate'
    return resp

@cadastros_bp.route('/motoristas/inativar/<int:id>', methods=['POST'])
def inativar_motorista(id):
    motorista = Motorista.query.get_or_404(id)
    try:
        motorista.ativo = False
        db.session.commit()
        flash(f'Motorista "{motorista.nome}" inativado.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao inativar: {str(e)}', 'danger')
    return redirect(url_for('cadastros.form_motorista', id=id))

@cadastros_bp.route('/motoristas/reativar/<int:id>', methods=['POST'])
def reativar_motorista(id):
    motorista = Motorista.query.get_or_404(id)
    try:
        motorista.ativo = True
        db.session.commit()
        flash(f'Motorista "{motorista.nome}" reativado.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao reativar: {str(e)}', 'danger')
    return redirect(url_for('cadastros.form_motorista', id=id))



# ── Excluir Documento de Motorista ──────────────────────────────────────────
@cadastros_bp.route('/motoristas/<int:id>/doc/excluir/<nome>', methods=['POST'])
def excluir_doc_motorista(id, nome):
    nome_seguro = secure_filename(nome)
    caminho     = os.path.join(_pasta_motorista(id), nome_seguro)
    if os.path.isfile(caminho):
        os.remove(caminho)
        flash(f'Documento "{nome_seguro}" removido.', 'success')
    else:
        flash('Documento não encontrado.', 'warning')
    return redirect(url_for('cadastros.form_motorista', id=id))


# =============================================================================
# Transportadoras
# =============================================================================

UPLOAD_BASE_TRA = os.path.join('static', 'uploads', 'transportadoras')

def _pasta_transportadora(transportadora_id):
    pasta = os.path.join(UPLOAD_BASE_TRA, str(transportadora_id))
    os.makedirs(pasta, exist_ok=True)
    return pasta


# =============================================================================
# Entregador
# =============================================================================
@cadastros_bp.route('/entregadores/form', methods=['GET', 'POST'])
@cadastros_bp.route('/entregadores/form/<int:id>', methods=['GET', 'POST'])
@login_required
def form_entregador(id=None):
    from app.models.cadastros.entregador import Entregador
    try:
        db.create_all()
    except:
        pass

    entregador = Entregador.query.get(id) if id else None
    
    if request.method == 'POST':
        if not entregador:
            entregador = Entregador()
            db.session.add(entregador)
        
        entregador.nome         = request.form.get('nome', '').strip().upper()
        entregador.whatsapp     = request.form.get('whatsapp', '').strip()
        entregador.tipo_veiculo = request.form.get('tipo_veiculo', '').strip().upper()
        entregador.placa        = request.form.get('placa', '').strip().upper()
        
        try:
            db.session.commit()
            flash("Entregador salvo com sucesso!", "success")
            import time
            return redirect(url_for('cadastros.form_entregador', id=entregador.id, modal=request.args.get('modal', 0), t=int(time.time())))
        except Exception as e:
            db.session.rollback()
            flash(f"Erro: {str(e)}", "danger")

    entregadores_lista = Entregador.query.order_by(Entregador.nome).all()
    resp = make_response(render_template('operacoes/cards/expedicao/form_entregador.html', entregador=entregador, entregadores_lista=entregadores_lista))
    resp.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    resp.headers["Pragma"] = "no-cache"
    resp.headers["Expires"] = "0"
    return resp

@cadastros_bp.route('/transportadoras/form', methods=['GET', 'POST'])
@cadastros_bp.route('/transportadoras/form/<int:id>', methods=['GET', 'POST'])
@login_required
def form_transportadora(id=None):
    from app.models.cadastros.transportadora import Transportadora
    from sqlalchemy import text
    
    # --- AUTO SYNC DB SCHEMA ---
    try:
        columns = [
            ('modal_transporte', 'VARCHAR(100)'), ('tipo_servico', 'VARCHAR(100)'), ('prazo_entrega', 'INTEGER'),
            ('avaliacao', 'VARCHAR(1)'), ('contato_nome', 'VARCHAR(100)'), ('contato_cargo', 'VARCHAR(100)'),
            ('parceira_desde', 'DATE'), ('end_com_cep', 'VARCHAR(9)'), ('end_com_logradouro', 'VARCHAR(150)'),
            ('end_com_numero', 'VARCHAR(20)'), ('end_com_complemento', 'VARCHAR(100)'), ('end_com_bairro', 'VARCHAR(80)'),
            ('end_com_cidade', 'VARCHAR(80)'), ('end_com_uf', 'VARCHAR(2)'), ('end_ent_cep', 'VARCHAR(9)'),
            ('end_ent_logradouro', 'VARCHAR(150)'), ('end_ent_numero', 'VARCHAR(20)'), ('end_ent_complemento', 'VARCHAR(100)'),
            ('end_ent_bairro', 'VARCHAR(80)'), ('end_ent_cidade', 'VARCHAR(80)'), ('end_ent_uf', 'VARCHAR(2)'),
            ('prazo_pagamento', 'VARCHAR(50)'), ('forma_pagamento', 'VARCHAR(50)'), ('tabela_frete', 'VARCHAR(100)'),
            ('banco_nome', 'VARCHAR(100)'), ('banco_codigo', 'VARCHAR(10)'), ('banco_agencia', 'VARCHAR(20)'),
            ('banco_conta', 'VARCHAR(20)'), ('pix_chave', 'VARCHAR(100)'),
            ('coleta_origem', 'VARCHAR(3)'), ('entrega_final', 'VARCHAR(3)'), ('entregador_final', 'VARCHAR(50)'),
            ('coleta_veiculos', 'VARCHAR(100)'), ('entrega_veiculos', 'VARCHAR(100)'), ('rotas_data', 'TEXT')
        ]
        for col_name, col_type in columns:
            try:
                db.session.execute(text(f"ALTER TABLE transportadoras ADD COLUMN {col_name} {col_type}"))
                db.session.commit()
            except Exception:
                db.session.rollback()
        
        from app.models.cadastros.entregador import Entregador
        db.create_all()
    except Exception:
        pass
    # ---------------------------

    transportadora        = Transportadora.query.get(id) if id else None
    transportadoras_lista = Transportadora.query.order_by(Transportadora.razao_social).all()

    docs                  = []
    is_modal = request.args.get('modal') == '1'

    if request.method == 'POST':
        if not transportadora:
            transportadora = Transportadora()
            db.session.add(transportadora)

        # Identificação (Sanitização AriOne: Uppercase)
        transportadora.tipo_pessoa   = request.form.get('tipo_pessoa', 'J')
        transportadora.razao_social  = request.form.get('razao_social', '').strip().upper()
        transportadora.nome_fantasia = request.form.get('nome_fantasia', '').strip().upper()
        
        doc_val = request.form.get('cnpj_cpf', '').strip()
        if not doc_val:
            # 💡 AriOne Hack: Se o banco não permite NULL, usamos um ID único temporário
            # Isso permite "cadastrar sem CNPJ" satisfazendo as constraints UNIQUE e NOT NULL do SQLite
            import uuid
            transportadora.cnpj_cpf = f"SN-{uuid.uuid4().hex[:12]}"
        else:
            transportadora.cnpj_cpf = doc_val
        
        transportadora.ie_rg         = request.form.get('ie_rg', '').strip().upper()
        transportadora.rntrc         = request.form.get('rntrc', '').strip().upper()

        # Contato
        transportadora.whatsapp = request.form.get('whatsapp', '').strip()
        transportadora.telefone = request.form.get('telefone', '').strip()
        transportadora.email    = request.form.get('email', '').strip().lower()
        transportadora.website  = request.form.get('website', '').strip().lower()

        # Endereço Comercial (Sede)
        transportadora.end_com_cep         = request.form.get('end_com_cep', '').strip()
        transportadora.end_com_logradouro  = request.form.get('end_com_logradouro', '').strip().upper()
        transportadora.end_com_numero      = request.form.get('end_com_numero', '').strip().upper()
        transportadora.end_com_complemento = request.form.get('end_com_complemento', '').strip().upper()
        transportadora.end_com_bairro      = request.form.get('end_com_bairro', '').strip().upper()
        transportadora.end_com_cidade      = request.form.get('end_com_cidade', '').strip().upper()
        transportadora.end_com_uf          = request.form.get('end_com_uf', '').strip().upper()

        # Endereço Entrega (Coleta)
        transportadora.end_ent_cep         = request.form.get('end_ent_cep', '').strip()
        transportadora.end_ent_logradouro  = request.form.get('end_ent_logradouro', '').strip().upper()
        transportadora.end_ent_numero      = request.form.get('end_ent_numero', '').strip().upper()
        transportadora.end_ent_complemento = request.form.get('end_ent_complemento', '').strip().upper()
        transportadora.end_ent_bairro      = request.form.get('end_ent_bairro', '').strip().upper()
        transportadora.end_ent_cidade      = request.form.get('end_ent_cidade', '').strip().upper()
        transportadora.end_ent_uf          = request.form.get('end_ent_uf', '').strip().upper()

        # Logística (Checkboxes)
        transportadora.modal_transporte = ",".join(request.form.getlist('modal_transporte')).upper()
        transportadora.tipo_servico     = ",".join(request.form.getlist('tipo_servico')).upper()
        
        prazo_raw = request.form.get('prazo_entrega', '').strip()
        transportadora.prazo_entrega    = int(prazo_raw) if prazo_raw.isdigit() else 0
        transportadora.avaliacao        = request.form.get('avaliacao', 'B').strip().upper()
        
        transportadora.coleta_origem    = request.form.get('coleta_origem', 'NAO').strip().upper()
        transportadora.entrega_final    = request.form.get('entrega_final', 'NAO').strip().upper()
        transportadora.coleta_veiculos  = ",".join(request.form.getlist('coleta_veiculos')).upper()
        transportadora.entrega_veiculos = ",".join(request.form.getlist('entrega_veiculos')).upper()
        entregador_final_opcao = request.form.get('entregador_final_opcao', 'NAO SE APLICA').strip().upper()
        if entregador_final_opcao == 'ENTREGADOR':
            transportadora.entregador_final = request.form.get('entregador_final', '').strip().upper()
        else:
            transportadora.entregador_final = 'NAO SE APLICA'

        # Contato Adicional
        transportadora.contato_nome  = request.form.get('contato_nome', '').strip().upper()
        transportadora.contato_cargo = request.form.get('contato_cargo', '').strip().upper()
        p_desde_raw = request.form.get('parceira_desde', '').strip()
        if p_desde_raw:
            try: transportadora.parceira_desde = datetime.strptime(p_desde_raw, '%Y-%m-%d').date()
            except: pass

        # Financeiro
        transportadora.prazo_pagamento = request.form.get('prazo_pagamento', '').strip()
        transportadora.forma_pagamento = request.form.get('forma_pagamento', '').strip()
        transportadora.tabela_frete    = request.form.get('tabela_frete', '').strip().upper()
        transportadora.banco_nome      = request.form.get('banco_nome', '').strip().upper()
        transportadora.banco_codigo    = request.form.get('banco_codigo', '').strip().upper()
        transportadora.banco_agencia   = request.form.get('banco_agencia', '').strip().upper()
        transportadora.banco_conta     = request.form.get('banco_conta', '').strip().upper()
        transportadora.pix_chave       = request.form.get('pix_chave', '').strip()

        transportadora.observacoes = request.form.get('observacoes', '').strip()
        transportadora.rotas_data  = request.form.get('rotas_json', '[]')
        transportadora.ativo       = request.form.get('ativo') == 'on' or request.form.get('ativo') == '1' or 'ativo' not in request.form

        # 🛡️ AriOne Anti-Duplicidade: Verifica se o CNPJ/CPF já existe (Ignora placeholders SN-)
        if transportadora.cnpj_cpf and not transportadora.cnpj_cpf.startswith('SN-'):
            existente = Transportadora.query.filter(Transportadora.cnpj_cpf == transportadora.cnpj_cpf, Transportadora.id != transportadora.id).first()
            if existente:
                db.session.rollback()
                msg = f"O CNPJ/CPF '{transportadora.cnpj_cpf}' já está cadastrado para a transportadora '{existente.razao_social}'."
                if is_modal or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({'ok': False, 'msg': msg})
                flash(msg, "danger")
                return redirect(url_for('cadastros.form_transportadora', id=id) if id else url_for('cadastros.form_transportadora'))

        try:
            db.session.commit()
            flash(f"Transportadora '{transportadora.razao_social}' salva com sucesso!", "success")
            
            if is_modal or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({
                    'ok': True, 
                    'msg': 'Salvo com sucesso', 
                    'id': transportadora.id,
                    'nome': transportadora.razao_social
                })
                
            return redirect(url_for('cadastros.form_transportadora', id=transportadora.id))
        except Exception as e:
            db.session.rollback()
            flash(f"Erro ao salvar transportadora: {str(e)}", "danger")
            if is_modal or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'ok': False, 'msg': str(e)}), 500

    from app.models.cadastros.entregador import Entregador
    from app.models.cadastros.funcionario import Cargo
    entregadores_lista = Entregador.query.order_by(Entregador.nome).all()
    cargos_lista = Cargo.query.order_by(Cargo.nome).all()

    return render_template(
        'operacoes/cards/expedicao/form_transportadora.html',
        transportadora=transportadora,
        transportadoras_lista=transportadoras_lista,
        docs=docs,
        is_modal=is_modal,
        entregadores_lista=entregadores_lista,
        cargos_lista=cargos_lista,
    )


# ── Inativar Transportadora ─────────────────────────────────────────────────
@cadastros_bp.route('/transportadoras/inativar/<int:id>', methods=['POST'])
@login_required
def inativar_transportadora(id):
    from app.models.cadastros.transportadora import Transportadora
    transportadora = Transportadora.query.get_or_404(id)
    try:
        transportadora.ativo = False
        db.session.commit()
        flash(f'Transportadora "{transportadora.razao_social}" inativada com sucesso.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao inativar transportadora: {str(e)}', 'danger')
    return redirect(url_for('cadastros.form_transportadora', id=id))


# ── Reativar Transportadora ─────────────────────────────────────────────────
@cadastros_bp.route('/transportadoras/reativar/<int:id>', methods=['POST'])
@login_required
def reativar_transportadora(id):
    from app.models.cadastros.transportadora import Transportadora
    transportadora = Transportadora.query.get_or_404(id)
    try:
        transportadora.ativo = True
        db.session.commit()
        flash(f'Transportadora "{transportadora.razao_social}" reativada com sucesso.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao reativar transportadora: {str(e)}', 'danger')
    return redirect(url_for('cadastros.form_transportadora', id=id))


# ── Excluir Documento de Transportadora ─────────────────────────────────────
@cadastros_bp.route('/transportadoras/<int:id>/doc/excluir/<nome>', methods=['POST'])
def excluir_doc_transportadora(id, nome):
    nome_seguro = secure_filename(nome)
    caminho     = os.path.join(_pasta_transportadora(id), nome_seguro)
    if os.path.isfile(caminho):
        os.remove(caminho)
        flash(f'Documento "{nome_seguro}" removido.', 'success')
    else:
        flash('Documento não encontrado.', 'warning')
    return redirect(url_for('cadastros.form_transportadora', id=id))


# ══════════════════════════════════════════════════════════════════════════════
# PRODUTOS
# ══════════════════════════════════════════════════════════════════════════════

@cadastros_bp.route('/produtos/fragmento/<path:filename>')
@login_required
def fragmento_produto(filename):
    """Rota Master para carregar fragmentos de composição (Mprim, Acess, etc)"""
    try:
        return render_template(f'cadastros/cards/catalogos/{filename}')
    except Exception as e:
        return f"Erro ao carregar fragmento: {str(e)}", 404

@cadastros_bp.route('/produtos/limpeza-total-debug')
@login_required
def limpeza_total_produtos():
    """Rota de emergência para limpar o catálogo de testes"""
    try:
        from app.models.catalogos import Produto, ProdutoVariacao, ProdutoComposicao
        db.session.query(ProdutoComposicao).delete()
        db.session.query(ProdutoVariacao).delete()
        db.session.query(Produto).delete()
        db.session.commit()
        return "<h1>✅ Catálogo Limpo!</h1><p>Todos os produtos, variações e composições foram removidos. Pode voltar ao formulário agora.</p><a href='/cadastros/abas?aba=catalogos'>Voltar ao Sistema</a>"
    except Exception as e:
        db.session.rollback()
        return f"<h1>❌ Erro na limpeza</h1><p>{str(e)}</p>"

@cadastros_bp.route('/produtos/cards/form', methods=['GET', 'POST'])
@cadastros_bp.route('/produtos/cards/form/<int:id>', methods=['GET', 'POST'])
@login_required
def form_produto(id=None):
    """Formulário de cadastro/edição de produto (Golden Standard AJAX)"""
    produto = Produto.query.get(id) if id else None

    
    # Dados para os selects
    categorias = Categoria.query.filter_by(ativa=True).all()
    subcategorias = Subcategoria.query.filter_by(ativa=True).all()
    marcas = Marca.query.filter_by(ativa=True).all()
    unidades = UnidadeMedida.query.all()
    
    from app.models.cadastros.fornecedor import Fornecedor
    fornecedores = Fornecedor.query.filter_by(ativo=True).all()
    from sqlalchemy.orm import joinedload
    depositos_lista = Deposito.query.filter_by(ativa=True).options(joinedload(Deposito.prateleiras)).all()
    
    cores_catalogo = CorCatalogo.query.order_by(CorCatalogo.nome).all()
    tamanhos_catalogo = TamanhoCatalogo.query.order_by(TamanhoCatalogo.ordem, TamanhoCatalogo.nome).all()
    from app.models.catalogos import GradeModelo, AtributoCatalogo, ModeloCatalogo
    grades_modelos = GradeModelo.query.order_by(GradeModelo.nome).all()
    atributos_catalogo = AtributoCatalogo.query.filter_by(ativa=True).order_by(AtributoCatalogo.nome).all()
    modelos_lista = ModeloCatalogo.query.filter_by(ativa=True).order_by(ModeloCatalogo.nome).all()
    from app.models.catalogos import TipoMateriaPrima
    tipos_list = TipoMateriaPrima.query.filter_by(ativa=True).order_by(TipoMateriaPrima.nome).all()
    
    # Dicionário para automação no Frontend: { "Depósito A": ["P1", "P2"], ... }
    mapeamento_prateleiras = { d.nome.strip(): [p.nome.strip() for p in d.prateleiras] for d in depositos_lista }
    
    if request.method == 'POST':
        def clean_money(val):
            if not val: return 0.0
            return float(val.replace('R$', '').replace('.', '').replace(',', '.').strip())

        def clean_float(val):
            if not val: return 0.0
            try:
                if isinstance(val, str):
                    return float(val.replace(',', '.').strip())
                return float(val)
            except:
                return 0.0

        def to_bool(val):
            return val in ['1', 'on', 'true', True]

        try:
            descricao = request.form.get('descricao', '').strip()
            cod_interno = request.form.get('cod_interno', '').strip()
            referencia = request.form.get('referencia', '').strip()

            # 🛡️ Validação de Integridade AriOne Master: Evitar Duplicidade (Ignora o próprio registro na edição)
            # Usamos ilike e cast de ID para garantir que edições não sejam bloqueadas
            target_id = int(id) if id else None
            
            # 🛡️ Cadeado de Integridade AriOne (Descrição + Atributo)
            target_id = int(id) if id else None
            # Se o ID não veio pela URL, tentamos pegar do formulário (AJAX padrão)
            if not target_id:
                form_id = request.form.get('id')
                if form_id and form_id != 'new' and form_id != 'None':
                    target_id = int(form_id)

            atributo_id = request.form.get('tipo_material_id')
            
            if descricao:
                # Se tem atributo, a unicidade é Descrição + Atributo. Se não tem, é só Descrição.
                query = Produto.query.filter(Produto.descricao.ilike(descricao))
                if atributo_id and atributo_id != 'None' and atributo_id != '':
                    query = query.filter(Produto.tipo_material_id == atributo_id)
                
                # Ignora o próprio produto se for uma edição
                if target_id:
                    query = query.filter(Produto.id != target_id)
                
                existente = query.first()
                
                if existente:
                    msg = f'Já existe um produto "{descricao}"'
                    if atributo_id and atributo_id != 'None' and atributo_id != '':
                        # Busca o nome do atributo para uma mensagem mais clara
                        from app.models.catalogos import TipoMateriaPrima
                        at = TipoMateriaPrima.query.get(atributo_id)
                        if at: msg += f' com o atributo "{at.nome}"'
                    return jsonify({'success': False, 'message': f'{msg}. Verifique o cadastro.'}), 400
            
            # 🛡️ Cadeado de EAN (Código de Barras)
            cod_barras = request.form.get('cod_barras', '').strip()
            if cod_barras:
                existente_ean = Produto.query.filter(Produto.cod_barras == cod_barras).filter(Produto.id != target_id if target_id else True).first()
                if existente_ean:
                    return jsonify({'success': False, 'message': f'O Código de Barras "{cod_barras}" já está cadastrado no produto ID {existente_ean.id}.'}), 400
            
            if cod_interno:
                existente_cod = Produto.query.filter(Produto.cod_interno.ilike(cod_interno)).filter(Produto.id != target_id if target_id else True).first()
                if existente_cod:
                    return jsonify({'success': False, 'message': f'O Código Interno "{cod_interno}" já está em uso.'}), 400

            if not produto:
                produto = Produto()
                db.session.add(produto)
            
            # Identificação
            produto.descricao = descricao
            produto.tipo_item = request.form.get('tipo_item')
            produto.cod_barras = request.form.get('cod_barras')
            produto.cod_interno = cod_interno
            produto.referencia = referencia
            produto.origem_produto = request.form.get('origem_produto')
            produto.regra_cod_interno = request.form.get('regra_cod_interno')
            produto.tipo_material_id = request.form.get('tipo_material_id')
            produto.unidade = request.form.get('unidade')
            produto.peso = clean_float(request.form.get('peso'))
            produto.categoria = request.form.get('categoria')
            produto.subcategoria = request.form.get('subcategoria')
            produto.marca = request.form.get('marca')
            produto.modelo = request.form.get('modelo')
            produto.fornecedor = request.form.get('fornecedor')
            produto.dim_comprimento = clean_float(request.form.get('dim_comprimento'))
            produto.dim_largura = clean_float(request.form.get('dim_largura'))
            produto.dim_altura = clean_float(request.form.get('dim_altura'))
            produto.tags = request.form.get('tags')
            
            # Preços
            produto.preco_custo = clean_money(request.form.get('preco_custo'))
            produto.preco_varejo = clean_money(request.form.get('preco_varejo'))
            produto.preco_atacado = clean_money(request.form.get('preco_atacado'))
            produto.preco_promocional = clean_money(request.form.get('preco_promocional'))
            
            # Estoque
            produto.tipo_estoque = request.form.get('tipo_estoque', 'unico')
            produto.estoque_atual = clean_float(request.form.get('estoque_atual'))
            produto.estoque_minimo = clean_float(request.form.get('estoque_minimo'))
            produto.qtd_min_varejo = int(request.form.get('qtd_min_varejo', 1) or 1)
            produto.qtd_min_atacado = int(request.form.get('qtd_min_atacado', 10) or 10)
            produto.deposito = request.form.get('deposito')
            produto.prateleira = request.form.get('prateleira')
            produto.mov_estoque = to_bool(request.form.get('mov_estoque'))
            
            # 🛡️ Integridade AriOne: Controle de Engenharia
            produto.has_composicao = to_bool(request.form.get('has_composicao'))
            if not produto.has_composicao:
                produto.mov_estoque_composicao = False
                produto.composicao = {} # Limpa dados de engenharia (Dict Vazio para JSON)
            else:
                produto.mov_estoque_composicao = to_bool(request.form.get('mov_estoque_composicao'))
            
            # Fiscal
            produto.ncm = request.form.get('ncm')
            produto.cest = request.form.get('cest')
            produto.cfop = request.form.get('cfop')
            produto.origem = request.form.get('origem', '0')
            produto.cst = request.form.get('cst')
            produto.aliq_icms = clean_float(request.form.get('aliq_icms'))
            produto.aliq_pis = clean_float(request.form.get('aliq_pis'))
            produto.aliq_cofins = clean_float(request.form.get('aliq_cofins'))
            produto.aliq_ipi = clean_float(request.form.get('aliq_ipi'))
            produto.mva = clean_float(request.form.get('mva'))
            produto.base_st = clean_float(request.form.get('base_st'))
            
            # Regras
            produto.permite_desconto = to_bool(request.form.get('permite_desconto'))
            produto.desconto_maximo = float(request.form.get('desconto_maximo', 0.0) or 0.0)
            produto.vender_sem_estoque = to_bool(request.form.get('vender_sem_estoque'))
            produto.exige_obs_venda = to_bool(request.form.get('exige_obs_venda'))
            produto.imprimir_nfe = to_bool(request.form.get('imprimir_nfe'))
            produto.gerar_etiqueta = to_bool(request.form.get('gerar_etiqueta'))
            produto.ativo = to_bool(request.form.get('ativo'))

            # Grade (Matrix Master)
            produto.grade_id = request.form.get('grade_id')
            produto.grade_cores = request.form.getlist('grade_cores')
            produto.grade_tamanhos = request.form.getlist('grade_tamanhos')
            produto.grade_label_adicional = request.form.get('grade_label_adicional')
            produto.grade_valores_adicional = request.form.getlist('grade_valores_adicional')
            
            # Grade Matrix (JSON da Matriz)
            matrix_json = request.form.get('matrix_json')
            if matrix_json:
                try:
                    produto.grade_matrix = json.loads(matrix_json)
                except Exception as je:
                    print(f"Erro ao parsear matrix_json: {je}")

            # Composicao (JSON)
            comp_json = request.form.get('matrix_json') # Reuso do JSON da matriz para extrair variações
            composicao_json = request.form.get('composicao_json')

            if composicao_json:
                try:
                    produto.composicao = json.loads(composicao_json)
                except:
                    pass

            # 🚀 Upload de Imagens do Produto
            if 'imagens' in request.files:
                imagens = request.files.getlist('imagens')
                if imagens and imagens[0].filename:
                    # Salva a primeira imagem como foto principal
                    foto_principal = imagens[0]
                    if foto_principal and foto_principal.filename:
                        pasta = os.path.join('static', 'uploads', 'produtos')
                        os.makedirs(pasta, exist_ok=True)
                        ext = foto_principal.filename.rsplit('.', 1)[1].lower()
                        nome_foto = f"prod_{produto.id}_principal.{ext}"
                        caminho_foto = os.path.join(pasta, nome_foto)
                        foto_principal.save(caminho_foto)
                        produto.foto = f"uploads/produtos/{nome_foto}"

            # 🛡️ SINCRONIZACAO RELACIONAL ARIONE
            try:
                from app.models.catalogos import ProdutoVariacao, ProdutoComposicao
                
                # 1. Limpa variações e composições antigas para reconstrução íntegra
                ProdutoVariacao.query.filter_by(produto_id=produto.id).delete()
                ProdutoComposicao.query.filter_by(produto_id=produto.id).delete()
                db.session.flush() # Força a limpeza antes de recriar

                # Função auxiliar para persistir itens (Refinada para AriOne Master)
                def persistir_itens(v_id, c_data):
                    for item in c_data:
                        try:
                            # Limpeza robusta de valores monetários (Padrão clean_money)
                            raw_custo = str(item.get('custo') or '0')
                            v_custo = float(raw_custo.replace('R$', '').replace('.', '').replace(',', '.').strip())
                            
                            raw_qtd = str(item.get('qtd') or '0')
                            v_qtd = float(raw_qtd.replace(',', '.').strip())
                            
                            db.session.add(ProdutoComposicao(
                                produto_id=produto.id, variacao_id=v_id,
                                tipo_componente=item.get('tipo'), 
                                item_id=item.get('id'), # Agora capturando o ID real do item
                                nome=item.get('nome'), 
                                unidade=item.get('unidade'),
                                custo_unitario=v_custo, 
                                quantidade=v_qtd, 
                                total_custo=v_custo * v_qtd
                            ))
                        except Exception as e_item:
                            print(f"⚠️ Erro ao persistir item de composição: {e_item}")
                            continue

                # 2. Processamento por tipo de estoque
                if produto.tipo_estoque == 'grade' and produto.grade_matrix:
                    for key, data in produto.grade_matrix.items():
                        parts = key.split('|')
                        variacao = ProdutoVariacao(
                            produto_id=produto.id,
                            sku=data.get('sku') or f"{produto.referencia or produto.id}-{key.replace('|', '-')}",
                            cor=parts[0] if len(parts) > 0 else None,
                            tamanho=parts[1] if len(parts) > 1 else None,
                            atributo=parts[2] if len(parts) > 2 else None,
                            estoque_atual=float(data.get('estoque') or 0),
                            preco_venda=float(data.get('varejo') or 0)
                        )
                        db.session.add(variacao)
                        db.session.flush()
                        
                        ctx_key = variacao.tamanho if variacao.tamanho else 'GERAL'
                        comp_data = (produto.composicao or {}).get(ctx_key) or (produto.composicao or {}).get('GERAL')
                        if comp_data: persistir_itens(variacao.id, comp_data)
                else:
                    # Produto Único
                    variacao_mestre = ProdutoVariacao(
                        produto_id=produto.id,
                        sku=produto.referencia or f"PROD-{produto.id}",
                        estoque_atual=produto.estoque_atual or 0,
                        preco_venda=produto.preco_varejo or 0
                    )
                    db.session.add(variacao_mestre)
                    db.session.flush()
                    comp_data = (produto.composicao or {}).get('GERAL')
                    if comp_data: persistir_itens(variacao_mestre.id, comp_data)

                db.session.commit()
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({'success': True, 'message': 'Produto e Engenharia salvos com sucesso!', 'id': produto.id})
                
                flash('Produto e Engenharia salvos com sucesso!', 'success')
                return redirect(url_for('cadastros.form_produto', id=produto.id))
            except Exception as e_sync:
                db.session.rollback()
                print(f"❌ Erro na Sincronização Relacional: {str(e_sync)}")
                return jsonify({'success': False, 'message': f'Erro ao sincronizar variações: {str(e_sync)}'}), 500
            
            # ── GARANTIA DE ID E PERSISTÊNCIA ──
            try:
                # 0. Garante que o produto está na sessão
                if produto not in db.session:
                    db.session.add(produto)
                
                # ── Correção Forçada de Código e SKU (REFORÇADA) ──
                import re
                cod = str(produto.cod_interno or "").strip().upper()
                
                # Sempre garante que a categoria e o ID estejam presentes se for regra automática
                if not cod or cod == "AUTOMÁTICO" or cod.count('-') < 3:
                    try:
                        origem = request.form.get('origem_produto', '')
                        material_id = request.form.get('tipo_material_id')
                        cat_nome = request.form.get('categoria', '')
                        
                        p1 = "FP" if "propria" in (str(origem) or "").lower() else "PR"
                        mat = TipoMateriaPrima.query.get(material_id) if material_id else None
                        
                        def get_sigla_simples(t):
                            if not t: return "MP"
                            w = [x for x in str(t).split() if len(x) > 2]
                            return (w[0][0] + (w[1][0] if len(w) > 1 else w[0][1])).upper() if len(w) >= 1 else "MP"

                        p2 = get_sigla_simples(mat.nome) if mat else "MP"
                        p3 = str(cat_nome or "X").strip().upper()[0]
                        
                        produto.cod_interno = f"{p1}-{p2}-{p3}-{produto.id}" 
                    except Exception as ge:
                        print(f"Erro na geração do código: {ge}")
                        produto.cod_interno = f"PROD-{produto.id}"
                
                # 2. Sincroniza Referência
                produto.referencia = produto.cod_interno
                
                db.session.commit()
                print(f"✅ Produto {produto.id} salvo com sucesso: {produto.cod_interno}")
            except Exception as e:
                db.session.rollback()
                print(f"❌ ERRO CRÍTICO AO SALVAR: {e}")
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.form.get('partial_save'):
                    return jsonify({'success': False, 'message': f"Erro no Banco: {str(e)}"}), 500
                flash(f"Erro ao salvar: {str(e)}", 'danger')
                return redirect(url_for('cadastros.form_produto', id=produto.id if produto else None))
            
            # Se for salvamento parcial, retornamos sucesso imediato sem recarregar tudo
            if request.form.get('partial_save'):
                return jsonify({
                    'success': True, 
                    'message': f'Seção {request.form.get("partial_save")} salva!', 
                    'id': produto.id,
                    'cod_interno': produto.cod_interno
                })

            flash(f'Produto "{produto.descricao}" salvo com sucesso!', 'success')
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                from flask import current_app
                cores_catalogo = CorCatalogo.query.order_by(CorCatalogo.nome).all()
                tamanhos_catalogo = TamanhoCatalogo.query.order_by(TamanhoCatalogo.nome).all()
                grades_modelos = GradeModelo.query.order_by(GradeModelo.nome).all()
                atributos_catalogo = AtributoCatalogo.query.filter_by(ativa=True).order_by(AtributoCatalogo.nome).all()
                produtos = Produto.query.order_by(Produto.id.desc()).all()
                return render_template('cadastros/cards/catalogos/form_produto.html', 
                                     produto=produto, 
                                     categorias=categorias, 
                                     subcategorias=subcategorias, marcas=marcas, 
                                     unidades=unidades, fornecedores=fornecedores,
                                     depositos_lista=depositos_lista,
                                     cores_catalogo=cores_catalogo,
                                     tamanhos_catalogo=tamanhos_catalogo,
                                     grades_modelos=grades_modelos,
                                     atributos_catalogo=atributos_catalogo,
                                     modelos_lista=modelos_lista, 
                                     tipos_list=tipos_list, mapeamento_prateleiras=mapeamento_prateleiras,
                                     produtos=produtos)
            
            return redirect(url_for('cadastros.form_produto', id=produto.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao salvar produto: {str(e)}', 'danger')
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.form.get('partial_save'):
                return jsonify({'success': False, 'message': str(e)}), 500
            return redirect(url_for('cadastros.form_produto'))

    produtos = Produto.query.order_by(Produto.id.desc()).all()
    return render_template('cadastros/cards/catalogos/form_produto.html', 
                         produto=produto, categorias=categorias, 
                         subcategorias=subcategorias, marcas=marcas, 
                         unidades=unidades, fornecedores=fornecedores,
                         depositos_lista=depositos_lista,
                         cores_catalogo=cores_catalogo,
                         tamanhos_catalogo=tamanhos_catalogo,
                         grades_modelos=grades_modelos,
                         atributos_catalogo=atributos_catalogo,
                         modelos_lista=modelos_lista, 
                         tipos_list=tipos_list,
                         produtos=produtos)

@cadastros_bp.route('/produtos/duplicar/<int:id>')
@login_required
def duplicar_produto(id):
    p_origem = Produto.query.get_or_404(id)
    
    try:
        # Cria cópia básica
        p_novo = Produto(
            descricao=p_origem.descricao + " (CÓPIA)",
            referencia=p_origem.referencia + "-COPY" if p_origem.referencia else None,
            tipo_material_id=p_origem.tipo_material_id,
            unidade=p_origem.unidade,
            categoria=p_origem.categoria,
            subcategoria=p_origem.subcategoria,
            marca=p_origem.marca,
            modelo=p_origem.modelo,
            origem_produto=p_origem.origem_produto,
            preco_custo=p_origem.preco_custo,
            preco_varejo=p_origem.preco_varejo,
            preco_atacado=p_origem.preco_atacado,
            preco_distribuidor=p_origem.preco_distribuidor,
            ncm=p_origem.ncm,
            cest=p_origem.cest,
            cst=p_origem.cst,
            origem=p_origem.origem,
            tipo_item=p_origem.tipo_item,
            peso=p_origem.peso,
            dim_comprimento=p_origem.dim_comprimento,
            dim_largura=p_origem.dim_largura,
            dim_altura=p_origem.dim_altura,
            mov_estoque=p_origem.mov_estoque,
            mov_estoque_composicao=p_origem.mov_estoque_composicao,
            tags=p_origem.tags,
            composicao=p_origem.composicao, # Copia o JSON da composição
            grade_id=p_origem.grade_id,
            grade_cores=p_origem.grade_cores,
            grade_tamanhos=p_origem.grade_tamanhos,
            grade_valores_adicional=p_origem.grade_valores_adicional,
            ativo=True
        )
        
        db.session.add(p_novo)
        db.session.commit()
        
        # Copia Variacoes (SKUs) se existirem
        from app.models.catalogos import ProdutoVariacao
        vars_origem = ProdutoVariacao.query.filter_by(produto_id=id).all()
        for v in vars_origem:
            v_nova = ProdutoVariacao(
                produto_id=p_novo.id,
                sku=None, # Gera novo no salvamento
                cor=v.cor,
                tamanho=v.tamanho,
                preco_venda=v.preco_venda,
                custo_bruto=v.custo_bruto,
                fator=v.fator,
                estoque_min=v.estoque_min,
                estoque_max=v.estoque_max,
                ativa=True
            )
            db.session.add(v_nova)
        
        db.session.commit()
        flash(f"Produto #{id} duplicado com sucesso para #{p_novo.id}!", "success")
        return redirect(url_for('cadastros.form_produto', id=p_novo.id))
        
    except Exception as e:
        db.session.rollback()
        flash(f"Erro ao duplicar produto: {str(e)}", "danger")
        return redirect(url_for('cadastros.form_produto', id=id))

# ── EXPORTAÇÃO DE PRODUTOS (DOWLOAD) ──
@cadastros_bp.route('/produtos/exportar')
@login_required
def exportar_produtos():
    try:
        produtos = Produto.query.filter_by(ativo=True).all()
        
        output = io.StringIO()
        # Adiciona BOM para o Excel abrir com UTF-8 corretamente
        output.write('\ufeff')
        
        # AriOne Standard: Delimitador ponto-e-vírgula para compatibilidade Excel PT-BR
        writer = csv.writer(output, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        
        # Header
        writer.writerow(['ID', 'DESCRICAO', 'SKU_INTERNO', 'REFERENCIA', 'CATEGORIA', 'UNIDADE', 'PRECO_CUSTO', 'PRECO_VAREJO', 'NCM', 'EAN'])
        
        for p in produtos:
            writer.writerow([
                p.id,
                p.descricao or '',
                p.cod_interno or '',
                p.referencia or '',
                p.categoria or '',
                p.unidade or '',
                f"{p.preco_custo or 0:.2f}".replace('.', ','),
                f"{p.preco_varejo or 0:.2f}".replace('.', ','),
                p.ncm or '',
                p.cod_barras or ''
            ])
        
        # O .getvalue() já pega tudo, incluindo o BOM que escrevemos no início
        return Response(
            output.getvalue(),
            mimetype="text/csv",
            headers={"Content-disposition": "attachment; filename=produtos_arione_export.csv"}
        )
    except Exception as e:
        flash(f"Erro ao exportar: {str(e)}", "danger")
        return redirect(url_for('cadastros.form_produto'))

# ── IMPORTAÇÃO DE PRODUTOS (UPLOAD) ──
@cadastros_bp.route('/produtos/importar', methods=['POST'])
@login_required
def importar_produtos():
    if 'arquivo' not in request.files:
        return jsonify({'success': False, 'message': 'Nenhum arquivo enviado.'}), 400
    
    file = request.files['arquivo']
    if file.filename == '':
        return jsonify({'success': False, 'message': 'Arquivo selecionado está vazio.'}), 400

    try:
        # Lê o conteúdo e converte para string
        content = file.stream.read().decode("utf-8-sig") # utf-8-sig lida com BOM do Excel
        stream = io.StringIO(content)
        
        # Detecta delimitador
        sample = stream.read(2048)
        stream.seek(0)
        sniffer = csv.Sniffer()
        dialect = sniffer.sniff(sample) if sample else csv.excel
        
        reader = csv.DictReader(stream, dialect=dialect)
        
        count_new = 0
        count_upd = 0
        for row in reader:
            # Normaliza chaves (maiusculas/minusculas)
            row = {k.upper(): v for k, v in row.items()}
            
            descricao = row.get('DESCRICAO')
            sku = row.get('SKU_INTERNO')
            if not descricao: continue
            
            # Busca se já existe para fazer Update em vez de Create (Smart Sync)
            p = None
            if sku:
                p = Produto.query.filter_by(cod_interno=sku, ativo=True).first()
            
            if p:
                # Atualiza existente
                p.descricao = descricao
                p.referencia = row.get('REFERENCIA') or p.referencia
                p.categoria = row.get('CATEGORIA') or p.categoria
                p.unidade = row.get('UNIDADE') or p.unidade
                if row.get('PRECO_CUSTO'):
                    p.preco_custo = float(row.get('PRECO_CUSTO').replace(',', '.'))
                if row.get('PRECO_VAREJO'):
                    p.preco_varejo = float(row.get('PRECO_VAREJO').replace(',', '.'))
                count_upd += 1
            else:
                # Cria novo
                p = Produto(
                    descricao=descricao,
                    cod_interno=sku,
                    referencia=row.get('REFERENCIA'),
                    categoria=row.get('CATEGORIA'),
                    unidade=row.get('UNIDADE', 'UN'),
                    preco_custo=float(row.get('PRECO_CUSTO', '0').replace(',', '.')) if row.get('PRECO_CUSTO') else 0,
                    preco_varejo=float(row.get('PRECO_VAREJO', '0').replace(',', '.')) if row.get('PRECO_VAREJO') else 0,
                    ativo=True
                )
                db.session.add(p)
                count_new += 1
            
        db.session.commit()
        return jsonify({'success': True, 'message': f'Integração Concluída: {count_new} novos e {count_upd} atualizados.'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Falha na integração: {str(e)}'}), 500

@cadastros_bp.route('/produtos/proximo-sequencial-interno')
@login_required
def proximo_sequencial_interno():
    prefixo = request.args.get('prefixo', '')
    if not prefixo: return jsonify({'proximo': 1})
    
    from app.models.catalogos import Produto
    produtos = Produto.query.filter(Produto.cod_interno.like(f"{prefixo}%")).all()
    
    if not produtos: return jsonify({'proximo': 1})
        
    numeros = []
    for p in produtos:
        if not p.cod_interno: continue
        try:
            # Remove o prefixo e o hífen inicial se houver
            num_str = p.cod_interno[len(prefixo):]
            if num_str.startswith('-'):
                num_str = num_str[1:]
            
            if num_str.isdigit():
                numeros.append(int(num_str))
        except Exception:
            pass
            
    proximo = max(numeros) + 1 if numeros else 1
    return jsonify({'proximo': proximo})


@cadastros_bp.route('/produtos/cards/inativar/<int:id>', methods=['POST'])
@login_required
def inativar_produto(id):
    """Inativa um produto"""
    produto = Produto.query.get_or_404(id)
    produto.ativo = False
    db.session.commit()
    flash(f'Produto "{produto.descricao}" inativado.', 'success')
    return redirect(url_for('cadastros.form_produto', id=id))


@cadastros_bp.route('/produtos/cards/reativar/<int:id>', methods=['POST'])
@login_required
def reativar_produto(id):
    """Reativa um produto"""
    produto = Produto.query.get_or_404(id)
    produto.ativo = True
    db.session.commit()
    flash(f'Produto "{produto.descricao}" reativado!', 'success')
    return redirect(url_for('cadastros.form_produto', id=id))


@cadastros_bp.route('/produtos/excluir/<int:id>', methods=['POST'])
@login_required
def excluir_produto(id):
    """Exclui um produto se não houver movimentações"""
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    produto = Produto.query.get_or_404(id)
    
    # 1. Proteção de Estoque (Movimentação Simples)
    if (produto.estoque_atual or 0) != 0:
        msg = f'❌ Bloqueio de Segurança: O produto "{produto.descricao}" possui saldo em estoque ({produto.estoque_atual}). Para manter a integridade, inative o item em vez de excluí-lo.'
        if is_ajax: return jsonify({'success': False, 'message': msg})
        flash(msg, 'warning')
        return redirect(url_for('cadastros.form_produto'))

    # 2. Tentativa de Exclusão Física (O Banco de Dados barrou via FK se houver vínculos)
    try:
        nome_removido = produto.descricao
        db.session.delete(produto)
        db.session.commit()
        msg = f'✅ Produto "{nome_removido}" removido definitivamente do catálogo.'
        if is_ajax: return jsonify({'success': True, 'message': msg})
        flash(msg, 'success')
    except Exception as e:
        db.session.rollback()
        msg = f'🚫 Não foi possível excluir: Este item já possui histórico de movimentações ou vínculos em outros módulos. Sugerimos usar a opção "Inativar".'
        if is_ajax: return jsonify({'success': False, 'message': msg})
        flash(msg, 'danger')
        
    return redirect(url_for('cadastros.form_produto'))


@cadastros_bp.route('/produtos/pesquisa')
@login_required
def pesquisa_produtos():
    q = request.args.get('q', '').strip()
    if len(q) < 2: return jsonify([])
    
    produtos = Produto.query.filter(
        (Produto.descricao.ilike(f'%{q}%')) | 
        (Produto.cod_interno.ilike(f'%{q}%')) |
        (Produto.cod_barras.ilike(f'%{q}%'))
    ).limit(20).all()
    
    return jsonify([{
        'id': p.id,
        'descricao': p.descricao,
        'tipo': p.tipo_item,
        'preco': p.preco_varejo,
        'preco_custo': p.preco_custo,
        'unidade': p.unidade,
        'ativo': p.ativo
    } for p in produtos])


@cadastros_bp.route('/servicos/pesquisa')
@login_required
def pesquisa_servicos():
    q = request.args.get('q', '').strip()
    if len(q) < 2: return jsonify([])
    
    servicos = Servico.query.filter(
        (Servico.descricao.ilike(f'%{q}%')) | 
        (Servico.codigo.ilike(f'%{q}%'))
    ).limit(20).all()
    
    return jsonify([{
        'id': s.id,
        'sku': s.codigo or '',
        'descricao': s.descricao,
        'unidade': s.unidade_medida or 'UN',
        'preco_custo': s.preco_custo or 0.0
    } for s in servicos])

@cadastros_bp.route('/cards/insumos/pesquisa')
@login_required
def pesquisa_insumos():
    q = request.args.get('q', '').strip()
    if len(q) < 2: return jsonify([])
    from app.models.catalogos import Insumo
    insumos = Insumo.query.filter(
        (Insumo.nome.ilike(f'%{q}%')) | 
        (Insumo.sku.ilike(f'%{q}%'))
    ).limit(20).all()
    return jsonify([{
        'id': i.id,
        'sku': i.sku or '',
        'descricao': i.nome,
        'unidade': i.unidade.sigla if i.unidade else 'UN',
        'preco_custo': i.preco_custo or 0.0
    } for i in insumos])


# ══════════════════════════════════════════════════════════════════════════════
# SERVIÇOS
# ══════════════════════════════════════════════════════════════════════════════

@cadastros_bp.route('/servicos/cards/form', methods=['GET', 'POST'])
@cadastros_bp.route('/servicos/cards/form/<int:id>', methods=['GET', 'POST'])
@login_required
def form_servico(id=None):
    """Formulário de cadastro/edição de serviço (Golden Standard AJAX)"""
    servico = Servico.query.get(id) if id else None
    
    if request.method == 'POST':
        def clean_money(val):
            if not val: return 0.0
            return float(val.replace('R$', '').replace('.', '').replace(',', '.').strip())

        try:
            descricao = request.form.get('descricao', '').strip()
            sku = request.form.get('sku', '').strip()

            # 🛡️ Validação de Integridade AriOne: Evitar Duplicidade
            if descricao:
                existente_desc = Servico.query.filter(Servico.descricao == descricao, Servico.id != id).first()
                if existente_desc:
                    msg = f'Já existe um serviço cadastrado com a descrição "{descricao}".'
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return jsonify({'success': False, 'message': msg}), 400
                    flash(msg, 'danger')
                    return render_template('cadastros/cards/catalogos/form_servico.html', servico=servico)
            
            if sku:
                existente_sku = Servico.query.filter(Servico.codigo == sku, Servico.id != id).first()
                if existente_sku:
                    msg = f'O código "{sku}" já está em uso por outro serviço.'
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return jsonify({'success': False, 'message': msg}), 400
                    flash(msg, 'danger')
                    return render_template('cadastros/cards/catalogos/form_servico.html', servico=servico)

            if not servico:
                servico = Servico()
                db.session.add(servico)
            
            servico.descricao = descricao
            servico.categoria = request.form.get('categoria')
            servico.codigo = sku # Usando 'sku' do form para 'codigo'
            servico.observacoes = request.form.get('observacoes')
            servico.unidade_medida = request.form.get('unidade_medida')
            servico.preco_custo = clean_money(request.form.get('preco_custo'))
            servico.preco_venda = clean_money(request.form.get('preco_venda'))
            servico.qtd_minima = float(request.form.get('qtd_minima', 1.0) or 1.0)
            servico.tempo_execucao = request.form.get('tempo_execucao')
            servico.comissao = float(request.form.get('comissao', 0.0) or 0.0)
            servico.descricao_detalhada = request.form.get('descricao_detalhada')
            servico.garantia = request.form.get('garantia')
            servico.validade_proposta = request.form.get('validade_proposta')
            servico.forma_pagamento = request.form.get('forma_pagamento')
            servico.ncm = request.form.get('ncm')
            servico.cest = request.form.get('cest')
            servico.codigo_servico = request.form.get('codigo_servico')
            
            db.session.commit()
            flash(f'Serviço "{servico.descricao}" salvo com sucesso!', 'success')
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return render_template('cadastros/cards/catalogos/form_servico.html', servico=servico)
            
            return redirect(url_for('cadastros.form_servico', id=servico.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao salvar serviço: {str(e)}', 'danger')
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return render_template('cadastros/cards/catalogos/form_servico.html', servico=servico)
    
    servicos = Servico.query.order_by(Servico.descricao).all()
    return render_template('cadastros/cards/catalogos/form_servico.html', servico=servico, servicos=servicos)


@cadastros_bp.route('/servicos/inativar/<int:id>', methods=['POST'])
@login_required
def inativar_servico(id):
    """Inativa um serviço"""
    servico = Servico.query.get_or_404(id)
    servico.ativo = False
    db.session.commit()
    flash(f'Serviço "{servico.descricao}" inativado com sucesso.', 'success')
    return redirect(url_for('cadastros.form_servico', id=id))


@cadastros_bp.route('/servicos/reativar/<int:id>', methods=['POST'])
@login_required
def reativar_servico(id):
    """Reativa um serviço inativo"""
    servico = Servico.query.get_or_404(id)
    servico.ativo = True
    db.session.commit()
    flash(f'Serviço "{servico.descricao}" reativado!', 'success')
    return redirect(url_for('cadastros.form_servico', id=id))


# ── Cores e Tamanhos (Catálogo) ─────────────────────────────────────────────

@cadastros_bp.route('/catalogos/cores/add', methods=['POST'])
@login_required
def add_cor_catalogo():
    data = request.get_json()
    nome = data.get('nome', '').strip()
    cor_hex = data.get('cor_hex', '#CBD5E0')
    
    if not nome:
        return jsonify({'ok': False, 'erro': 'Por favor, digite um nome para a cor.'}), 400
    
    # Busca exata ignorando maiúsculas/minúsculas
    cor_existente = CorCatalogo.query.filter(CorCatalogo.nome.ilike(nome)).first()
    if cor_existente:
        return jsonify({'ok': False, 'erro': f'A cor "{cor_existente.nome}" já está cadastrada no catálogo.'}), 400
    
    try:
        cor = CorCatalogo(nome=nome, cor_hex=cor_hex)
        db.session.add(cor)
        db.session.commit()
        return jsonify({'ok': True, 'nome': nome, 'cor_hex': cor_hex, 'id': cor.id})
    except Exception as e:
        db.session.rollback()
        return jsonify({'ok': False, 'erro': f'Erro ao salvar no banco: {str(e)}'}), 500

@cadastros_bp.route('/cards/cores', methods=['GET', 'POST'])
@cadastros_bp.route('/cards/cores/<int:id>', methods=['GET', 'POST'])
@login_required
def card_cores(id=None):
    cor = CorCatalogo.query.get(id) if id else None
    if request.method == 'POST':
        nome = request.form.get('nome_cor')
        cor_hex = request.form.get('cor_hex', '#CBD5E0')
        if nome:
            if not cor:
                existente = CorCatalogo.query.filter(CorCatalogo.nome.ilike(nome)).first()
                if existente:
                    flash(f'Alerta de Integridade: A cor "{nome}" já existe.', 'warning')
                else:
                    cor = CorCatalogo()
            
            if cor:
                cor.nome = nome
                cor.cor_hex = cor_hex
                cor.ativa = request.form.get('status_cor') == 'ATIVO'
                db.session.add(cor)
                db.session.commit()
                flash('Integridade: Cor salva com sucesso!', 'success')
        
        # AJAX-friendly: Retorna o fragmento do formulário
        return render_template('cadastros/cards/catalogos/form_cores.html', 
                             cores=CorCatalogo.query.order_by(CorCatalogo.nome).all(),
                             cor=cor)
    
    cores = CorCatalogo.query.order_by(CorCatalogo.nome).all()
    return render_template('cadastros/cards/catalogos/form_cores.html', cores=cores, cor=cor)

@cadastros_bp.route('/cards/cores/excluir/<int:id>', methods=['POST'])
@login_required
def excluir_cor_card(id):
    cor = CorCatalogo.query.get_or_404(id)
    if cor.em_uso:
        return jsonify({'success': False, 'message': 'Esta cor está em uso e não pode ser excluída.'}), 400
    try:
        db.session.delete(cor)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Cor excluída com sucesso!'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 400

@cadastros_bp.route('/catalogos/cores/excluir/<int:id>', methods=['POST'])
@login_required
def excluir_cor_catalogo(id):
    cor = CorCatalogo.query.get_or_404(id)
    
    # Verifica se está em uso
    if cor.em_uso:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'ok': False, 'erro': 'Esta cor já está vinculada a produtos e não pode ser excluída.'})
        flash(f'Cor "{cor.nome}" está em uso e não pode ser excluída.', 'danger')
        return redirect(url_for('cadastros.form_produto'))
        
    db.session.delete(cor)
    db.session.commit()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'ok': True})
        
    flash(f'Cor "{cor.nome}" excluída.', 'success')
    return redirect(url_for('cadastros.form_produto'))

@cadastros_bp.route('/catalogos/tamanhos/add', methods=['POST'])
@login_required
def add_tamanho_catalogo():
    data = request.get_json()
    nome = data.get('nome')
    if not nome:
        return jsonify({'ok': False, 'erro': 'Nome é obrigatório'}), 400
    
    if TamanhoCatalogo.query.filter_by(nome=nome).first():
        return jsonify({'ok': False, 'erro': 'Tamanho já existe'}), 400
    
    tam = TamanhoCatalogo(nome=nome)
    db.session.add(tam)
    db.session.commit()
    return jsonify({'ok': True, 'nome': nome, 'id': tam.id})

@cadastros_bp.route('/catalogos/tamanhos/excluir/<int:id>', methods=['POST'])
@login_required
def excluir_tamanho_catalogo(id):
    tam = TamanhoCatalogo.query.get_or_404(id)
    db.session.delete(tam)
    db.session.commit()
    flash(f'Tamanho "{tam.nome}" excluído.', 'success')
    return redirect(url_for('cadastros.form_produto'))

@cadastros_bp.route('/produtos/<int:id>/img/excluir/<nome>', methods=['POST'])
def excluir_img_produto(id, nome):
    flash('Funcionalidade de imagem ainda não implementada.', 'info')
    return redirect(url_for('cadastros.form_produto', id=id))


# ── Rotas AJAX para Cards de Catálogo ──────────────────────────────────────

@cadastros_bp.route('/cards/marcas', methods=['GET', 'POST'])
@cadastros_bp.route('/cards/marcas/<int:id>', methods=['GET', 'POST'])
def card_marcas(id=None):
    marca = Marca.query.get(id) if id else None
    if request.method == 'POST':
        nome = request.form.get('nome_marca')
        if nome:
            if not marca:
                existente = Marca.query.filter_by(nome=nome).first()
                if existente:
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return jsonify({'success': False, 'message': f'A marca "{nome}" já existe.'}), 400
                    flash(f'Alerta de Integridade: A marca "{nome}" já existe.', 'warning')
                else:
                    marca = Marca()

            if marca:
                marca.nome = nome
                marca.pais_origem = request.form.get('pais_origem')
                marca.website = request.form.get('website')
                marca.origem_comercial = request.form.get('origem_comercial')
                marca.status = request.form.get('status_marca', 'ATIVO')

                # Upload do logo
                logo_file = request.files.get('logo_marca')
                if logo_file and logo_file.filename:
                    import os
                    from werkzeug.utils import secure_filename
                    upload_dir = os.path.join('static', 'uploads', 'marcas')
                    os.makedirs(upload_dir, exist_ok=True)
                    filename = secure_filename(f"marca_{marca.id or 'new'}_{logo_file.filename}")
                    logo_path = os.path.join(upload_dir, filename)
                    logo_file.save(logo_path)
                    marca.logo = f'uploads/marcas/{filename}'

                db.session.add(marca)
                db.session.commit()

                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({'success': True, 'message': 'Marca salva com sucesso!'})
                flash('Integridade: Marca salva com sucesso!', 'success')

        # AJAX-friendly: Retorna o fragmento do formulário
        return render_template('cadastros/cards/catalogos/form_marcas.html',
                             marcas=Marca.query.order_by(Marca.nome).all(),
                             marca=marca)

    marcas = Marca.query.order_by(Marca.nome).all()
    return render_template('cadastros/cards/catalogos/form_marcas.html', marcas=marcas, marca=marca)

@cadastros_bp.route('/cards/marcas/excluir/<int:id>', methods=['POST'])
def excluir_marca(id):
    marca = Marca.query.get_or_404(id)
    try:
        db.session.delete(marca)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Marca excluída com sucesso!'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 400

@cadastros_bp.route('/cards/marcas/dados-json', methods=['GET'])
def exportar_marcas_json():
    """Retorna todas as marcas como JSON para exportação via frontend."""
    marcas = Marca.query.all()
    return jsonify([{'id': m.id, 'nome': m.nome, 'pais': m.pais_origem} for m in marcas])

# ── Central de Grades de Variação ───────────────────────────────────────────

@cadastros_bp.route('/catalogos/grades', methods=['GET', 'POST'])
@cadastros_bp.route('/catalogos/grades/<int:id>', methods=['GET', 'POST'])
@login_required
def card_grades(id=None):
    """Gestão da Central de Grades de Variação"""
    grade = GradeModelo.query.get(id) if id else None
    
    if request.method == 'POST':
        nome = request.form.get('nome')
        categoria = request.form.get('categoria')
        # Recebe os itens como string separada por vírgula e converte para lista
        itens_raw = request.form.get('itens', '')
        itens = [i.strip() for i in itens_raw.split(',') if i.strip()]
        
        if nome and itens:
            # 🛡️ Blindagem Anti-Duplicidade (Nome Único)
            existente = GradeModelo.query.filter_by(nome=nome).first()
            if existente and (not grade or existente.id != grade.id):
                flash(f'Alerta de Integridade: A grade "{nome}" já existe.', 'warning')
                return render_template('cadastros/cards/catalogos/form_grades.html', 
                                     grades=GradeModelo.query.order_by(GradeModelo.nome).all(),
                                     grade=grade)

            if not grade:
                grade = GradeModelo()
                db.session.add(grade)
            
            grade.nome = nome
            grade.categoria = categoria
            grade.itens = itens
            
            try:
                db.session.commit()
                flash(f'Grade "{nome}" salva com sucesso!', 'success')
            except Exception as e:
                db.session.rollback()
                flash(f'Erro ao salvar grade: {str(e)}', 'danger')
        else:
            flash('Nome e Itens são obrigatórios para a grade.', 'warning')
            
        return render_template('cadastros/cards/catalogos/form_grades.html', 
                             grades=GradeModelo.query.order_by(GradeModelo.nome).all(),
                             grade=grade)

    grades = GradeModelo.query.order_by(GradeModelo.nome).all()
    return render_template('cadastros/cards/catalogos/form_grades.html', grades=grades, grade=grade)

@cadastros_bp.route('/catalogos/grades/excluir/<int:id>', methods=['POST'])
@login_required
def excluir_grade(id):
    grade = GradeModelo.query.get_or_404(id)
    
    # 🛡️ TRAVA DE INTEGRIDADE ARIONE
    if grade.em_uso:
        msg = f'Não é possível excluir a grade "{grade.nome}" pois ela possui movimentações ou está vinculada a produtos.'
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'message': msg}), 400
        flash(msg, 'danger')
        return redirect(url_for('cadastros.card_grades'))

    nome = grade.nome
    try:
        db.session.delete(grade)
        db.session.commit()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': True, 'message': f'Grade "{nome}" excluída.'})
        flash(f'Grade "{nome}" excluída.', 'success')
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 400
    return redirect(url_for('cadastros.card_grades'))

@cadastros_bp.route('/catalogos/grades/<int:id>/json', methods=['GET'])
@login_required
def grade_json(id):
    grade = GradeModelo.query.get_or_404(id)
    return jsonify({
        "id": grade.id,
        "nome": grade.nome,
        "itens": grade.itens
    })

@cadastros_bp.route('/produtos/checar-uso-variacao/<int:produto_id>/<string:tipo>/<string:valor>', methods=['GET'])
@login_required
def checar_uso_variacao(produto_id, tipo, valor):
    from app.models.catalogos import MovimentoEstoque
    filtros = { 'produto_id': produto_id }
    if tipo == 'cor': filtros['cor'] = valor
    elif tipo == 'tamanho': filtros['tamanho'] = valor
    elif tipo == 'atributo': filtros['atributo'] = valor
    existe_movimento = MovimentoEstoque.query.filter_by(**filtros).first() is not None
    return jsonify({
        "bloqueado": existe_movimento,
        "mensagem": "Esta variação possui movimentações e não pode ser removida." if existe_movimento else "Livre para remoção."
    })

# ── Atributos de Produto (Variações Adicionais) ──────────────────────────────

@cadastros_bp.route('/cards/tamanhos', methods=['GET', 'POST'])
@login_required
def card_tamanhos():
    """Gestão de Tamanhos Individuais (P, M, G, 40...) — Suporte a AJAX"""
    if request.method == 'POST':
        tam_id = request.form.get('id')
        nome   = request.form.get('nome_tamanho', '').strip().upper()
        ordem  = request.form.get('ordem', 0)
        status = request.form.get('status_tamanho', 'ATIVO')

        if nome:
            if tam_id:
                tamanho = TamanhoCatalogo.query.get(tam_id)
                if tamanho:
                    tamanho.nome = nome
                    tamanho.ordem = int(ordem)
                    tamanho.ativa = (status == 'ATIVO')
                    flash(f'Tamanho "{nome}" atualizado!', 'success')
            else:
                existente = TamanhoCatalogo.query.filter_by(nome=nome).first()
                if not existente:
                    tamanho = TamanhoCatalogo(nome=nome, ordem=int(ordem), ativa=(status == 'ATIVO'))
                    db.session.add(tamanho)
                    flash(f'Tamanho "{nome}" cadastrado!', 'success')
                else:
                    flash(f'Tamanho "{nome}" já existe.', 'warning')
            
            db.session.commit()
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                tamanhos = TamanhoCatalogo.query.order_by(TamanhoCatalogo.ordem, TamanhoCatalogo.nome).all()
                return render_template('cadastros/cards/catalogos/form_tamanhos.html', tamanhos=tamanhos)
        
        return redirect(url_for('cadastros.card_tamanhos'))

    tamanhos = TamanhoCatalogo.query.order_by(TamanhoCatalogo.ordem, TamanhoCatalogo.nome).all()
    return render_template('cadastros/cards/catalogos/form_tamanhos.html', tamanhos=tamanhos)

@cadastros_bp.route('/cards/tamanhos/excluir/<int:id>', methods=['POST'])
@login_required
def excluir_tamanho(id):
    """Exclusão de tamanho com trava de integridade"""
    tamanho = TamanhoCatalogo.query.get_or_404(id)
    nome = tamanho.nome
    try:
        db.session.delete(tamanho)
        db.session.commit()
        return jsonify({'success': True, 'message': f'Tamanho "{nome}" removido.'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 400

@cadastros_bp.route('/cards/atributos', methods=['GET', 'POST'])
@login_required
def card_atributos():
    """Gestão de Atributos de Catálogo — Suporte a Edição e AJAX"""
    if request.method == 'POST':
        atrib_id  = request.form.get('id')
        nome      = request.form.get('nome_atributo', '').strip()
        descricao = request.form.get('descricao', '').strip()
        status    = request.form.get('status_atributo', 'ATIVO')

        if nome:
            if atrib_id:
                atributo = AtributoCatalogo.query.get(atrib_id)
                if atributo:
                    atributo.nome = nome
                    atributo.descricao = descricao
                    atributo.ativa = (status == 'ATIVO')
                    flash(f'Atributo "{nome}" atualizado!', 'success')
            else:
                # Verifica se já existe com o mesmo nome
                existente = AtributoCatalogo.query.filter_by(nome=nome).first()
                if not existente:
                    atributo = AtributoCatalogo(nome=nome, descricao=descricao, ativa=(status == 'ATIVO'))
                    db.session.add(atributo)
                    flash(f'Atributo "{nome}" cadastrado!', 'success')
                else:
                    flash(f'Atributo "{nome}" já existe.', 'warning')
            
            db.session.commit()
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                atributos = AtributoCatalogo.query.order_by(AtributoCatalogo.nome).all()
                return render_template('cadastros/cards/catalogos/form_atributos.html', atributos=atributos)
        
        return redirect(url_for('cadastros.card_atributos'))

    atributos = AtributoCatalogo.query.order_by(AtributoCatalogo.nome).all()
    return render_template('cadastros/cards/catalogos/form_atributos.html', atributos=atributos)

@cadastros_bp.route('/cards/atributos/excluir/<int:id>', methods=['POST'])
@login_required
def excluir_atributo(id):
    atributo = AtributoCatalogo.query.get_or_404(id)
    if atributo.em_uso:
        return jsonify({'success': False, 'message': 'Atributo em uso em produtos.'}), 400
    db.session.delete(atributo)
    db.session.commit()
    return jsonify({'success': True})




@cadastros_bp.route('/cards/categorias', methods=['GET', 'POST'])
@cadastros_bp.route('/cards/categorias/<int:id>', methods=['GET', 'POST'])
def card_categorias(id=None):
    from sqlalchemy import text
    try:
        db.session.execute(text("ALTER TABLE cat_categorias ADD COLUMN descricao TEXT"))
        db.session.execute(text("ALTER TABLE cat_categorias ADD COLUMN cor VARCHAR(20) DEFAULT '#27AE60'"))
        db.session.execute(text("ALTER TABLE cat_categorias ADD COLUMN icone VARCHAR(50) DEFAULT 'fa-layer-group'"))
        db.session.commit()
    except Exception:
        db.session.rollback()

    if request.method == 'POST':
        cat_id = request.form.get('id')
        categoria = Categoria.query.get(cat_id) if cat_id else None
        
        nome = request.form.get('nome_categoria')
        if nome:
            if not categoria: categoria = Categoria()
            categoria.nome = nome
            categoria.departamento = request.form.get('departamento')
            categoria.descricao = request.form.get('descricao')
            categoria.cor = request.form.get('cor', '#27AE60')
            categoria.icone = request.form.get('icone', 'fa-layer-group')
            
            db.session.add(categoria)
            db.session.flush() # get id for subcategorias
            
            # ── Subcategorias em Nível 2 ──
            sub_ids = request.form.getlist('sub_id[]')
            sub_nomes = request.form.getlist('sub_nome[]')
            sub_margens = request.form.getlist('sub_margem[]')
            sub_status = request.form.getlist('sub_status[]')
            
            for i, s_nome in enumerate(sub_nomes):
                s_nome = s_nome.strip()
                if not s_nome: continue
                s_id = sub_ids[i] if i < len(sub_ids) and sub_ids[i] else None
                s_margem = sub_margens[i] if i < len(sub_margens) and sub_margens[i] else 0.0
                s_stat = sub_status[i] if i < len(sub_status) else 'ATIVO'
                
                if s_id:
                    sub = Subcategoria.query.get(s_id)
                    if sub:
                        sub.nome = s_nome
                        sub.margem_sugerida = float(s_margem)
                        sub.ativa = (s_stat == 'ATIVO')
                else:
                    sub = Subcategoria(nome=s_nome, categoria_id=categoria.id, margem_sugerida=float(s_margem), ativa=(s_stat == 'ATIVO'))
                    db.session.add(sub)
                    
            db.session.commit()
            flash('Integridade: Categoria e Subcategorias salvas!', 'success')
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': True})
            return redirect(url_for('cadastros.card_categorias'))
            
    categorias = Categoria.query.order_by(Categoria.nome).all()
    return render_template('cadastros/cards/catalogos/form_categorias.html', categorias=categorias)

@cadastros_bp.route('/cards/categorias/<int:id>/json', methods=['GET'])
def categoria_json(id):
    cat = Categoria.query.get_or_404(id)
    return jsonify({
        'id': cat.id,
        'nome': cat.nome,
        'departamento': cat.departamento,
        'descricao': getattr(cat, 'descricao', ''),
        'cor': getattr(cat, 'cor', '#27AE60'),
        'icone': getattr(cat, 'icone', 'fa-layer-group'),
        'subcategorias': [{
            'id': s.id,
            'nome': s.nome,
            'margem': s.margem_sugerida,
            'status': 'ATIVO' if s.ativa else 'INATIVO'
        } for s in cat.subcategorias]
    })

@cadastros_bp.route('/cards/categorias/excluir/<int:id>', methods=['POST'])
def excluir_categoria(id):
    cat = Categoria.query.get_or_404(id)
    try:
        db.session.delete(cat)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

@cadastros_bp.route('/cards/categorias/lista-json', methods=['GET'])
def lista_categorias_json():
    """Retorna todas as categorias como JSON para o seletor de categoria pai."""
    categorias = Categoria.query.order_by(Categoria.nome).all()
    return jsonify([{'id': c.id, 'nome': c.nome, 'departamento': c.departamento or '',
                     'total_subs': len(c.subcategorias)} for c in categorias])

@cadastros_bp.route('/cards/categorias/dados-json', methods=['GET'])
def exportar_categorias_json():
    """Retorna todas as categorias + subcategorias como JSON para exportação via frontend."""
    categorias = Categoria.query.order_by(Categoria.nome).all()
    resultado = []
    for c in categorias:
        resultado.append({'ID': c.id, 'Categoria': c.nome, 'Departamento': c.departamento or '',
                          'Total_Subcategorias': len(c.subcategorias), 'Tipo': 'CATEGORIA'})
        for s in c.subcategorias:
            resultado.append({'ID': s.id, 'Categoria': c.nome, 'Departamento': c.departamento or '',
                              'Subcategoria': s.nome, 'Margem_%': s.margem_sugerida or 0,
                              'Status': 'ATIVO' if s.ativa else 'INATIVO', 'Tipo': 'SUBCATEGORIA'})
    return jsonify(resultado)

@cadastros_bp.route('/cards/subcategorias', methods=['GET', 'POST'])
@cadastros_bp.route('/cards/subcategorias/nova', methods=['POST'])
@cadastros_bp.route('/cards/subcategorias/<int:id>', methods=['GET', 'POST'])
def card_subcategorias(id=None):
    """Formulário ou Edição de subcategoria."""
    from app.models.catalogos import Subcategoria
    
    if request.method == 'POST':
        # Se for edição inline
        if id:
            sub = Subcategoria.query.get_or_404(id)
            sub.nome = request.form.get('nome', '').strip()
            sub.margem_sugerida = float(request.form.get('margem', 0) or 0)
            sub.ativa = (request.form.get('status', 'ATIVO') == 'ATIVO')
            db.session.commit()
            return jsonify({'success': True})
            
        # Se for criação nova
        nome   = request.form.get('nome', '').strip() or request.form.get('nome_sub', '').strip()
        cat_id = request.form.get('categoria_id')
        if nome and cat_id:
            sub = Subcategoria(
                nome=nome,
                categoria_id=int(cat_id),
                margem_sugerida=float(request.form.get('margem', 0) or 0),
                ativa=(request.form.get('status', 'ATIVO') == 'ATIVO')
            )
            db.session.add(sub)
            db.session.commit()
            flash(f'Integridade: Subcategoria "{nome}" salva com sucesso!', 'success')
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': True, 'nome': nome, 'id': sub.id, 'categoria_nome': sub.categoria.nome})
            return redirect(url_for('cadastros.card_subcategorias'))
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'message': 'Nome e Categoria são obrigatórios.'}), 400
        flash('Nome e Categoria são obrigatórios.', 'danger')
    
    sub_obj = Subcategoria.query.get(id) if id else None
    categorias = Categoria.query.order_by(Categoria.nome).all()
    recentes = Subcategoria.query.order_by(Subcategoria.id.desc()).limit(5).all()
    return render_template('cadastros/cards/catalogos/form_subcategorias.html', 
                           categorias=categorias, recentes=recentes, sub_id=id, sub=sub_obj)

@cadastros_bp.route('/cards/subcategorias/excluir/<int:id>', methods=['POST'])
def excluir_subcategoria(id):
    from app.models.catalogos import Subcategoria
    sub = Subcategoria.query.get_or_404(id)
    try:
        db.session.delete(sub)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

@cadastros_bp.route('/cards/unidades', methods=['GET', 'POST'])
@cadastros_bp.route('/cards/unidades/<int:id>', methods=['GET', 'POST'])
def card_unidades(id=None):
    unidade = UnidadeMedida.query.get(id) if id else None
    if request.method == 'POST':
        sigla = request.form.get('sigla')
        if sigla:
            if not unidade: unidade = UnidadeMedida()
            unidade.sigla = sigla.upper()
            unidade.nome_extenso = request.form.get('nome_extenso')
            unidade.decimais = int(request.form.get('decimais', 0))
            unidade.permite_fracionamento = request.form.get('fracionamento') == 'SIM'
            db.session.add(unidade)
            db.session.commit()
            flash('Integridade: Unidade de Medida salva!', 'success')
        return render_template('cadastros/cards/catalogos/form_unidades.html', 
                             unidades=UnidadeMedida.query.order_by(UnidadeMedida.sigla).all(),
                             unidade=unidade)
    unidades = UnidadeMedida.query.order_by(UnidadeMedida.sigla).all()
    return render_template('cadastros/cards/catalogos/form_unidades.html', unidades=unidades, unidade=unidade)

@cadastros_bp.route('/cards/unidades/excluir/<int:id>', methods=['POST'])
def excluir_unidade(id):
    un = UnidadeMedida.query.get_or_404(id)
    try:
        db.session.delete(un)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

@cadastros_bp.route('/cards/unidades/dados-json', methods=['GET'])
def exportar_unidades_json():
    uns = UnidadeMedida.query.order_by(UnidadeMedida.sigla).all()
    return jsonify([{'ID': u.id, 'Sigla': u.sigla, 'Nome': u.nome_extenso,
                     'Decimais': u.decimais, 'Fracionamento': 'SIM' if u.permite_fracionamento else 'NAO'} for u in uns])

@cadastros_bp.route('/cards/etiquetas', methods=['GET', 'POST'])
@cadastros_bp.route('/cards/etiquetas/<int:id>', methods=['GET', 'POST'])
def card_etiquetas(id=None):
    etiqueta = Etiqueta.query.get(id) if id else None
    if request.method == 'POST':
        label = request.form.get('label')
        if label:
            if not etiqueta: etiqueta = Etiqueta()
            etiqueta.label = label
            etiqueta.cor_hex = request.form.get('cor_hex')
            etiqueta.prioridade = int(request.form.get('prioridade', 1))
            
            # Lógica de Foto/Ícone Etiqueta
            if 'foto_etiqueta' in request.files:
                file = request.files['foto_etiqueta']
                if file and file.filename:
                    import os
                    from werkzeug.utils import secure_filename
                    filename = secure_filename(f"tag_{etiqueta.id or 'new'}_{file.filename}")
                    upload_path = os.path.join('app', 'static', 'uploads', 'etiquetas')
                    os.makedirs(upload_path, exist_ok=True)
                    file.save(os.path.join(upload_path, filename))
                    etiqueta.foto = filename

            db.session.add(etiqueta)
            db.session.commit()
            flash('Integridade: Etiqueta/Tag salva!', 'success')
        return render_template('cadastros/cards/catalogos/form_etiquetas.html', 
                             etiquetas=Etiqueta.query.order_by(Etiqueta.label).all(),
                             etiqueta=etiqueta)
    etiquetas = Etiqueta.query.order_by(Etiqueta.label).all()
    return render_template('cadastros/cards/catalogos/form_etiquetas.html', etiquetas=etiquetas, etiqueta=etiqueta)

@cadastros_bp.route('/cards/etiquetas/excluir/<int:id>', methods=['POST'])
def excluir_etiqueta(id):
    et = Etiqueta.query.get_or_404(id)
    try:
        db.session.delete(et)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

@cadastros_bp.route('/cards/etiquetas/dados-json', methods=['GET'])
def exportar_etiquetas_json():
    ets = Etiqueta.query.order_by(Etiqueta.label).all()
    return jsonify([{'ID': e.id, 'Label': e.label, 'Cor': e.cor_hex} for e in ets])

@cadastros_bp.route('/cards/depositos', methods=['GET', 'POST'])
@cadastros_bp.route('/cards/depositos/<int:id>', methods=['GET', 'POST'])
def card_depositos(id=None):
    deposito = Deposito.query.get(id) if id else None
    if request.method == 'POST':
        nome = request.form.get('nome')
        if nome:
            try:
                if not deposito: 
                    deposito = Deposito()
                    db.session.add(deposito)
                
                deposito.nome = nome
                # Gera um código único interno para evitar conflito com a restrição UNIQUE do banco antigo
                if not deposito.sigla:
                    deposito.sigla = f"DEP_{datetime.now().strftime('%H%M%S%f')}"
                deposito.endereco = request.form.get('endereco')
                deposito.tipo = request.form.get('tipo', 'proprio')
                
                db.session.flush() # Garante que o ID exista para depósitos novos

                # Gerenciamento de Prateleiras
                prateleiras_raw = request.form.getlist('prateleiras[]')
                # Sempre limpa as atuais para este depósito e reinsere (sincronismo simples)
                DepositoPrateleira.query.filter_by(deposito_id=deposito.id).delete()
                
                if prateleiras_raw:
                    for p_nome in prateleiras_raw:
                        if p_nome.strip():
                            nova_p = DepositoPrateleira(deposito_id=deposito.id, nome=p_nome.strip())
                            db.session.add(nova_p)
                
                db.session.commit()
                flash('Integridade: Depósito e Localizações salvos!', 'success')
            except Exception as e:
                db.session.rollback()
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({'success': False, 'message': str(e)}), 500
                flash(f'Erro ao salvar: {str(e)}', 'danger')
        
        return render_template('cadastros/cards/catalogos/form_depositos.html', 
                             depositos=Deposito.query.order_by(Deposito.nome).all(),
                             deposito=deposito)
    
    depositos = Deposito.query.order_by(Deposito.nome).all()
    return render_template('cadastros/cards/catalogos/form_depositos.html', depositos=depositos, deposito=deposito)

@cadastros_bp.route('/cards/depositos/excluir/<int:id>', methods=['POST'])
def excluir_deposito(id):
    dep = Deposito.query.get_or_404(id)
    try:
        db.session.delete(dep)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Depósito excluído com sucesso!'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400
    return jsonify([{'ID': e.id, 'Label': e.label, 'Cor': e.cor_hex,
                     'Prioridade': e.prioridade, 'Ativa': 'SIM' if e.ativa else 'NAO'} for e in ets])
@cadastros_bp.route('/cards/materiaprima/tipos/add', methods=['POST'])
@login_required
def add_tipo_materiaprima():
    nome = request.form.get('nome', '').strip().upper()
    if not nome:
        return jsonify({'success': False, 'message': 'Nome é obrigatório'}), 400
    
    tipo = TipoMateriaPrima.query.filter_by(nome=nome).first()
    if tipo:
        return jsonify({'success': False, 'message': f'Alerta de Integridade: O tipo de material "{nome}" já está cadastrado.'}), 400
    
    tipo = TipoMateriaPrima(nome=nome)
    db.session.add(tipo)
    db.session.commit()
    
    return jsonify({'success': True, 'id': tipo.id, 'nome': tipo.nome})

@cadastros_bp.route('/cards/materiaprima/tipos/excluir/<int:id>', methods=['POST'])
@login_required
def excluir_tipo_materiaprima(id):
    tipo = TipoMateriaPrima.query.get_or_404(id)
    if tipo.em_uso:
        return jsonify({'success': False, 'message': 'Este tipo está vinculado a matérias-primas ou produtos e não pode ser excluído.'}), 400
    
    try:
        db.session.delete(tipo)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@cadastros_bp.route('/cards/materiaprima', methods=['GET', 'POST'])
@cadastros_bp.route('/cards/materiaprima/<int:id>', methods=['GET', 'POST'])
def card_materiaprima(id=None):
    from app.models.catalogos import MateriaPrima, UnidadeMedida
    mp = MateriaPrima.query.get(id) if id else None
    unidades_list = UnidadeMedida.query.order_by(UnidadeMedida.sigla).all()

    if request.method == 'POST':
        descricao = request.form.get('descricao', '').strip()
        sku = request.form.get('sku', '').strip()

        if descricao:
            # 🛡️ Validação de Integridade AriOne: Evitar Duplicidade
            existente_desc = MateriaPrima.query.filter(MateriaPrima.descricao == descricao, MateriaPrima.id != id).first()
            if existente_desc:
                return jsonify({'success': False, 'message': f'Já existe uma matéria-prima cadastrada com a descrição "{descricao}".'}), 400
            
            if sku:
                existente_sku = MateriaPrima.query.filter(MateriaPrima.sku == sku, MateriaPrima.id != id).first()
                if existente_sku:
                    return jsonify({'success': False, 'message': f'O SKU "{sku}" já está sendo utilizado por outro material.'}), 400

            if not mp: mp = MateriaPrima()
            mp.descricao = descricao
            mp.sku = sku
            mp.unidade_id = request.form.get('unidade_id')
            mp.tipo_id = request.form.get('tipo_id')
            
            def clean_money(val):
                if not val: return 0.0
                return float(str(val).replace('R$', '').replace('.', '').replace(',', '.').strip() or 0)
            
            mp.preco_custo = clean_money(request.form.get('preco_custo'))
            mp.estoque_minimo = float(request.form.get('estoque_minimo', 0) or 0)

            db.session.add(mp)
            try:
                db.session.commit() # Gera o ID primeiro
            except Exception as e:
                db.session.rollback()
                if 'UNIQUE' in str(e).upper():
                    return jsonify({'success': False, 'message': 'O SKU informado já está em uso por outra matéria-prima.'}), 400
                return jsonify({'success': False, 'message': str(e)}), 400

            # Lógica de Foto Matéria-Prima
            if 'foto_materiaprima' in request.files:
                file = request.files['foto_materiaprima']
                if file and file.filename:
                    import os
                    from werkzeug.utils import secure_filename
                    filename = secure_filename(f"mp_{mp.id}_{file.filename}")
                    upload_path = os.path.join('app', 'static', 'uploads', 'materiaprima')
                    os.makedirs(upload_path, exist_ok=True)
                    file.save(os.path.join(upload_path, filename))
                    mp.foto = filename
                    db.session.commit() # Salva o nome da foto no registro

            flash('Integridade: Matéria-Prima salva!', 'success')
        return render_template('cadastros/cards/catalogos/form_materiaprima.html', 
                             materias=MateriaPrima.query.order_by(MateriaPrima.descricao).all(),
                             unidades_list=unidades_list,
                             tipos_list=TipoMateriaPrima.query.order_by(TipoMateriaPrima.nome).all(),
                             materia=mp)
    
    materias = MateriaPrima.query.order_by(MateriaPrima.descricao).all()
    return render_template('cadastros/cards/catalogos/form_materiaprima.html', 
                         materias=materias, 
                         unidades_list=unidades_list, 
                         tipos_list=TipoMateriaPrima.query.order_by(TipoMateriaPrima.nome).all(),
                         materia=mp)

@cadastros_bp.route('/cards/materiaprima/excluir/<int:id>', methods=['POST'])
def excluir_materiaprima(id):
    mp = MateriaPrima.query.get_or_404(id)
    try:
        db.session.delete(mp)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

@cadastros_bp.route('/cards/materiaprima/dados-json', methods=['GET'])
def exportar_materiaprima_json():
    mps = MateriaPrima.query.order_by(MateriaPrima.descricao).all()
    return jsonify([{'ID': m.id, 'Descricao': m.descricao, 'SKU': m.sku or '',
                     'NCM': m.ncm or '', 'CST': m.cst or '',
                     'Estoque_Min': m.estoque_minimo, 'Ativa': 'SIM' if m.ativa else 'NAO'} for m in mps])

@cadastros_bp.route('/cards/materiaprima/pesquisa')
@login_required
def pesquisa_materiaprima():
    q = request.args.get('q', '').strip()
    if len(q) < 2: return jsonify([])
    from app.models.catalogos import MateriaPrima
    mps = MateriaPrima.query.filter(
        (MateriaPrima.descricao.ilike(f'%{q}%')) | 
        (MateriaPrima.sku.ilike(f'%{q}%'))
    ).limit(20).all()
    return jsonify([{
        'id': m.id,
        'sku': m.sku or '',
        'descricao': m.descricao,
        'unidade': m.unidade.sigla if m.unidade else 'UN',
        'preco_custo': m.preco_custo or 0.0
    } for m in mps])
@cadastros_bp.route('/cards/materiaprima/proximo-sku')
@login_required
def proximo_sku_materiaprima():
    from app.models.catalogos import MateriaPrima
    last = MateriaPrima.query.order_by(MateriaPrima.id.desc()).first()
    next_id = (last.id + 1) if last else 1
    sku = f"MP-{next_id:04d}"
    
    # Proteção contra duplicidade: enquanto existir, incrementa
    while MateriaPrima.query.filter_by(sku=sku).first():
        next_id += 1
        sku = f"MP-{next_id:04d}"
        
    return jsonify({'sku': sku})

@cadastros_bp.route('/cards/insumos/proximo-sku')
@login_required
def proximo_sku_insumo():
    from app.models.catalogos import Insumo
    last = Insumo.query.order_by(Insumo.id.desc()).first()
    next_id = (last.id + 1) if last else 1
    sku = f"IN-{next_id:04d}"
    
    while Insumo.query.filter_by(sku=sku).first():
        next_id += 1
        sku = f"IN-{next_id:04d}"
        
    return jsonify({'sku': sku})

@cadastros_bp.route('/cards/acessorios/proximo-sku')
@login_required
def proximo_sku_acessorio():
    from app.models.catalogos import Acessorio
    last = Acessorio.query.order_by(Acessorio.id.desc()).first()
    next_id = (last.id + 1) if last else 1
    sku = f"AC-{next_id:04d}"
    
    while Acessorio.query.filter_by(referencia=sku).first():
        next_id += 1
        sku = f"AC-{next_id:04d}"
        
    return jsonify({'sku': sku})

@cadastros_bp.route('/cards/embalagens/proximo-sku')
@login_required
def proximo_sku_embalagem():
    from app.models.catalogos import Embalagem
    last = Embalagem.query.order_by(Embalagem.id.desc()).first()
    next_id = (last.id + 1) if last else 1
    sku = f"EMB-{next_id:04d}"
    
    while Embalagem.query.filter_by(sku=sku).first():
        next_id += 1
        sku = f"EMB-{next_id:04d}"
        
    return jsonify({'sku': sku})

@cadastros_bp.route('/cards/servicos/proximo-sku')
@login_required
def proximo_sku_servico():
    from app.models.catalogos import Servico
    last = Servico.query.order_by(Servico.id.desc()).first()
    next_id = (last.id + 1) if last else 1
    sku = f"SRV-{next_id:03d}"
    
    while Servico.query.filter_by(codigo=sku).first():
        next_id += 1
        sku = f"SRV-{next_id:03d}"
        
    return jsonify({'sku': sku})


@cadastros_bp.route('/cards/insumos', methods=['GET', 'POST'])
@cadastros_bp.route('/cards/insumos/<int:id>', methods=['GET', 'POST'])
def card_insumos(id=None):
    from app.models.catalogos import Insumo, UnidadeMedida
    insumo = Insumo.query.get(id) if id else None
    unidades_list = UnidadeMedida.query.order_by(UnidadeMedida.sigla).all()
    
    if request.method == 'POST':
        nome = request.form.get('nome')
        if nome:
            if not insumo: insumo = Insumo()
            insumo.nome = nome
            insumo.sku = request.form.get('sku')
            insumo.unidade_id = request.form.get('unidade_id')
            
            def clean_money(val):
                if not val: return 0.0
                return float(str(val).replace('R$', '').replace('.', '').replace(',', '.').strip() or 0)
                
            insumo.preco_custo = clean_money(request.form.get('preco_custo'))
            insumo.estoque_minimo = float(request.form.get('estoque_minimo', 0) or 0)

            
            db.session.add(insumo)
            try:
                db.session.commit() # Gera o ID primeiro
            except Exception as e:
                db.session.rollback()
                return jsonify({'success': False, 'message': str(e)}), 400

            # Lógica de Foto Insumo
            if 'foto_insumo' in request.files:
                file = request.files['foto_insumo']
                if file and file.filename:
                    import os
                    from werkzeug.utils import secure_filename
                    filename = secure_filename(f"insumo_{insumo.id}_{file.filename}")
                    upload_path = os.path.join('app', 'static', 'uploads', 'insumos')
                    os.makedirs(upload_path, exist_ok=True)
                    file.save(os.path.join(upload_path, filename))
                    insumo.foto = filename
                    db.session.commit() # Atualiza o registro com o nome da foto

            flash('Integridade: Insumo salvo!', 'success')
        return render_template('cadastros/cards/catalogos/form_insumos.html', 
                             insumos=Insumo.query.order_by(Insumo.nome).all(),
                             unidades_list=unidades_list,
                             insumo=insumo)
    
    insumos = Insumo.query.order_by(Insumo.nome).all()
    return render_template('cadastros/cards/catalogos/form_insumos.html', 
                         insumos=insumos, 
                         unidades_list=unidades_list, 
                         insumo=insumo)

@cadastros_bp.route('/cards/insumos/excluir/<int:id>', methods=['POST'])
def excluir_insumo(id):
    ins = Insumo.query.get_or_404(id)
    try:
        db.session.delete(ins)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

@cadastros_bp.route('/cards/insumos/dados-json', methods=['GET'])
def exportar_insumos_json():
    ins_list = Insumo.query.order_by(Insumo.nome).all()
    return jsonify([{'ID': i.id, 'Nome': i.nome, 'Estoque_Min': i.estoque_minimo,
                     'Conta_Contabil': i.conta_contabil or '', 'Centro_Custo': i.centro_custo or '',
                     'Ativa': 'SIM' if i.ativa else 'NAO'} for i in ins_list])

@cadastros_bp.route('/cards/acessorios/classificacoes/add', methods=['POST'])
@login_required
def add_classificacao_acessorio():
    from app.models.catalogos import ClassificacaoAcessorio
    nome = request.form.get('nome')
    if not nome: return jsonify({'success': False, 'message': 'Nome obrigatório'}), 400
    try:
        nova = ClassificacaoAcessorio(nome=nome.upper())
        db.session.add(nova)
        db.session.commit()
        return jsonify({'success': True, 'id': nova.id, 'nome': nova.nome})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 400

@cadastros_bp.route('/cards/embalagens/classificacoes/add', methods=['POST'])
@login_required
def add_classificacao_embalagem():
    from app.models.catalogos import ClassificacaoEmbalagem
    nome = request.form.get('nome')
    if not nome: return jsonify({'success': False, 'message': 'Nome obrigatório'}), 400
    try:
        nova = ClassificacaoEmbalagem(nome=nome.upper())
        db.session.add(nova)
        db.session.commit()
        return jsonify({'success': True, 'id': nova.id, 'nome': nova.nome})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 400

@cadastros_bp.route('/cards/acessorios/classificacoes/excluir/<int:id>', methods=['POST'])
@login_required
def excluir_classificacao_acessorio(id):
    from app.models.catalogos import ClassificacaoAcessorio
    tipo = ClassificacaoAcessorio.query.get_or_404(id)
    if tipo.em_uso:
        return jsonify({'success': False, 'message': 'Este tipo está vinculado a acessórios e não pode ser excluído.'}), 400
    try:
        db.session.delete(tipo)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 400

@cadastros_bp.route('/cards/acessorios', methods=['GET', 'POST'])
@cadastros_bp.route('/cards/acessorios/<int:id>', methods=['GET', 'POST'])
@login_required
def card_acessorios(id=None):
    from app.models.catalogos import Acessorio, UnidadeMedida, ClassificacaoAcessorio, FornecedorAcessorio
    from app.models.cadastros.fornecedor import Fornecedor
    from app.models.cadastros.empresa import Empresa
    
    ace = Acessorio.query.get(id) if id else None
    
    # Listas para o form
    unidades_list = UnidadeMedida.query.order_by(UnidadeMedida.sigla).all()
    classificacoes_list = ClassificacaoAcessorio.query.order_by(ClassificacaoAcessorio.nome).all()
    fornecedores_lista = Fornecedor.query.order_by(Fornecedor.razao_social).all()
    empresas_lista = Empresa.query.all()
    
    if request.method == 'POST':
        nome = request.form.get('nome')
        if nome:
            if not ace: ace = Acessorio()
            ace.nome = nome
            ace.referencia = request.form.get('sku')
            ace.classificacao_id = request.form.get('classificacao_id')
            ace.unidade_id = request.form.get('unidade_id')
            
            def clean_money(val):
                if not val: return 0.0
                return float(str(val).replace('R$', '').replace('.', '').replace(',', '.').strip() or 0)
                
            ace.custo_unitario = clean_money(request.form.get('preco_custo'))
            ace.peso_g = float(request.form.get('peso_g', 0) or 0)
            
            db.session.add(ace)
            try:
                db.session.commit()
                
                # Matriz de Fornecedores
                FornecedorAcessorio.query.filter_by(acessorio_id=ace.id).delete()
                forn_ids = request.form.getlist('forn_id[]')
                forn_precos = request.form.getlist('forn_preco[]')
                forn_prazos = request.form.getlist('forn_prazo[]')
                forn_mods = request.form.getlist('forn_modalidade[]')
                
                for i in range(len(forn_ids)):
                    if i < len(forn_ids) and forn_ids[i]:
                        fa = FornecedorAcessorio(
                            acessorio_id=ace.id,
                            fornecedor_id=int(forn_ids[i]),
                            preco_compra=float(forn_precos[i] or 0),
                            prazo_entrega=int(forn_prazos[i] or 1),
                            modalidade=forn_mods[i]
                        )
                        db.session.add(fa)
                db.session.commit()
                
            except Exception as e:
                db.session.rollback()
                return jsonify({'success': False, 'message': str(e)}), 400

            # Lógica de Foto Acessório
            if 'foto_acessorio' in request.files:
                file = request.files['foto_acessorio']
                if file and file.filename:
                    import os
                    from werkzeug.utils import secure_filename
                    filename = secure_filename(f"ace_{ace.id}_{file.filename}")
                    upload_path = os.path.join('app', 'static', 'uploads', 'acessorios')
                    os.makedirs(upload_path, exist_ok=True)
                    file.save(os.path.join(upload_path, filename))
                    ace.foto = filename
                    db.session.commit()

            flash('Integridade: Acessório salvo!', 'success')
        return render_template('cadastros/cards/catalogos/form_acessorios.html', 
                             acessorios=Acessorio.query.order_by(Acessorio.nome).all(),
                             unidades_list=unidades_list,
                             classificacoes_list=classificacoes_list,
                             fornecedores_lista=fornecedores_lista,
                             empresas_lista=empresas_lista,
                             ace=ace)
    
    acessorios = Acessorio.query.order_by(Acessorio.nome).all()
    return render_template('cadastros/cards/catalogos/form_acessorios.html', 
                         acessorios=acessorios, 
                         unidades_list=unidades_list,
                         classificacoes_list=classificacoes_list,
                         fornecedores_lista=fornecedores_lista,
                         empresas_lista=empresas_lista,
                         ace=ace)


@cadastros_bp.route('/cards/acessorios/excluir/<int:id>', methods=['POST'])
def excluir_acessorio(id):
    ace = Acessorio.query.get_or_404(id)
    try:
        db.session.delete(ace)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

@cadastros_bp.route('/cards/acessorios/dados-json', methods=['GET'])
def exportar_acessorios_json():
    aces = Acessorio.query.order_by(Acessorio.nome).all()
    return jsonify([{'ID': a.id, 'Nome': a.nome, 'Referencia': a.referencia or '',
                     'Peso_g': a.peso_g, 'Custo': a.custo_unitario,
                     'Ativa': 'SIM' if a.ativa else 'NAO'} for a in aces])

@cadastros_bp.route('/cards/acessorios/pesquisa')
@login_required
def pesquisa_acessorios():
    q = request.args.get('q', '').strip()
    if len(q) < 2: return jsonify([])
    from app.models.catalogos import Acessorio
    aces = Acessorio.query.filter(
        (Acessorio.nome.ilike(f'%{q}%')) | 
        (Acessorio.referencia.ilike(f'%{q}%'))
    ).limit(20).all()
    return jsonify([{
        'id': a.id,
        'sku': a.referencia or '',
        'descricao': a.nome,
        'unidade': a.unidade.sigla if a.unidade else 'UN',
        'preco_custo': a.custo_unitario or 0.0
    } for a in aces])

@cadastros_bp.route('/cards/embalagens', methods=['GET', 'POST'])
@cadastros_bp.route('/cards/embalagens/<int:id>', methods=['GET', 'POST'])
@login_required
def card_embalagens(id=None):
    from app.models.catalogos import Embalagem, UnidadeMedida, FornecedorEmbalagem, ClassificacaoEmbalagem
    from app.models.cadastros.fornecedor import Fornecedor
    from app.models.cadastros.empresa import Empresa
    from flask_login import current_user
    
    # 🛡️ AriOne Multiempresa: Isolamento de Dados Master
    e_id = current_user.empresa_id
    
    # emb = Embalagem.query.filter_by(id=id, empresa_id=e_id).first() if id else None
    emb = Embalagem.query.get(id) if id else None
    unidades_list = UnidadeMedida.query.all() 
    # ⚠️ Fornecedores ainda não são multiempresa no banco, removendo filtro temporariamente
    fornecedores_lista = Fornecedor.query.filter_by(ativo=True).order_by(Fornecedor.razao_social).all()
    empresas_lista = Empresa.query.filter_by(ativa=True).all() 
    classificacoes_list = ClassificacaoEmbalagem.query.order_by(ClassificacaoEmbalagem.nome).all()

    if request.method == 'POST':
        nome = request.form.get('nome')
        if nome:
            if not emb: 
                emb = Embalagem()
                # emb.empresa_id = e_id # Vínculo Multiempresa na criação (Desativado temporariamente)
            emb.nome = nome
            emb.sku = request.form.get('sku')
            emb.tipo = request.form.get('tipo')
            emb.classificacao_id = request.form.get('classificacao_id')
            emb.unidade_id = request.form.get('unidade_id')
            
            def clean_money(val):
                if not val: return 0.0
                s = str(val).replace('R$', '').replace(' ', '').strip()
                # Se tem vírgula, é padrão BR (1.234,56). Removemos o ponto e trocamos a vírgula.
                if ',' in s:
                    s = s.replace('.', '').replace(',', '.')
                # Se não tem vírgula mas tem ponto, e o ponto está no final, é decimal (0.1128)
                # Se houver apenas um ponto e ele estiver longe do final, poderia ser milhar, 
                # mas em custos unitários de embalagem, quase sempre é decimal.
                return float(s or 0)
                
            emb.custo_compra = clean_money(request.form.get('custo_compra'))
            emb.fator_conversao = float(request.form.get('fator_conversao', 1) or 1)
            emb.custo_unitario = clean_money(request.form.get('custo_unitario'))
            
            emb.altura_mm = float(request.form.get('altura_mm', 0) or 0)
            emb.largura_mm = float(request.form.get('largura_mm', 0) or 0)
            emb.profundidade_mm = float(request.form.get('profundidade_mm', 0) or 0)
            
            db.session.add(emb)
            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                return jsonify({'success': False, 'message': str(e)}), 400

            # ── Lógica de Múltiplos Fornecedores ──
            # Limpa vínculos antigos
            FornecedorEmbalagem.query.filter_by(embalagem_id=emb.id).delete()
            
            forn_ids = request.form.getlist('forn_id[]')
            forn_ids = request.form.getlist('forn_id[]')
            forn_prazos = request.form.getlist('forn_prazos[]') # Corrigindo nome se necessário, mas mantendo forn_prazo[] do form
            forn_prazos = request.form.getlist('forn_prazo[]')
            forn_mods = request.form.getlist('forn_modalidade[]')

            for i in range(len(forn_ids)):
                if i < len(forn_ids) and forn_ids[i]:
                    novo_vinculo = FornecedorEmbalagem(
                        embalagem_id=emb.id,
                        fornecedor_id=int(forn_ids[i]),
                        preco_compra=emb.custo_compra, # Usando o custo global da embalagem
                        prazo_entrega=int(forn_prazos[i] or 1),
                        modalidade=forn_mods[i]
                    )

                    db.session.add(novo_vinculo)
            db.session.commit()

            # Lógica de Foto Embalagem
            if 'foto_embalagem' in request.files:
                file = request.files['foto_embalagem']
                if file and file.filename:
                    import os
                    from werkzeug.utils import secure_filename
                    filename = secure_filename(f"emb_{emb.id}_{file.filename}")
                    upload_path = os.path.join('app', 'static', 'uploads', 'embalagens')
                    os.makedirs(upload_path, exist_ok=True)
                    file.save(os.path.join(upload_path, filename))
                    emb.foto = filename
                    db.session.commit()

            flash('Integridade: Embalagem e Matriz de Fornecedores salvas!', 'success')
        return render_template('cadastros/cards/catalogos/form_embalagens.html', 
                             embalagens=Embalagem.query.order_by(Embalagem.nome).all(),
                             unidades_list=unidades_list,
                             fornecedores_lista=fornecedores_lista,
                             empresas_lista=empresas_lista,
                             classificacoes_list=classificacoes_list,
                             emb=emb)
    
    # 🛡️ Listagem GLOBAL (Multiempresa desativado por falta de coluna no DB)
    embalagens = Embalagem.query.order_by(Embalagem.nome).all()
    
    return render_template('cadastros/cards/catalogos/form_embalagens.html', 
                          embalagens=embalagens, 
                          unidades_list=unidades_list, 
                          fornecedores_lista=fornecedores_lista,
                          empresas_lista=empresas_lista,
                          classificacoes_list=classificacoes_list,
                          emb=emb)

@cadastros_bp.route('/cards/embalagens/excluir/<int:id>', methods=['POST'])
def excluir_embalagem(id):
    emb = Embalagem.query.get_or_404(id)
    try:
        db.session.delete(emb)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

@cadastros_bp.route('/cards/embalagens/dados-json', methods=['GET'])
def exportar_embalagens_json():
    embs = Embalagem.query.order_by(Embalagem.nome).all()
    return jsonify([{'ID': e.id, 'Nome': e.nome, 'Custo': e.custo_unitario,
                     'Estoque_Atual': e.estoque_atual, 'Altura_cm': e.altura_cm or 0,
                     'Largura_cm': e.largura_cm or 0, 'Prof_cm': e.profundidade_cm or 0,
                     'Peso_g': e.peso_proprio_g, 'Ativa': 'SIM' if e.ativa else 'NAO'} for e in embs])

@cadastros_bp.route('/cards/embalagens/pesquisa')
@login_required
def pesquisa_embalagens():
    q = request.args.get('q', '').strip()
    if len(q) < 2: return jsonify([])
    from app.models.catalogos import Embalagem
    embs = Embalagem.query.filter(
        (Embalagem.nome.ilike(f'%{q}%')) | 
        (Embalagem.sku.ilike(f'%{q}%'))
    ).limit(20).all()
    
    # 🛡️ Garantia de Integridade no Retorno JSON
    return jsonify([{
        'id': e.id,
        'sku': e.sku or str(e.id),
        'descricao': e.nome,
        'unidade': e.unidade.sigla if (hasattr(e, 'unidade') and e.unidade) else 'UN',
        'preco_custo': float(e.custo_unitario or 0) # Padronizado para preco_custo como o frontend espera
    } for e in embs])

@cadastros_bp.route('/cards/relatorios')
def card_relatorios():
    return render_template('cadastros/cards/catalogos/form_rel_catalogos.html')

@cadastros_bp.route('/cards/pessoas/relatorios')
def card_rel_pessoas():
    resp = make_response(render_template('cadastros/cards/pessoas/form_rel_pessoas.html'))
    resp.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate'
    return resp


# ── Estrutura Organizacional (Setores/Deptos) ───────────────────────────────

@cadastros_bp.route('/setores/novo', methods=['POST'])
@login_required
def cadastrar_setor():
    nome = request.form.get('nome')
    sigla = request.form.get('sigla')
    
    if not nome:
        return jsonify({'error': 'Nome é obrigatório'}), 400
        
    # Gerar código automático
    last = Setor.query.filter(Setor.codigo.like('SET-%')).order_by(Setor.id.desc()).first()
    next_num = 1
    if last:
        try:
            next_num = int(last.codigo.split('-')[1]) + 1
        except: pass
    codigo = f"SET-{str(next_num).zfill(3)}"
    
    # Se vier ID para edição
    edit_id = request.form.get('id')
    if edit_id:
        s = Setor.query.get(edit_id)
        if s:
            s.nome = nome
            s.sigla = sigla
    else:
        s = Setor(nome=nome, sigla=sigla, codigo=codigo)
        db.session.add(s)
        
    db.session.commit()
    return jsonify({'success': True, 'codigo': codigo})

@cadastros_bp.route('/departamentos/novo', methods=['POST'])
@login_required
def cadastrar_departamento():
    nome = request.form.get('nome')
    sigla = request.form.get('sigla')
    parent_id = request.form.get('parent_id')
    
    if not nome or not parent_id:
        return jsonify({'error': 'Nome e Setor Pai são obrigatórios'}), 400
        
    # Gerar código automático
    last = Setor.query.filter(Setor.codigo.like('DEP-%')).order_by(Setor.id.desc()).first()
    next_num = 1
    if last:
        try:
            next_num = int(last.codigo.split('-')[1]) + 1
        except: pass
    codigo = f"DEP-{str(next_num).zfill(3)}"
    
    edit_id = request.form.get('id')
    if edit_id:
        d = Setor.query.get(edit_id)
        if d:
            d.nome = nome
            d.sigla = sigla
            d.parent_id = parent_id
    else:
        d = Setor(nome=nome, sigla=sigla, codigo=codigo, parent_id=parent_id)
        db.session.add(d)
        
    db.session.commit()
    return jsonify({'success': True, 'codigo': codigo})

@cadastros_bp.route('/cargos/novo', methods=['POST'])
@login_required
def cadastrar_cargo():
    nome = request.form.get('nome')
    cbo = request.form.get('cbo')
    
    if not nome:
        return jsonify({'error': 'Nome é obrigatório'}), 400
        
    last = Cargo.query.filter(Cargo.codigo.like('CAR-%')).order_by(Cargo.id.desc()).first()
    next_num = 1
    if last:
        try:
            next_num = int(last.codigo.split('-')[1]) + 1
        except: pass
    codigo = f"CAR-{str(next_num).zfill(3)}"
    
    edit_id = request.form.get('id')
    if edit_id:
        c = Cargo.query.get(edit_id)
        if c:
            c.nome = nome
            c.cbo = cbo
    else:
        c = Cargo(nome=nome, cbo=cbo, codigo=codigo)
        db.session.add(c)
        
    db.session.commit()
    return jsonify({'success': True, 'codigo': codigo})

@cadastros_bp.route('/cargos/excluir/<int:id>')
@login_required
def excluir_cargo(id):
    c = Cargo.query.get_or_404(id)
    db.session.delete(c)
    db.session.commit()
    flash('Cargo excluído!', 'success')
    return redirect(url_for('cadastros.abas', aba='empresa'))

@cadastros_bp.route('/setores/excluir/<int:id>')
@login_required
def excluir_setor(id):
    s = Setor.query.get_or_404(id)
    db.session.delete(s)
    db.session.commit()
    flash('Setor/Departamento excluído!', 'success')
    return redirect(url_for('cadastros.abas', aba='empresa'))

@cadastros_bp.route('/socios/excluir/<int:id>')
@login_required
def excluir_socio(id):
    s = Socio.query.get_or_404(id)
    db.session.delete(s)
    db.session.commit()
    flash('Sócio excluído com sucesso!', 'success')
    return redirect(url_for('cadastros.abas', aba='empresa'))

@cadastros_bp.route('/investidores/excluir/<int:id>')
@login_required
def excluir_investidor(id):
    i = Investidor.query.get_or_404(id)
    db.session.delete(i)
    db.session.commit()
    flash('Investidor excluído com sucesso!', 'success')
    return redirect(url_for('cadastros.abas', aba='empresa'))


# ── Revendedores (Rede de Revendas) ──────────────────────────────────────────
@cadastros_bp.route('/revendedores/form', methods=['GET', 'POST'])
@cadastros_bp.route('/revendedores/form/<int:id>', methods=['GET', 'POST'])
@login_required
def form_revendedor(id=None):
    revendedor = Revendedor.query.get(id) if id else None
    revendedores_lista = Revendedor.query.order_by(Revendedor.nome).all()

    if request.method == 'POST':
        if not revendedor:
            revendedor = Revendedor()
        
        revendedor.nome            = request.form.get('nome')
        revendedor.cpf_cnpj        = request.form.get('cpf_cnpj')
        revendedor.categoria       = request.form.get('categoria')
        revendedor.tipo_revenda    = request.form.get('tipo_revenda')
        revendedor.regiao          = request.form.get('regiao')
        revendedor.rating          = request.form.get('rating')
        
        limite = request.form.get('limite', '0').replace('.', '').replace(',', '.')
        revendedor.limite_credito  = float(limite) if limite else 0.0
        
        revendedor.whatsapp        = request.form.get('whatsapp')
        revendedor.email           = request.form.get('email')
        revendedor.end_cep         = request.form.get('cep')
        revendedor.end_logradouro  = request.form.get('logradouro')
        revendedor.end_numero      = request.form.get('numero')
        revendedor.observacoes     = request.form.get('observacoes')

        # ── Upload de Foto
        if 'foto' in request.files:
            file = request.files['foto']
            if file and file.filename != '':
                upload_dir = os.path.join('static', 'img', 'revendedores')
                os.makedirs(upload_dir, exist_ok=True)
                ext = os.path.splitext(file.filename)[1]
                filename = secure_filename(f"rev_{revendedor.id or 'novo'}_{datetime.now().strftime('%m%d%H%M%S')}{ext}")
                file.save(os.path.join(upload_dir, filename))
                revendedor.foto = filename

        try:
            db.session.add(revendedor)
            db.session.commit()
            flash('Revendedor salvo com sucesso!', 'success')
            return redirect(url_for('cadastros.form_revendedor', id=revendedor.id))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao salvar: {str(e)}', 'danger')

    resp = make_response(render_template('cadastros/cards/pessoas/form_revendedor.html', 
                         revendedor=revendedor, 
                         revendedores_lista=revendedores_lista))
    resp.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate'
    return resp

# ── Influenciadores (Rede de Influência) ───────────────────────────────────────
@cadastros_bp.route('/influenciadores/form', methods=['GET', 'POST'])
@cadastros_bp.route('/influenciadores/form/<int:id>', methods=['GET', 'POST'])
@login_required
def form_influenciador(id=None):
    influenciador = Influenciador.query.get(id) if id else None
    influenciadores_lista = Influenciador.query.order_by(Influenciador.nome).all()

    if request.method == 'POST':
        if not influenciador:
            influenciador = Influenciador()
        
        influenciador.nome            = request.form.get('nome')
        influenciador.nicho           = request.form.get('nicho')
        influenciador.plataforma      = request.form.get('plataforma')
        influenciador.seguidores      = request.form.get('seguidores')
        influenciador.status_contrato = request.form.get('status_contrato')
        influenciador.whatsapp        = request.form.get('whatsapp')
        influenciador.email           = request.form.get('email')
        influenciador.instagram       = request.form.get('instagram')
        influenciador.observacoes     = request.form.get('observacoes')

        # ── Upload de Foto
        if 'foto' in request.files:
            file = request.files['foto']
            if file and file.filename != '':
                upload_dir = os.path.join('static', 'img', 'influenciadores')
                os.makedirs(upload_dir, exist_ok=True)
                ext = os.path.splitext(file.filename)[1]
                filename = secure_filename(f"inf_{influenciador.id or 'novo'}_{datetime.now().strftime('%m%d%H%M%S')}{ext}")
                file.save(os.path.join(upload_dir, filename))
                influenciador.foto = filename

        try:
            db.session.add(influenciador)
            db.session.commit()
            flash('Influenciador salvo com sucesso!', 'success')
            return redirect(url_for('cadastros.form_influenciador', id=influenciador.id))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao salvar: {str(e)}', 'danger')

    resp = make_response(render_template('cadastros/cards/pessoas/form_influenciador.html', 
                         influenciador=influenciador, 
                         influenciadores_lista=influenciadores_lista))
    resp.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate'
    return resp

# ── Estilistas (Parceiros Criativos) ──────────────────────────────────────────
@cadastros_bp.route('/estilistas/form', methods=['GET', 'POST'])
@cadastros_bp.route('/estilistas/form/<int:id>', methods=['GET', 'POST'])
@login_required
def form_estilista(id=None):
    estilista = Estilista.query.get(id) if id else None
    estilistas_lista = Estilista.query.order_by(Estilista.nome).all()

    if request.method == 'POST':
        if not estilista:
            estilista = Estilista()
        
        estilista.nome            = request.form.get('nome')
        estilista.especialidade   = request.form.get('especialidade')
        estilista.portfólio_url   = request.form.get('portfolio')
        estilista.disponibilidade = request.form.get('disponibilidade')
        estilista.whatsapp        = request.form.get('whatsapp')
        estilista.email           = request.form.get('email')
        estilista.observacoes      = request.form.get('observacoes')

        # ── Upload de Foto
        if 'foto' in request.files:
            file = request.files['foto']
            if file and file.filename != '':
                upload_dir = os.path.join('static', 'img', 'estilistas')
                os.makedirs(upload_dir, exist_ok=True)
                ext = os.path.splitext(file.filename)[1]
                filename = secure_filename(f"est_{estilista.id or 'novo'}_{datetime.now().strftime('%m%d%H%M%S')}{ext}")
                file.save(os.path.join(upload_dir, filename))
                estilista.foto = filename

        try:
            db.session.add(estilista)
            db.session.commit()
            flash('Estilista salvo com sucesso!', 'success')
            return redirect(url_for('cadastros.form_estilista', id=estilista.id))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao salvar: {str(e)}', 'danger')

    resp = make_response(render_template('cadastros/cards/pessoas/form_estilista.html', 
                         estilista=estilista, 
                         estilistas_lista=estilistas_lista))
    resp.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate'
    return resp



# ── Relatórios Comerciais ──────────────────────────────────────────────────
@cadastros_bp.route('/cards/comercial/com_relatorios')
@login_required
def com_relatorios():
    from app.models.cadastros.empresa import Empresa
    empresas_lista = Empresa.query.order_by(Empresa.razao_social).all()
    return render_template('cadastros/cards/comercial/form_relatorios.html', empresas_lista=empresas_lista)
@cadastros_bp.route('/produtos/catalogos/modelos')
@cadastros_bp.route('/produtos/catalogos/modelos/<int:id>')
@login_required
def catalogo_modelos_edit(id=None):
    from app.models.catalogos import ModeloCatalogo
    modelo = ModeloCatalogo.query.get(id) if id else None
    modelos = ModeloCatalogo.query.order_by(ModeloCatalogo.nome).all()
    return render_template('cadastros/cards/catalogos/form_modelos.html', modelo=modelo, modelos=modelos)

@cadastros_bp.route('/produtos/catalogos/modelos/save', methods=['POST'])
@login_required
def catalogo_modelos_save():
    from app.models.catalogos import ModeloCatalogo
    id = request.form.get('id')
    nome = request.form.get('nome')
    sigla = request.form.get('sigla')
    ativa = request.form.get('ativa') == '1'

    if id and id != '0':
        modelo = ModeloCatalogo.query.get(id)
    else:
        modelo = ModeloCatalogo()
        db.session.add(modelo)

    modelo.nome = nome
    modelo.sigla = sigla
    modelo.ativa = ativa

    try:
        db.session.commit()
        flash("Modelo salvo com sucesso!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Erro ao salvar modelo: {e}", "danger")

    return redirect(url_for('cadastros.catalogo_modelos_edit'))


# ── Perfis de Venda (Catálogos) ─────────────────────────────────────────────
@cadastros_bp.route('/perfis-venda/form', methods=['GET', 'POST'])
@cadastros_bp.route('/perfis-venda/form/<int:id>', methods=['GET', 'POST'])
@login_required
def form_perfil_venda(id=None):
    perfil = PerfilVenda.query.get(id) if id else None
    
    if request.method == 'POST':
        try:
            if not perfil:
                perfil = PerfilVenda()
            
            perfil.nome = request.form.get('nome').upper()
            perfil.descricao = request.form.get('descricao')
            perfil.ativa = request.form.get('status') == 'ATIVO'
            
            db.session.add(perfil)
            db.session.commit()
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify(success=True, message="Perfil salvo com sucesso!")
            
            flash("Perfil salvo com sucesso!", "success")
            return redirect(url_for('cadastros.form_perfil_venda'))
        except Exception as e:
            db.session.rollback()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify(success=False, error=str(e))
            flash(f"Erro ao salvar: {e}", "danger")

    perfis = PerfilVenda.query.order_by(PerfilVenda.nome).all()
    is_modal = request.args.get('modal') == '1'
    return render_template('cadastros/cards/catalogos/form_perfil_venda.html', 
                           perfil=perfil, perfis=perfis, is_modal=is_modal)

@cadastros_bp.route('/perfis-venda/excluir/<int:id>')
@login_required
def excluir_perfil_venda(id):
    perfil = PerfilVenda.query.get_or_404(id)
    try:
        db.session.delete(perfil)
        db.session.commit()
        flash("Perfil excluído com sucesso!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Erro ao excluir: {e}", "danger")
    return redirect(url_for('cadastros.form_perfil_venda'))

# ── Vendedores ──────────────────────────────────────────────────────────────
@cadastros_bp.route('/vendedores/form', methods=['GET', 'POST'])
@cadastros_bp.route('/vendedores/form/<int:id>', methods=['GET', 'POST'])
@login_required
def form_vendedor(id=None):
    from app.models.comercial.models import Vendedor, CanalVenda
    from app.models.cadastros.funcionario import Funcionario
    from app.utils.helpers import parse_money
    
    vendedor = Vendedor.query.get(id) if id else None
    vendedores_lista = Vendedor.query.filter_by(empresa_id=session.get('empresa_id')).all()
    
    # Lista de Canais Digitais (ChatOne / Omnichannel)
    canais_digitais = CanalVenda.query.filter_by(empresa_id=session.get('empresa_id', 1)).order_by(CanalVenda.nome).all()
    
    # Lista de IDs já usados (para não repetir)
    usados = [v.funcionario_id for v in Vendedor.query.filter_by(empresa_id=session.get('empresa_id')).all() if v.id != id]
    
    funcionarios = Funcionario.query.filter(
        Funcionario.empresa_id == session.get('empresa_id'),
        Funcionario.ativo == True,
        ~Funcionario.id.in_(usados) if usados else True
    ).order_by(Funcionario.nome).all()

    if request.method == 'POST':
        try:
            if not vendedor:
                vendedor = Vendedor(empresa_id=session.get('empresa_id'))
            
            vendedor.funcionario_id = request.form.get('funcionario_id')
            vendedor.nome_exibivel   = request.form.get('nome_exibivel')
            vendedor.comissao_padrao = parse_money(request.form.get('comissao_padrao', '0'))
            vendedor.meta_mensal     = parse_money(request.form.get('meta_mensal', '0'))
            vendedor.cor_identidade  = request.form.get('cor_identidade', '#2980B9')
            vendedor.canais_venda    = ", ".join(request.form.getlist('canais_venda[]'))
            vendedor.ativo           = 'ativo' in request.form

            db.session.add(vendedor)
            db.session.commit()
            flash('Consultor salvo com sucesso!', 'success')
            return redirect(url_for('cadastros.form_vendedor', id=vendedor.id))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao salvar: {str(e)}', 'danger')

    is_modal = request.args.get('modal') == '1'
    return render_template('cadastros/cards/pessoas/form_vendedor.html', 
                           vendedor=vendedor, vendedores_lista=vendedores_lista, 
                           funcionarios=funcionarios, canais_digitais=canais_digitais, is_modal=is_modal)

@cadastros_bp.route('/vendedores/excluir/<int:id>')
@login_required
def excluir_vendedor(id):
    from app.models.comercial.models import Vendedor
    vendedor = Vendedor.query.get_or_404(id)
    try:
        db.session.delete(vendedor)
        db.session.commit()
        flash('Consultor removido com sucesso.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao excluir: {str(e)}', 'danger')
    return redirect(url_for('cadastros.form_vendedor'))