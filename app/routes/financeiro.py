from flask import Blueprint, render_template, request, session
from flask_login import login_required
from app.extensions import db
from app.utils.helpers import parse_money
from sqlalchemy import case

financeiro_bp = Blueprint("financeiro", __name__, url_prefix="/financeiro")

@financeiro_bp.before_app_request
def setup_financeiro():
    """Auto-migração para tabelas financeiras."""
    from sqlalchemy import text
    try:
        with db.engine.begin() as conn:
            # Operadoras Financeiras
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS comercial_operadoras_financeiras (
                    id INTEGER PRIMARY KEY,
                    nome VARCHAR(100) NOT NULL,
                    nome_fantasia VARCHAR(100),
                    cnpj VARCHAR(20),
                    site VARCHAR(255),
                    email_suporte VARCHAR(100),
                    telefone_suporte VARCHAR(20),
                    taxa_debito FLOAT DEFAULT 0,
                    taxa_pix FLOAT DEFAULT 0,
                    taxa_credito_vista FLOAT DEFAULT 0,
                    taxa_credito_parcelado FLOAT DEFAULT 0,
                    taxa_antecipacao FLOAT DEFAULT 0,
                    taxas_parcelamento TEXT,
                    icone VARCHAR(50) DEFAULT 'fas fa-landmark',
                    cor VARCHAR(20) DEFAULT '#2980B9',
                    ativa BOOLEAN DEFAULT 1,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            # Formas de Pagamento
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS comercial_formas_pagamento (
                    id INTEGER PRIMARY KEY,
                    nome VARCHAR(100) NOT NULL,
                    agrupador_operacional VARCHAR(50) DEFAULT 'OUTROS',
                    baixa_automatica BOOLEAN DEFAULT 0,
                    tipo VARCHAR(50) DEFAULT 'DINHEIRO',
                    operadora_id INTEGER,
                    max_parcelas INTEGER DEFAULT 1,
                    intervalo_dias INTEGER DEFAULT 0,
                    parcela_minima FLOAT DEFAULT 0,
                    taxa_juros FLOAT DEFAULT 0,
                    percentual_desconto FLOAT DEFAULT 0,
                    icone VARCHAR(50) DEFAULT 'fas fa-money-bill-wave',
                    cor VARCHAR(20) DEFAULT '#2ECC71',
                    ativa BOOLEAN DEFAULT 1,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (operadora_id) REFERENCES comercial_operadoras_financeiras(id)
                )
            """))
            
            # Verificações de Migração Incremental
            result = conn.execute(text("PRAGMA table_info(comercial_operadoras_financeiras)"))
            cols = [row[1] for row in result]
            if 'taxa_pix' not in cols:
                try: conn.execute(text('ALTER TABLE comercial_operadoras_financeiras ADD COLUMN taxa_pix FLOAT DEFAULT 0'))
                except: pass
            if 'taxas_parcelamento' not in cols:
                try: conn.execute(text('ALTER TABLE comercial_operadoras_financeiras ADD COLUMN taxas_parcelamento TEXT'))
                except: pass
            
            # Verifica se a coluna agrupador_operacional existe (Migração Incremental)
            result = conn.execute(text("PRAGMA table_info(comercial_formas_pagamento)"))
            cols = [row[1] for row in result]
            if 'agrupador_operacional' not in cols:
                try: conn.execute(text('ALTER TABLE comercial_formas_pagamento ADD COLUMN agrupador_operacional VARCHAR(50) DEFAULT "OUTROS"'))
                except: pass
            
            if 'baixa_automatica' not in cols:
                try: conn.execute(text('ALTER TABLE comercial_formas_pagamento ADD COLUMN baixa_automatica BOOLEAN DEFAULT 0'))
                except: pass
            
            if 'operadora_id' not in cols:
                try: conn.execute(text('ALTER TABLE comercial_formas_pagamento ADD COLUMN operadora_id INTEGER REFERENCES comercial_operadoras_financeiras(id)'))
                except: pass

            # 🏢 Centros de Custo (Migração Híbrida)
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS centros_custo (
                    id INTEGER PRIMARY KEY,
                    empresa_id INTEGER,
                    pai_id INTEGER,
                    codigo VARCHAR(20) NOT NULL UNIQUE,
                    nome VARCHAR(100) NOT NULL,
                    tipo VARCHAR(20) DEFAULT 'Operacional',
                    orcamento_mensal DECIMAL(15,2) DEFAULT 0,
                    ativo BOOLEAN DEFAULT 1,
                    contabil_cod VARCHAR(50),
                    pix VARCHAR(100),
                    criado_em DATETIME DEFAULT CURRENT_TIMESTAMP,
                    atualizado_em DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            result = conn.execute(text("PRAGMA table_info(centros_custo)"))
            cols = [row[1] for row in result]
            if 'empresa_id' not in cols:
                try: conn.execute(text("ALTER TABLE centros_custo ADD COLUMN empresa_id INTEGER REFERENCES empresas(id)"))
                except: pass
            if 'pai_id' not in cols:
                try: conn.execute(text("ALTER TABLE centros_custo ADD COLUMN pai_id INTEGER REFERENCES centros_custo(id)"))
                except: pass
            if 'orcamento_mensal' not in cols:
                try: conn.execute(text("ALTER TABLE centros_custo ADD COLUMN orcamento_mensal DECIMAL(15,2) DEFAULT 0"))
                except: pass
            if 'atualizado_em' not in cols:
                try: conn.execute(text("ALTER TABLE centros_custo ADD COLUMN atualizado_em DATETIME DEFAULT CURRENT_TIMESTAMP"))
                except: pass

    except Exception as e:
        print(f"Erro na migração financeira: {e}")

@financeiro_bp.route("/")
def abas():
    abas = [
        {"id": "contas",   "label": "Contas",   "icon": "fas fa-receipt"},
        {"id": "caixas",   "label": "Caixas",   "icon": "fas fa-cash-register"},
        {"id": "fluxo",    "label": "Fluxo & Projeções", "icon": "fas fa-chart-line"},
        {"id": "bancos",   "label": "Bancos",   "icon": "fas fa-university"},
        {"id": "gerencial","label": "Gerencial", "icon": "fas fa-sitemap"},
    ]
    aba_ativa = request.args.get("aba", "contas")
    if aba_ativa not in [a["id"] for a in abas]:
        aba_ativa = "contas"

    return render_template(
        "financeiro/abas_financeiro.html",
        abas=abas,
        aba_ativa=aba_ativa
    )

@financeiro_bp.route("/card/gateway/modulos")
def gateway_modulos_financeiro():
    return render_template('financeiro/cards/form_gateway_modulos_financeiro.html')

@financeiro_bp.route("/cards/relatorios")
def card_financeiro_relatorios():
    modulo = request.args.get('modulo', 'contas')
    titulos = {
        'contas': 'Relatórios de Contas',
        'caixas': 'Relatórios de Caixas',
        'bancos': 'Relatórios Bancários',
        'gerencial': 'Relatórios Gerenciais'
    }
    cores = {
        'contas': '#27AE60',
        'caixas': '#16A085',
        'bancos': '#2980B9',
        'gerencial': '#8E44AD'
    }
    return render_template('financeiro/cards/form_financeiro_relatorios.html', 
                            titulo=titulos.get(modulo, 'Relatórios Financeiros'), 
                            cor=cores.get(modulo, '#27AE60'), 
                            modulo=modulo)

@financeiro_bp.route("/cards/receitas")
def card_receitas():
    return render_template("financeiro/cards/form_financeiro_receitas.html", titulo='Lançar Receita')

@financeiro_bp.route("/cards/despesas")
def card_despesas():
    return render_template("financeiro/cards/form_financeiro_despesas.html", titulo='Lançar Despesa')

@financeiro_bp.route("/api/centro-custo/proximo-codigo")
@login_required
def proximo_codigo_cc():
    from app.models.gestao.centro_custo import CentroCusto
    e_id = session.get('empresa_id')
    pai_id = request.args.get('pai_id', type=int)
    
    if pai_id:
        pai = CentroCusto.query.get(pai_id)
        # Busca o último filho deste pai
        ultimo_filho = CentroCusto.query.filter_by(empresa_id=e_id, pai_id=pai_id).order_by(CentroCusto.codigo.desc()).first()
        if ultimo_filho:
            # Pega o sufixo numérico e incrementa
            partes = ultimo_filho.codigo.split('.')
            proximo_num = int(partes[-1]) + 1
            codigo = f"{pai.codigo}.{proximo_num:02d}"
        else:
            codigo = f"{pai.codigo}.01"
    else:
        # Busca o último raiz
        ultimo_raiz = CentroCusto.query.filter_by(empresa_id=e_id, pai_id=None).order_by(CentroCusto.codigo.desc()).first()
        if ultimo_raiz:
            proximo_num = int(ultimo_raiz.codigo.split('.')[0]) + 1
            codigo = f"{proximo_num:02d}"
        else:
            codigo = "01"
            
    return {"codigo": codigo}

@financeiro_bp.route("/api/centro-custo/excluir/<int:id>", methods=['POST'])
@login_required
def excluir_centro_custo(id):
    from app.models.gestao.centro_custo import CentroCusto
    try:
        cc = CentroCusto.query.get_or_404(id)
        db.session.delete(cc)
        db.session.commit()
        return {"success": True, "message": "Centro de Custo excluído com sucesso!"}
    except Exception as e:
        db.session.rollback()
        return {"success": False, "error": str(e)}, 500

@financeiro_bp.route("/cards/centro-custos", methods=['GET', 'POST'])
@login_required
def form_centro_custo():
    from app.models.gestao.centro_custo import CentroCusto
    
    e_id = session.get('empresa_id')
    id_cc = request.args.get('id', type=int)
    cc = CentroCusto.query.get(id_cc) if id_cc else None
    
    # 📑 Lista para o formulário (Pais) e Listagem Geral
    pais = CentroCusto.query.filter_by(empresa_id=e_id, pai_id=None).all()
    centros_lista = CentroCusto.query.filter_by(empresa_id=e_id).order_by(CentroCusto.codigo).all()
    
    if request.method == 'POST':
        try:
            if not cc:
                cc = CentroCusto(empresa_id=e_id)
                cc.codigo = request.form.get('codigo')
            else:
                cc.codigo = request.form.get('codigo')
            
            cc.nome = request.form.get('nome').upper() 
            cc.tipo = request.form.get('tipo')
            cc.pai_id = request.form.get('pai_id') if request.form.get('pai_id') else None
            cc.orcamento_mensal = parse_money(request.form.get('orcamento_mensal') or '0')
            cc.contabil_cod = request.form.get('contabil_cod')
            cc.pix = request.form.get('pix')
            cc.ativo = True if request.form.get('ativo') == 'on' else False
            
            db.session.add(cc)
            db.session.commit()
            return {"success": True, "message": "Centro de Custo salvo com sucesso!"}
        except Exception as e:
            db.session.rollback()
            return {"success": False, "error": str(e)}, 500
            
    from app.models.gestao.plano_contas import PlanoContas
    
    # 🛡️ Auto-Seed: Garantir dados mínimos para teste se estiver vazio
    if PlanoContas.query.count() == 0:
        contas_seed = [
            {'cod': '3.01.001', 'desc': 'COMPRA DE MERCADORIA PARA REVENDA', 'tipo': 'DESPESA'},
            {'cod': '3.01.002', 'desc': 'DESPESAS COM LOGÍSTICA E FRETE', 'tipo': 'DESPESA'},
            {'cod': '3.01.003', 'desc': 'MANUTENÇÃO E CONSERVAÇÃO', 'tipo': 'DESPESA'}
        ]
        for c in contas_seed:
            db.session.add(PlanoContas(codigo=c['cod'], descricao=c['desc'], tipo=c['tipo'], empresa_id=session.get('empresa_id')))
        db.session.commit()

    plano_contas = PlanoContas.query.filter_by(ativo=True).order_by(PlanoContas.codigo).all()
    
    return render_template("financeiro/cards/form_financeiro_centro_de_custos.html", cc=cc, pais=pais, centros_lista=centros_lista, plano_contas=plano_contas)

# ── Formas de Pagamento (Quiet Luxury Standard) ─────────────────────────────
@financeiro_bp.route('/card/pagamentos')
def card_formas_pagamento():
    from app.models.comercial.models import FormaPagamento, OperadoraFinanceira
    pagamentos = FormaPagamento.query.order_by(FormaPagamento.tipo, FormaPagamento.nome).all()
    operadoras = OperadoraFinanceira.query.filter_by(ativa=True).order_by(OperadoraFinanceira.nome).all()
    return render_template('financeiro/cards/form_financeiro_forma_pagamentos.html', 
                           pagamentos=pagamentos, 
                           operadoras=operadoras, 
                           is_modal=True)

@financeiro_bp.route('/card/pagamentos/salvar', methods=['POST'])
def salvar_forma_pagamento():
    from app.models.comercial.models import FormaPagamento
    try:
        pid = request.form.get('id')
        if pid:
            pag = FormaPagamento.query.get(pid)
        else:
            pag = FormaPagamento()
        
        pag.nome = request.form.get('nome').upper()
        pag.agrupador_operacional = request.form.get('agrupador_operacional') or 'OUTROS'
        pag.baixa_automatica = True if request.form.get('baixa_automatica') == 'SIM' else False
        
        # Campos simplificados (Legacy ou Automáticos)
        pag.tipo = request.form.get('tipo') or 'OUTROS'
        pag.icone = request.form.get('icone', 'fas fa-credit-card')
        pag.cor = request.form.get('cor', '#2980B9')
        
        db.session.add(pag)
        db.session.commit()
        return {"success": True, "message": "Forma de Pagamento salva com sucesso!"}
    except Exception as e:
        db.session.rollback()
        return {"success": False, "error": str(e)}, 500

@financeiro_bp.route('/card/pagamentos/excluir/<int:id>', methods=['POST'])
def excluir_forma_pagamento(id):
    from app.models.comercial.models import FormaPagamento
    try:
        pag = FormaPagamento.query.get_or_404(id)
        db.session.delete(pag)
        db.session.commit()
        return {"success": True, "message": "Excluído com sucesso!"}
    except Exception as e:
        db.session.rollback()
        return {"success": False, "error": str(e)}, 500

@financeiro_bp.route('/card/pagamentos/seed', methods=['POST'])
def seed_formas_pagamento():
    from app.models.comercial.models import FormaPagamento
    try:
        # Limpa as formas existentes para evitar duplicatas e garantir o novo padrão
        FormaPagamento.query.delete()
        
        defaults = [
            {'nome': 'DINHEIRO - ESPÉCIE', 'agrupador_operacional': 'Á VISTA', 'baixa_automatica': True, 'icone': 'fas fa-money-bill-wave', 'cor': '#27AE60'},
            {'nome': 'PIX - TRANSFERÊNCIA', 'agrupador_operacional': 'DIGITAL', 'baixa_automatica': True, 'icone': 'fab fa-pix', 'cor': '#32BCAD'},
            {'nome': 'CARTÃO - DÉBITO', 'agrupador_operacional': 'CARTÃO', 'baixa_automatica': True, 'icone': 'fas fa-credit-card', 'cor': '#2980B9'},
            {'nome': 'CARTÃO - CRÉDITO', 'agrupador_operacional': 'CARTÃO', 'baixa_automatica': False, 'icone': 'fas fa-credit-card', 'cor': '#8E44AD'},
            {'nome': 'BOLETO - BANCÁRIO', 'agrupador_operacional': 'BANCÁRIOS', 'baixa_automatica': False, 'icone': 'fas fa-barcode', 'cor': '#2C3E50'},
            {'nome': 'CARNÊ - LOJA', 'agrupador_operacional': 'A PRAZO', 'baixa_automatica': False, 'icone': 'fas fa-book', 'cor': '#D35400'},
            {'nome': 'CRÉDITO - ESPECIAL', 'agrupador_operacional': 'CRÉDITO', 'baixa_automatica': False, 'icone': 'fas fa-star', 'cor': '#F1C40F'},
            {'nome': 'A RECEBER - PRAZO', 'agrupador_operacional': 'A PRAZO', 'baixa_automatica': False, 'icone': 'fas fa-calendar-alt', 'cor': '#34495E'},
            {'nome': 'A PAGAR - PRAZO', 'agrupador_operacional': 'A PRAZO', 'baixa_automatica': False, 'icone': 'fas fa-calendar-minus', 'cor': '#E67E22'},
            {'nome': 'VALE - ADIANTAMENTOS', 'agrupador_operacional': 'OUTROS', 'baixa_automatica': True, 'icone': 'fas fa-ticket-alt', 'cor': '#16A085'},
            {'nome': 'OUTROS - NÃO ESPECIFICADOS', 'agrupador_operacional': 'OUTROS', 'baixa_automatica': False, 'icone': 'fas fa-question-circle', 'cor': '#95A5A6'},
            {'nome': 'LINK DE PAGAMENTOS', 'agrupador_operacional': 'DIGITAL', 'baixa_automatica': False, 'icone': 'fas fa-link', 'cor': '#2980B9'},
            {'nome': 'DUPLICATAS', 'agrupador_operacional': 'BANCÁRIOS', 'baixa_automatica': False, 'icone': 'fas fa-copy', 'cor': '#7F8C8D'},
            {'nome': 'TRANSF. BANCÁRIA (TED/DOC)', 'agrupador_operacional': 'BANCÁRIOS', 'baixa_automatica': True, 'icone': 'fas fa-exchange-alt', 'cor': '#2980B9'},
            {'nome': 'DEPÓSITO IDENTIFICADO', 'agrupador_operacional': 'BANCÁRIOS', 'baixa_automatica': True, 'icone': 'fas fa-university', 'cor': '#16A085'},
            {'nome': 'PERMUTA', 'agrupador_operacional': 'OUTROS', 'baixa_automatica': True, 'icone': 'fas fa-sync', 'cor': '#8E44AD'},
            {'nome': 'GATEWAYS DE PAGAMENTOS', 'agrupador_operacional': 'DIGITAL', 'baixa_automatica': False, 'icone': 'fas fa-handshake', 'cor': '#00B1EA'},
        ]
        for d in defaults:
            db.session.add(FormaPagamento(**d))
        db.session.commit()
        return {"success": True, "message": "Formas de Pagamento resetadas e configuradas com sucesso!"}
    except Exception as e:
        db.session.rollback()
        return {"success": False, "error": str(e)}, 500

# ── Operadoras Financeiras (Quiet Luxury Standard) ─────────────────────────
@financeiro_bp.route('/card/operadoras')
def card_operadoras():
    from app.models.comercial.models import OperadoraFinanceira
    operadoras = OperadoraFinanceira.query.order_by(OperadoraFinanceira.nome).all()
    return render_template('financeiro/cards/form_financeiro_operadora.html', operadoras=operadoras, is_modal=True)

@financeiro_bp.route('/card/operadoras/salvar', methods=['POST'])
def salvar_operadora():
    from app.models.comercial.models import OperadoraFinanceira
    try:
        oid = request.form.get('id')
        if oid:
            op = OperadoraFinanceira.query.get(oid)
        else:
            op = OperadoraFinanceira()
        
        op.nome = request.form.get('nome').upper()
        op.nome_fantasia = request.form.get('nome_fantasia', '').upper()
        op.cnpj = request.form.get('cnpj')
        op.site = request.form.get('site')
        op.email_suporte = request.form.get('email_suporte')
        op.telefone_suporte = request.form.get('telefone_suporte')
        
        op.taxa_debito = float(request.form.get('taxa_debito', '0').replace('.', '').replace(',', '.'))
        op.taxa_pix = float(request.form.get('taxa_pix', '0').replace('.', '').replace(',', '.'))
        op.taxa_credito_vista = float(request.form.get('taxa_credito_vista', '0').replace('.', '').replace(',', '.'))
        op.taxa_credito_parcelado = float(request.form.get('taxa_credito_parcelado', '0').replace('.', '').replace(',', '.'))
        op.taxa_antecipacao = float(request.form.get('taxa_antecipacao', '0').replace('.', '').replace(',', '.'))
        
        # Captura as taxas por parcelas (JSON enviado pelo front)
        op.taxas_parcelamento = request.form.get('taxas_parcelamento')
        
        op.icone = request.form.get('icone', 'fas fa-landmark')
        op.cor = request.form.get('cor', '#2980B9')
        
        db.session.add(op)
        db.session.commit()
        return {"success": True, "message": "Operadora Financeira salva com sucesso!"}
    except Exception as e:
        db.session.rollback()
        return {"success": False, "error": str(e)}, 500

@financeiro_bp.route('/card/operadoras/excluir/<int:id>', methods=['POST'])
def excluir_operadora(id):
    from app.models.comercial.models import OperadoraFinanceira
    try:
        op = OperadoraFinanceira.query.get_or_404(id)
        db.session.delete(op)
        db.session.commit()
        return {"success": True, "message": "Operadora excluída com sucesso!"}
    except Exception as e:
        db.session.rollback()
        return {"success": False, "error": str(e)}, 500

@financeiro_bp.route('/card/operadoras/seed', methods=['POST'])
def seed_operadoras():
    from app.models.comercial.models import OperadoraFinanceira
    try:
        defaults = [
            {'nome': 'PAYPAL', 'nome_fantasia': 'PAYPAL BRASIL', 'site': 'https://www.paypal.com', 'icone': 'fab fa-paypal', 'cor': '#003087'},
            {'nome': 'MERCADO PAGO', 'nome_fantasia': 'MERCADO PAGO', 'site': 'https://www.mercadopago.com.br', 'icone': 'fas fa-handshake', 'cor': '#00B1EA'},
            {'nome': 'PAGSEGURO', 'nome_fantasia': 'PAGBANK', 'site': 'https://www.pagseguro.uol.com.br', 'icone': 'fas fa-wallet', 'cor': '#53D337'},
            {'nome': 'CIELO', 'nome_fantasia': 'CIELO S.A.', 'site': 'https://www.cielo.com.br', 'icone': 'fas fa-credit-card', 'cor': '#005596'},
            {'nome': 'STONE', 'nome_fantasia': 'STONE PAGAMENTOS', 'site': 'https://www.stone.com.br', 'icone': 'fas fa-gem', 'cor': '#00A859'},
        ]
        for d in defaults:
            if not OperadoraFinanceira.query.filter_by(nome=d['nome']).first():
                db.session.add(OperadoraFinanceira(**d))
        db.session.commit()
        return {"success": True, "message": "Operadoras configuradas!"}
    except Exception as e:
        db.session.rollback()
        return {"success": False, "error": str(e)}, 500

# ── Plano de Contas Gerencial ──────────────────────────────────────────────
@financeiro_bp.route('/card/plano-contas')
@login_required
def card_plano_contas():
    from app.models.gestao.plano_contas import PlanoContas
    e_id = session.get('empresa_id')
    contas = PlanoContas.query.filter_by(empresa_id=e_id).order_by(PlanoContas.codigo).all()
    return render_template('financeiro/cards/form_financeiro_plano_contas.html', contas=contas)

@financeiro_bp.route("/api/plano-contas/proximo-codigo")
@login_required
def proximo_codigo_pc():
    from app.models.gestao.plano_contas import PlanoContas
    e_id = session.get('empresa_id')
    pai_codigo = request.args.get('pai_codigo', '')
    
    if pai_codigo:
        contas_filhas = PlanoContas.query.filter(
            PlanoContas.empresa_id == e_id,
            PlanoContas.codigo.like(f"{pai_codigo}.%")
        ).all()
        
        pontos_pai = pai_codigo.count('.')
        filhos_diretos = [c for c in contas_filhas if c.codigo.count('.') == pontos_pai + 1]
        
        if filhos_diretos:
            def get_last_num(c):
                try: return int(c.codigo.split('.')[-1])
                except: return 0
            ultimo = sorted(filhos_diretos, key=get_last_num)[-1]
            partes = ultimo.codigo.split('.')
            proximo_num = int(partes[-1]) + 1
            formato = len(partes[-1])
            codigo = f"{pai_codigo}.{str(proximo_num).zfill(formato)}"
        else:
            if pontos_pai >= 1:
                codigo = f"{pai_codigo}.001"
            else:
                codigo = f"{pai_codigo}.1"
    else:
        contas_raiz = PlanoContas.query.filter(
            PlanoContas.empresa_id == e_id,
            ~PlanoContas.codigo.like("%.%")
        ).all()
        
        if contas_raiz:
            nums = [int(c.codigo) for c in contas_raiz if c.codigo.isdigit()]
            if nums:
                codigo = str(max(nums) + 1)
            else:
                codigo = "1"
        else:
            codigo = "1"
            
    return {"codigo": codigo}


@financeiro_bp.route('/card/plano-contas/seed', methods=['POST'])
@login_required
def seed_plano_contas():
    from app.models.gestao.plano_contas import PlanoContas
    e_id = session.get('empresa_id')
    try:
        # Estrutura Sugerida pelo Gemini/Agente
        seed = [
            # 1. RECEITAS OPERACIONAIS
            {'codigo': '1', 'descricao': 'RECEITAS', 'tipo': 'RECEITA', 'natureza': 'SINTETICA', 'grupo': 'R'},
            {'codigo': '1.1', 'descricao': 'RECEITAS DE VENDAS', 'tipo': 'RECEITA', 'natureza': 'SINTETICA', 'grupo': 'R'},
            {'codigo': '1.1.001', 'descricao': 'VENDA DE PRODUTOS', 'tipo': 'RECEITA', 'natureza': 'ANALITICA', 'grupo': 'R'},
            {'codigo': '1.1.002', 'descricao': 'PRESTAÇÃO DE SERVIÇOS', 'tipo': 'RECEITA', 'natureza': 'ANALITICA', 'grupo': 'R'},
            {'codigo': '1.2', 'descricao': 'RECEITAS FINANCEIRAS', 'tipo': 'RECEITA', 'natureza': 'ANALITICA', 'grupo': 'R'},
            {'codigo': '1.3', 'descricao': 'OUTRAS RECEITAS OPERACIONAIS', 'tipo': 'RECEITA', 'natureza': 'ANALITICA', 'grupo': 'R'},

            # 2. DEDUÇÕES E IMPOSTOS
            {'codigo': '2', 'descricao': 'DEDUÇÕES E IMPOSTOS', 'tipo': 'DESPESA', 'natureza': 'SINTETICA', 'grupo': 'D'},
            {'codigo': '2.1', 'descricao': 'IMPOSTOS SOBRE VENDAS (SIMPLES/ICMS/ISS)', 'tipo': 'DESPESA', 'natureza': 'ANALITICA', 'grupo': 'D'},
            {'codigo': '2.2', 'descricao': 'DEVOLUÇÕES E CANCELAMENTOS', 'tipo': 'DESPESA', 'natureza': 'ANALITICA', 'grupo': 'D'},

            # 3. CUSTOS VARIÁVEIS (CPV/CMV)
            {'codigo': '3', 'descricao': 'CUSTOS VARIÁVEIS', 'tipo': 'DESPESA', 'natureza': 'SINTETICA', 'grupo': 'D'},
            {'codigo': '3.1', 'descricao': 'MATÉRIA-PRIMA E INSUMOS', 'tipo': 'DESPESA', 'natureza': 'ANALITICA', 'grupo': 'D'},
            {'codigo': '3.2', 'descricao': 'EMBALAGENS E LOGÍSTICA', 'tipo': 'DESPESA', 'natureza': 'ANALITICA', 'grupo': 'D'},
            {'codigo': '3.3', 'descricao': 'COMISSÕES DE VENDAS', 'tipo': 'DESPESA', 'natureza': 'ANALITICA', 'grupo': 'D'},
            {'codigo': '3.4', 'descricao': 'TAXAS DE CARTÃO / GATEWAYS', 'tipo': 'DESPESA', 'natureza': 'ANALITICA', 'grupo': 'D'},

            # 4. DESPESAS FIXAS (OPERACIONAIS)
            {'codigo': '4', 'descricao': 'DESPESAS FIXAS', 'tipo': 'DESPESA', 'natureza': 'SINTETICA', 'grupo': 'D'},
            {'codigo': '4.1', 'descricao': 'DESPESAS COM PESSOAL', 'tipo': 'DESPESA', 'natureza': 'SINTETICA', 'grupo': 'D'},
            {'codigo': '4.1.001', 'descricao': 'SALÁRIOS E ORDENADOS', 'tipo': 'DESPESA', 'natureza': 'ANALITICA', 'grupo': 'D'},
            {'codigo': '4.1.002', 'descricao': 'PRO-LABORE (SÓCIOS)', 'tipo': 'DESPESA', 'natureza': 'ANALITICA', 'grupo': 'D'},
            {'codigo': '4.1.003', 'descricao': 'ENCARGOS E BENEFÍCIOS', 'tipo': 'DESPESA', 'natureza': 'ANALITICA', 'grupo': 'D'},
            
            {'codigo': '4.2', 'descricao': 'OCUPAÇÃO E MANUTENÇÃO', 'tipo': 'DESPESA', 'natureza': 'SINTETICA', 'grupo': 'D'},
            {'codigo': '4.2.001', 'descricao': 'ALUGUEL E CONDOMÍNIO', 'tipo': 'DESPESA', 'natureza': 'ANALITICA', 'grupo': 'D'},
            {'codigo': '4.2.002', 'descricao': 'ENERGIA / ÁGUA / INTERNET', 'tipo': 'DESPESA', 'natureza': 'ANALITICA', 'grupo': 'D'},
            {'codigo': '4.2.003', 'descricao': 'MANUTENÇÃO E REPAROS', 'tipo': 'DESPESA', 'natureza': 'ANALITICA', 'grupo': 'D'},

            {'codigo': '4.3', 'descricao': 'ADMINISTRATIVAS E TI', 'tipo': 'DESPESA', 'natureza': 'SINTETICA', 'grupo': 'D'},
            {'codigo': '4.3.001', 'descricao': 'SOFTWARE E CLOUD (SaaS)', 'tipo': 'DESPESA', 'natureza': 'ANALITICA', 'grupo': 'D'},
            {'codigo': '4.3.002', 'descricao': 'CONTABILIDADE E JURÍDICO', 'tipo': 'DESPESA', 'natureza': 'ANALITICA', 'grupo': 'D'},
            {'codigo': '4.3.003', 'descricao': 'TARIFAS BANCÁRIAS', 'tipo': 'DESPESA', 'natureza': 'ANALITICA', 'grupo': 'D'},
            
            {'codigo': '4.4', 'descricao': 'MARKETING E COMERCIAL', 'tipo': 'DESPESA', 'natureza': 'ANALITICA', 'grupo': 'D'},
            
            {'codigo': '4.5', 'descricao': 'DEPRECIAÇÃO E AMORTIZAÇÃO', 'tipo': 'DESPESA', 'natureza': 'ANALITICA', 'grupo': 'D'},

            # 5. INVESTIMENTOS E RESULTADO NÃO OPERACIONAL
            {'codigo': '5', 'descricao': 'INVESTIMENTOS E NÃO OPERACIONAIS', 'tipo': 'DESPESA', 'natureza': 'SINTETICA', 'grupo': 'D'},
            {'codigo': '5.1', 'descricao': 'AQUISIÇÃO DE MÁQUINAS/EQUIPAMENTOS', 'tipo': 'DESPESA', 'natureza': 'ANALITICA', 'grupo': 'D'},
            {'codigo': '5.2', 'descricao': 'REFORMA E BENFEITORIAS', 'tipo': 'DESPESA', 'natureza': 'ANALITICA', 'grupo': 'D'},
            {'codigo': '5.3', 'descricao': 'AMORTIZAÇÃO DE EMPRÉSTIMOS', 'tipo': 'DESPESA', 'natureza': 'ANALITICA', 'grupo': 'D'},
            {'codigo': '5.4', 'descricao': 'DISTRIBUIÇÃO DE LUCROS', 'tipo': 'DESPESA', 'natureza': 'ANALITICA', 'grupo': 'D'},
        ]
        
        for item in seed:
            if not PlanoContas.query.filter_by(empresa_id=e_id, codigo=item['codigo']).first():
                nova = PlanoContas(
                    empresa_id=e_id,
                    codigo=item['codigo'],
                    descricao=item['descricao'],
                    tipo=item['tipo'],
                    natureza=item['natureza'],
                    grupo_gerencial=item['grupo'],
                    vida_util_meses=item.get('vida', 0)
                )
                db.session.add(nova)
        
        db.session.commit()
        return {"success": True, "message": "Estrutura do Plano de Contas gerada com sucesso!"}
    except Exception as e:
        db.session.rollback()
        return {"success": False, "error": str(e)}, 500

# ── Gestão de Patrimônio ──────────────────────────────────────────────────
@financeiro_bp.route('/card/patrimonio')
@login_required
def card_patrimonio():
    from app.models.gestao.patrimonio import Patrimonio
    from app.models.gestao.plano_contas import PlanoContas
    
    # 🛡️ Auto-Migração Inteligente de Colunas (Para evitar Crash)
    try:
        with db.engine.begin() as conn:
            from sqlalchemy import text
            res = conn.execute(text("PRAGMA table_info(financeiro_patrimonio)"))
            cols = [r[1] for r in res]
            if 'categoria' not in cols:
                conn.execute(text("ALTER TABLE financeiro_patrimonio ADD COLUMN categoria VARCHAR(50) DEFAULT 'OUTROS'"))
            if 'detalhes' not in cols:
                conn.execute(text("ALTER TABLE financeiro_patrimonio ADD COLUMN detalhes TEXT"))
        db.create_all()
    except Exception:
        pass

    e_id = session.get('empresa_id')
    bens = Patrimonio.query.filter_by(empresa_id=e_id).all()
    contas_imobilizado = PlanoContas.query.filter(PlanoContas.empresa_id == e_id, PlanoContas.codigo.like('1.4%')).all()
    return render_template('financeiro/cards/form_financeiro_patrimonio.html', bens=bens, contas=contas_imobilizado)

@financeiro_bp.route('/api/patrimonio/processar-depreciacao', methods=['POST'])
@login_required
def api_depreciacao():
    from app.services.financeiro import FinanceiroService
    e_id = session.get('empresa_id')
    u_id = session.get('user_id')
    
    # Pega mês/ano do request ou usa atual
    import datetime
    hoje = datetime.datetime.now()
    mes = request.json.get('mes', hoje.month)
    ano = request.json.get('ano', hoje.year)
    
    result = FinanceiroService.processar_depreciacao_mensal(e_id, mes, ano, u_id)
    return result

@financeiro_bp.route('/card/plano-contas/sync')
@login_required
def sync_db_manual():
    from sqlalchemy import text
    cols_pc = [('grupo_gerencial', 'VARCHAR(1)'), ('vida_util_meses', 'INTEGER DEFAULT 0'), ('valor_residual_percent', 'FLOAT DEFAULT 0.0')]
    for col, tipo in cols_pc:
        try:
            db.session.execute(text(f"ALTER TABLE financeiro_plano_contas ADD COLUMN {col} {tipo}"))
            db.session.commit()
        except: db.session.rollback()
    db.create_all()
    return {"success": True}

# ── Contas a Pagar / A Receber (Quiet Luxury Standard) ────────────────────
@financeiro_bp.route('/card/contas')
@login_required
def card_contas():
    from app.models.gestao.lancamento import Lancamento
    from app.models.gestao.plano_contas import PlanoContas
    from app.models.gestao.centro_custo import CentroCusto
    from app.models.comercial.models import FormaPagamento
    from app.models.cadastros.cliente import Cliente
    from app.models.cadastros.fornecedor import Fornecedor
    import datetime

    e_id = session.get('empresa_id')
    tipo = request.args.get('tipo', 'RECEITA').upper() # RECEITA ou DESPESA
    
    # 🛡️ Auto-Migração Inteligente de Colunas e Tabelas
    try:
        with db.engine.begin() as conn:
            from sqlalchemy import text
            res = conn.execute(text("PRAGMA table_info(financeiro_lancamentos)"))
            cols = [r[1] for r in res]
            if 'numero_documento' not in cols:
                conn.execute(text("ALTER TABLE financeiro_lancamentos ADD COLUMN numero_documento VARCHAR(50)"))
            if 'data_lancamento' not in cols:
                conn.execute(text("ALTER TABLE financeiro_lancamentos ADD COLUMN data_lancamento DATETIME"))
            if 'rateio_multiplo' not in cols:
                conn.execute(text("ALTER TABLE financeiro_lancamentos ADD COLUMN rateio_multiplo BOOLEAN DEFAULT 0"))
            if 'conta_bancaria_id' not in cols:
                conn.execute(text("ALTER TABLE financeiro_lancamentos ADD COLUMN conta_bancaria_id INTEGER"))
            if 'caixa_id' not in cols:
                conn.execute(text("ALTER TABLE financeiro_lancamentos ADD COLUMN caixa_id INTEGER"))
        db.create_all()
    except Exception:
        pass

    # 📋 Títulos da Empresa
    lancamentos = Lancamento.query.filter_by(empresa_id=e_id, tipo=tipo).order_by(Lancamento.data_vencimento.desc()).all()
    
    # 📋 Registro Ativo (se for edição)
    target_id = request.args.get('id', type=int)
    lancamento = Lancamento.query.get(target_id) if target_id else None

    # 📋 Listas Auxiliares (Apenas Contas Analíticas para Rateio)
    plano_contas = PlanoContas.query.filter_by(empresa_id=e_id, ativo=True, natureza='ANALITICA').order_by(PlanoContas.codigo).all()
    centros_custo_raw = CentroCusto.query.filter_by(empresa_id=e_id, ativo=True).order_by(CentroCusto.codigo).all()
    pai_ids = {cc.pai_id for cc in centros_custo_raw if cc.pai_id is not None}
    centros_custo = [cc for cc in centros_custo_raw if cc.id not in pai_ids]
    formas_pagamento = FormaPagamento.query.filter_by(ativa=True).order_by(FormaPagamento.nome).all()
    
    from app.models.gestao.caixa import Caixa
    caixas = Caixa.query.filter_by(empresa_id=e_id, status='ABERTO').order_by(Caixa.nome).all()
    
    # Pessoas (Clientes para Receita, Fornecedores para Despesa)
    if tipo == 'RECEITA':
        clientes_raw = Cliente.query.filter_by(ativo=True).order_by(Cliente.nome).all()
        pessoas = [{'id': c.id, 'nome': c.nome} for c in clientes_raw]
    else:
        fornecedores_raw = Fornecedor.query.filter_by(ativo=True).order_by(Fornecedor.razao_social).all()
        pessoas = [{'id': f.id, 'nome': f.razao_social} for f in fornecedores_raw]

    today = datetime.datetime.now().strftime('%Y-%m-%d')
    is_modal = request.args.get('modal', '0') == '1'

    return render_template('financeiro/cards/form_financeiro_contas.html',
                           lancamentos=lancamentos,
                           lancamento=lancamento,
                           tipo=tipo,
                           plano_contas=plano_contas,
                           centros_custo=centros_custo,
                           formas_pagamento=formas_pagamento,
                           caixas=caixas,
                           pessoas=pessoas,
                           today=today,
                           is_modal=is_modal)

@financeiro_bp.route('/card/contas/salvar', methods=['POST'])
@login_required
def salvar_conta():
    from app.models.gestao.lancamento import Lancamento
    from app.utils.helpers import parse_money
    import datetime

    try:
        e_id = session.get('empresa_id')
        u_id = session.get('user_id')
        lid = request.form.get('id')
        
        if lid:
            lanc = Lancamento.query.get(lid)
        else:
            lanc = Lancamento(empresa_id=e_id, usuario_id=u_id)
        
        lanc.tipo = request.form.get('tipo', 'DESPESA').upper()
        lanc.descricao = request.form.get('descricao', '').upper()
        lanc.valor = parse_money(request.form.get('valor') or '0')
        
        # Datas e Documentação
        venc_str = request.form.get('data_vencimento')
        if venc_str:
            lanc.data_vencimento = datetime.datetime.strptime(venc_str, '%Y-%m-%d')
        
        comp_str = request.form.get('data_competencia')
        if comp_str:
            lanc.data_competencia = datetime.datetime.strptime(comp_str, '%Y-%m-%d')
        else:
            lanc.data_competencia = lanc.data_vencimento

        lanc.numero_documento = request.form.get('numero_documento', '').upper()
        
        lanc_str = request.form.get('data_lancamento')
        if lanc_str:
            lanc.data_lancamento = datetime.datetime.strptime(lanc_str, '%Y-%m-%d')
        else:
            lanc.data_lancamento = datetime.datetime.now()

        # Classificação & Rateio (Único vs. Múltiplo)
        lanc.rateio_multiplo = request.form.get('rateio_multiplo') == '1'
        
        if not lanc.rateio_multiplo:
            # Rateio Único (100% do valor)
            pc_id = request.form.get('plano_contas_id')
            lanc.plano_contas_id = int(pc_id) if pc_id and pc_id.isdigit() else None
            
            cc_id = request.form.get('centro_custo_id')
            lanc.centro_custo_id = int(cc_id) if cc_id and cc_id.isdigit() else None
            
            # Limpa rateios múltiplos anteriores, se houver
            if lanc.rateios:
                for r in lanc.rateios:
                    db.session.delete(r)
        else:
            # Rateio Múltiplo (+ de Um)
            import json
            from app.models.gestao.lancamento import RateioLancamento
            
            pc_id = request.form.get('plano_contas_id')
            lanc.plano_contas_id = int(pc_id) if pc_id and pc_id.isdigit() else None
            cc_id = request.form.get('centro_custo_id')
            lanc.centro_custo_id = int(cc_id) if cc_id and cc_id.isdigit() else None
            
            db.session.add(lanc)
            db.session.flush() # Garante que lanc.id existe para vincular os rateios
            
            if lanc.rateios:
                for r in lanc.rateios:
                    db.session.delete(r)
            
            rateios_json = request.form.get('rateios_multiplos')
            if rateios_json:
                try:
                    itens_rateio = json.loads(rateios_json)
                    for item in itens_rateio:
                        r_pc = item.get('plano_contas_id')
                        r_cc = item.get('centro_custo_id')
                        r_val = parse_money(str(item.get('valor', 0)))
                        if r_pc and r_val > 0:
                            novo_r = RateioLancamento(
                                lancamento_id=lanc.id,
                                plano_contas_id=int(r_pc),
                                centro_custo_id=int(r_cc) if r_cc else None,
                                valor=r_val
                            )
                            db.session.add(novo_r)
                except Exception as e:
                    return {"success": False, "error": f"Erro ao processar rateio múltiplo: {str(e)}"}, 400

        fp_id = request.form.get('forma_pagamento_id')
        lanc.forma_pagamento_id = int(fp_id) if fp_id and fp_id.isdigit() else None

        lanc.status = request.form.get('status', 'PENDENTE').upper()
        lanc.observacoes = request.form.get('observacoes')
        
        db.session.add(lanc)
        db.session.commit()
        return {"success": True, "message": f"Título {'a Receber' if lanc.tipo == 'RECEITA' else 'a Pagar'} salvo com sucesso!"}
    except Exception as e:
        db.session.rollback()
        return {"success": False, "error": str(e)}, 500

@financeiro_bp.route('/card/contas/excluir/<int:id>', methods=['POST'])
@login_required
def excluir_conta(id):
    from app.models.gestao.lancamento import Lancamento
    try:
        lanc = Lancamento.query.get_or_404(id)
        db.session.delete(lanc)
        db.session.commit()
        return {"success": True, "message": "Título excluído com sucesso!"}
    except Exception as e:
        db.session.rollback()
        return {"success": False, "error": str(e)}, 500

@financeiro_bp.route('/card/contas/baixar/<int:id>', methods=['POST'])
@login_required
def baixar_conta(id):
    from app.models.gestao.lancamento import Lancamento
    from app.models.gestao.lancamento import RateioLancamento
    from app.utils.helpers import parse_money
    import datetime

    try:
        lanc = Lancamento.query.get_or_404(id)
        
        pag_str = request.form.get('data_pagamento')
        if pag_str:
            lanc.data_pagamento = datetime.datetime.strptime(pag_str, '%Y-%m-%d')
        else:
            lanc.data_pagamento = datetime.datetime.now()
            
        fp_id = request.form.get('forma_pagamento_id')
        if fp_id and fp_id.isdigit():
            lanc.forma_pagamento_id = int(fp_id)
            
        conta_bancaria_id = request.form.get('conta_bancaria_id')
        if conta_bancaria_id and conta_bancaria_id.isdigit():
            lanc.conta_bancaria_id = int(conta_bancaria_id)
            
        caixa_id = request.form.get('caixa_id')
        if caixa_id and caixa_id.isdigit():
            lanc.caixa_id = int(caixa_id)
            
        val_pago = parse_money(request.form.get('valor_pago') or str(lanc.valor))
        
        # Verifica se é baixa parcial
        valor_original = lanc.valor
        if val_pago < valor_original:
            # Cria título residual com o valor restante
            valor_residual = valor_original - val_pago
            
            # Atualiza o título original com o valor pago
            lanc.valor = val_pago
            lanc.status = 'PAGO'
            
            # Cria novo título residual
            lanc_residual = Lancamento(
                empresa_id=lanc.empresa_id,
                tipo=lanc.tipo,
                descricao=f"{lanc.descricao} (RESTANTE)",
                numero_documento=lanc.numero_documento,
                data_lancamento=lanc.data_lancamento,
                data_vencimento=lanc.data_vencimento,
                valor=valor_residual,
                plano_contas_id=lanc.plano_contas_id,
                centro_custo_id=lanc.centro_custo_id,
                forma_pagamento_id=lanc.forma_pagamento_id,
                status='PENDENTE',
                rateio_multiplo=lanc.rateio_multiplo,
                observacoes=f"Baixa parcial do título #{lanc.id}. Valor original: R$ {valor_original:.2f}, Valor pago: R$ {val_pago:.2f}"
            )
            db.session.add(lanc_residual)
            
            # Se houver rateio múltiplo, copia para o título residual
            if lanc.rateio_multiplo and lanc.rateios:
                for rateio in lanc.rateios:
                    # Calcula o valor proporcional do rateio residual
                    proporcao = valor_residual / valor_original
                    valor_rateio_residual = rateio.valor * proporcao
                    
                    # Atualiza o valor do rateio original proporcionalmente
                    rateio.valor = rateio.valor - valor_rateio_residual
                    
                    # Cria novo rateio para o título residual
                    rateio_residual = RateioLancamento(
                        lancamento_id=lanc_residual.id,
                        plano_contas_id=rateio.plano_contas_id,
                        centro_custo_id=rateio.centro_custo_id,
                        valor=valor_rateio_residual
                    )
                    db.session.add(rateio_residual)
        else:
            # Baixa total
            lanc.status = 'PAGO'
        
        # Opcional: Se for caixa_id, já gera a movimentação de Caixa vinculada!
        if lanc.caixa_id:
            from app.models.gestao.caixa import MovimentacaoCaixa
            cat_mov = "RECEBIMENTO" if lanc.tipo == 'RECEITA' else "PAGAMENTO"
            nova_movimentacao = MovimentacaoCaixa(
                caixa_id=lanc.caixa_id,
                tipo="ENTRADA" if lanc.tipo == 'RECEITA' else "SAIDA",
                categoria=cat_mov,
                descricao=f"Baixa do Título: {lanc.descricao}",
                valor=val_pago,
                data_movimentacao=lanc.data_pagamento,
                plano_contas_id=lanc.plano_contas_id,
                centro_custo_id=lanc.centro_custo_id,
                forma_pagamento_id=lanc.forma_pagamento_id,
                lancamento_id=lanc.id
            )
            db.session.add(nova_movimentacao)
        
        db.session.commit()
        
        if val_pago < valor_original:
            return {"success": True, "message": f"Baixa parcial realizada! Título residual de R$ {valor_residual:.2f} criado."}
        else:
            return {"success": True, "message": "Título baixado/pago com sucesso!"}
    except Exception as e:
        db.session.rollback()
        return {"success": False, "error": str(e)}, 500


# =============================================================================
# 🔹 ABA CAIXAS E MOVIMENTAÇÕES DE PDV
# =============================================================================

@financeiro_bp.route('/card/caixas', methods=['GET'])
@login_required
def card_caixas():
    from app.models.gestao.caixa import Caixa, MovimentacaoCaixa
    from app.models.gestao.plano_contas import PlanoContas
    from app.models.gestao.centro_custo import CentroCusto
    from app.models.comercial.models import FormaPagamento
    from app.models.sistema.parametro import ParametroSistema
    import datetime

    # 🛡️ Garantir que as tabelas existem no SQLite automaticamente
    try:
        db.create_all()
    except Exception:
        pass

    empresa_id = session.get('empresa_id')
    
    q_caixas = Caixa.query
    if empresa_id:
        q_caixas = q_caixas.filter_by(empresa_id=empresa_id)
    caixas = q_caixas.order_by(Caixa.nome).all()
    
    # Carregar movimentações para cada caixa
    for caixa in caixas:
        caixa.movimentacoes = MovimentacaoCaixa.query.filter_by(caixa_id=caixa.id).order_by(MovimentacaoCaixa.data_movimentacao).all()

    # Buscar listas auxiliares para o modal de movimentação
    q_pc = PlanoContas.query
    if empresa_id: q_pc = q_pc.filter_by(empresa_id=empresa_id)
    planos_conta = q_pc.order_by(PlanoContas.codigo).all()

    q_cc = CentroCusto.query
    if empresa_id: q_cc = q_cc.filter_by(empresa_id=empresa_id)
    centros_custo = q_cc.order_by(CentroCusto.codigo).all()

    formas_pagamento = FormaPagamento.query.order_by(FormaPagamento.nome).all()

    today = datetime.datetime.now().strftime('%Y-%m-%d')
    is_modal = request.args.get('modal', '0') == '1'

    return render_template('financeiro/cards/form_financeiro_caixas.html',
                           caixas=caixas,
                           planos_conta=planos_conta,
                           centros_custo=centros_custo,
                           formas_pagamento=formas_pagamento,
                           today=today,
                           parametro_sistema=ParametroSistema,
                           is_modal=is_modal)


@financeiro_bp.route('/card/caixas/salvar', methods=['POST'])
@login_required
def salvar_caixa():
    from app.models.gestao.caixa import Caixa
    from app.utils.helpers import parse_money
    import datetime

    try:
        caixa_id = request.form.get('caixa_id')
        nome = request.form.get('nome', '').strip()
        responsavel = request.form.get('responsavel', '').strip()
        saldo_inicial = parse_money(request.form.get('saldo_inicial') or '0')
        status = request.form.get('status', 'ABERTO').upper()
        observacoes = request.form.get('observacoes', '').strip()

        if not nome:
            return {"success": False, "error": "O nome do caixa é obrigatório."}, 400

        if caixa_id and caixa_id.isdigit():
            c = Caixa.query.get_or_404(int(caixa_id))
            c.nome = nome
            c.responsavel = responsavel
            c.status = status
            c.observacoes = observacoes
            if status == 'FECHADO' and not c.data_fechamento:
                c.data_fechamento = datetime.datetime.utcnow()
            elif status == 'ABERTO':
                c.data_fechamento = None
            msg = "Caixa atualizado com sucesso!"
        else:
            c = Caixa(
                empresa_id=session.get('empresa_id'),
                nome=nome,
                responsavel=responsavel,
                saldo_inicial=saldo_inicial,
                saldo_atual=saldo_inicial,
                status=status,
                observacoes=observacoes
            )
            db.session.add(c)
            msg = "Caixa aberto com sucesso!"

        db.session.commit()
        return {"success": True, "message": msg, "id": c.id}
    except Exception as e:
        db.session.rollback()
        return {"success": False, "error": str(e)}, 500


@financeiro_bp.route('/card/caixas/excluir/<int:id>', methods=['POST'])
@login_required
def excluir_caixa(id):
    from app.models.gestao.caixa import Caixa
    try:
        c = Caixa.query.get_or_404(id)
        db.session.delete(c)
        db.session.commit()
        return {"success": True, "message": "Caixa excluído com sucesso!"}
    except Exception as e:
        db.session.rollback()
        return {"success": False, "error": str(e)}, 500


@financeiro_bp.route('/card/caixas/movimentar/<int:id>', methods=['POST'])
@login_required
def movimentar_caixa(id):
    from app.models.gestao.caixa import Caixa, MovimentacaoCaixa
    from app.utils.helpers import parse_money

    try:
        c = Caixa.query.get_or_404(id)
        
        if c.status == 'FECHADO':
            return {"success": False, "error": "Não é possível movimentar um caixa fechado."}, 400

        tipo = request.form.get('tipo', '').upper()
        categoria = request.form.get('categoria', '').upper()
        descricao = request.form.get('descricao', '').strip()
        valor = parse_money(request.form.get('valor') or '0')
        observacoes = request.form.get('observacoes', '').strip()

        if not tipo or not categoria or not descricao or valor <= 0:
            return {"success": False, "error": "Preencha todos os campos obrigatórios com um valor maior que zero."}, 400

        pc_id = request.form.get('plano_contas_id')
        cc_id = request.form.get('centro_custo_id')
        fp_id = request.form.get('forma_pagamento_id')

        mov = MovimentacaoCaixa(
            caixa_id=c.id,
            tipo=tipo,
            categoria=categoria,
            descricao=descricao,
            valor=valor,
            plano_contas_id=int(pc_id) if pc_id and pc_id.isdigit() else None,
            centro_custo_id=int(cc_id) if cc_id and cc_id.isdigit() else None,
            forma_pagamento_id=int(fp_id) if fp_id and fp_id.isdigit() else None,
            observacoes=observacoes
        )
        db.session.add(mov)

        # Atualiza o saldo atual do caixa
        if tipo == 'ENTRADA':
            c.saldo_atual = float(c.saldo_atual or 0) + float(valor)
        elif tipo == 'SAIDA':
            c.saldo_atual = float(c.saldo_atual or 0) - float(valor)

        db.session.commit()
        return {"success": True, "message": f"Movimentação de {categoria} registrada com sucesso!", "saldo_atual": c.saldo_atual}
    except Exception as e:
        db.session.rollback()
        return {"success": False, "error": str(e)}, 500


# =============================================================================
# 🔹 ABA FLUXO, PROJEÇÕES E MOVIMENTAÇÕES (FASE 2.5)
# =============================================================================

@financeiro_bp.route('/card/fluxo-caixa')
@login_required
def card_fluxo_caixa():
    from app.models.gestao.lancamento import Lancamento
    import datetime

    e_id = session.get('empresa_id')
    hoje = datetime.date.today()
    ano_atual = hoje.year
    mes_atual = hoje.month

    lancamentos = Lancamento.query.filter_by(empresa_id=e_id).all()

    # Agregação Mensal (Mês Atual)
    receitas_mes = sum(float(l.valor or 0) for l in lancamentos if l.tipo == 'RECEITA' and l.status == 'PAGO' and (l.data_pagamento or l.data_vencimento) and (l.data_pagamento or l.data_vencimento).year == ano_atual and (l.data_pagamento or l.data_vencimento).month == mes_atual)
    despesas_mes = sum(float(l.valor or 0) for l in lancamentos if l.tipo == 'DESPESA' and l.status == 'PAGO' and (l.data_pagamento or l.data_vencimento) and (l.data_pagamento or l.data_vencimento).year == ano_atual and (l.data_pagamento or l.data_vencimento).month == mes_atual)
    saldo_mes = receitas_mes - despesas_mes

    # Agregação Anual para Gráfico
    grafico_meses = ['Jan','Fev','Mar','Abr','Mai','Jun','Jul','Ago','Set','Out','Nov','Dez']
    grafico_receitas = [0.0] * 12
    grafico_despesas = [0.0] * 12

    for l in lancamentos:
        if l.status != 'CANCELADO':
            dt = l.data_pagamento if l.status == 'PAGO' else l.data_vencimento
            if dt and dt.year == ano_atual:
                m_idx = dt.month - 1
                v = float(l.valor or 0)
                if l.tipo == 'RECEITA': grafico_receitas[m_idx] += v
                elif l.tipo == 'DESPESA': grafico_despesas[m_idx] += v

    is_modal = request.args.get('modal', '0') == '1'

    return render_template('financeiro/cards/form_financeiro_fluxo_caixa.html',
                           receitas_mes=receitas_mes,
                           despesas_mes=despesas_mes,
                           saldo_mes=saldo_mes,
                           grafico_meses=grafico_meses,
                           grafico_receitas=grafico_receitas,
                           grafico_despesas=grafico_despesas,
                           is_modal=is_modal)

@financeiro_bp.route('/card/projecao')
@login_required
def card_projecao():
    from app.models.gestao.lancamento import Lancamento
    import datetime

    e_id = session.get('empresa_id')
    hoje = datetime.date.today()

    # Query robusta: inclui lançamentos da empresa OU sem empresa_id cadastrado
    q = Lancamento.query.filter(
        Lancamento.status.notin_(['PAGO', 'CANCELADO'])
    )
    if e_id:
        from sqlalchemy import or_
        q = q.filter(or_(Lancamento.empresa_id == e_id, Lancamento.empresa_id == None))

    pendentes = q.all()

    proj_30 = {'receitas': 0.0, 'despesas': 0.0, 'saldo': 0.0, 'titulos': []}
    proj_60 = {'receitas': 0.0, 'despesas': 0.0, 'saldo': 0.0, 'titulos': []}
    proj_90 = {'receitas': 0.0, 'despesas': 0.0, 'saldo': 0.0, 'titulos': []}

    for l in pendentes:
        dt = l.data_vencimento
        if dt:
            dt_val = dt.date() if isinstance(dt, datetime.datetime) else dt
            dias = (dt_val - hoje).days
            v = float(l.valor or 0)

            # Inclui vencidos (dias < 0) na janela de 30 dias (já vencidos são urgentes)
            if dias <= 30:
                if l.tipo == 'RECEITA': proj_30['receitas'] += v
                else: proj_30['despesas'] += v
                proj_30['titulos'].append(l)
            elif 31 <= dias <= 60:
                if l.tipo == 'RECEITA': proj_60['receitas'] += v
                else: proj_60['despesas'] += v
                proj_60['titulos'].append(l)
            elif 61 <= dias <= 90:
                if l.tipo == 'RECEITA': proj_90['receitas'] += v
                else: proj_90['despesas'] += v
                proj_90['titulos'].append(l)

    proj_30['saldo'] = proj_30['receitas'] - proj_30['despesas']
    proj_60['saldo'] = proj_60['receitas'] - proj_60['despesas']
    proj_90['saldo'] = proj_90['receitas'] - proj_90['despesas']

    is_modal = request.args.get('modal', '0') == '1'

    return render_template('financeiro/cards/form_financeiro_projecao.html',
                           proj_30=proj_30, proj_60=proj_60, proj_90=proj_90, is_modal=is_modal)

@financeiro_bp.route('/card/movimentacoes')
@login_required
def card_movimentacoes():
    from app.models.gestao.lancamento import Lancamento
    from app.models.gestao.caixa import MovimentacaoCaixa, Caixa
    import datetime

    e_id = session.get('empresa_id')
    
    # Query dos caixas cadastrados
    q_caixas = Caixa.query
    if e_id:
        q_caixas = q_caixas.filter_by(empresa_id=e_id)
    caixas = q_caixas.order_by(Caixa.nome).all()
    
    # Extrato unificando títulos pagos e movimentações de caixa
    titulos_pagos = Lancamento.query.filter_by(empresa_id=e_id, status='PAGO').order_by(Lancamento.data_pagamento.desc()).limit(50).all()
    movs_caixa = MovimentacaoCaixa.query.order_by(MovimentacaoCaixa.data_movimentacao.desc()).limit(50).all()

    # Padroniza lista mestre
    extrato = []
    for t in titulos_pagos:
        extrato.append({
            'origem': 'TÍTULO',
            'id': t.id,
            'caixa_id': '',
            'data': t.data_pagamento.strftime('%d/%m/%Y %H:%M') if t.data_pagamento else '',
            'tipo': t.tipo,
            'descricao': t.descricao,
            'valor': float(t.valor or 0),
            'conta': t.plano_contas.descricao if t.plano_contas else 'NÃO CLASSIFICADO',
            'forma': t.forma_pagamento.nome if t.forma_pagamento else 'OUTROS'
        })
    for m in movs_caixa:
        extrato.append({
            'origem': f'CAIXA PDV (#{m.caixa_id})',
            'id': m.id,
            'caixa_id': str(m.caixa_id) if m.caixa_id else '',
            'data': m.data_movimentacao.strftime('%d/%m/%Y %H:%M') if m.data_movimentacao else '',
            'tipo': m.tipo,
            'descricao': m.descricao,
            'valor': float(m.valor or 0),
            'conta': m.plano_contas.descricao if m.plano_contas else m.categoria,
            'forma': m.forma_pagamento.nome if m.forma_pagamento else 'DINHEIRO'
        })

    # Ordena por data decrescente
    extrato.sort(key=lambda x: x['data'], reverse=True)
    is_modal = request.args.get('modal', '0') == '1'

    return render_template('financeiro/cards/form_financeiro_movimentacoes.html', extrato=extrato, caixas=caixas, is_modal=is_modal)

@financeiro_bp.route('/card/entradas-saidas')
@login_required
def card_entradas_saidas():
    from app.models.gestao.plano_contas import PlanoContas
    from app.models.gestao.centro_custo import CentroCusto
    from app.models.comercial.models import FormaPagamento
    import datetime

    e_id = session.get('empresa_id')
    plano_contas = PlanoContas.query.filter_by(empresa_id=e_id, ativo=True, natureza='ANALITICA').order_by(PlanoContas.codigo).all()
    centros_custo_raw = CentroCusto.query.filter_by(empresa_id=e_id, ativo=True).order_by(CentroCusto.codigo).all()
    pai_ids = {cc.pai_id for cc in centros_custo_raw if cc.pai_id is not None}
    centros_custo = [cc for cc in centros_custo_raw if cc.id not in pai_ids]
    formas_pagamento = FormaPagamento.query.filter_by(ativa=True).order_by(FormaPagamento.nome).all()
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    is_modal = request.args.get('modal', '0') == '1'

    return render_template('financeiro/cards/form_financeiro_entradas_saidas.html',
                           plano_contas=plano_contas,
                           centros_custo=centros_custo,
                           formas_pagamento=formas_pagamento,
                           today=today,
                           is_modal=is_modal)

@financeiro_bp.route('/card/entradas-saidas/salvar', methods=['POST'])
@login_required
def salvar_entrada_saida():
    from app.models.gestao.lancamento import Lancamento
    from app.utils.helpers import parse_money
    import datetime

    try:
        e_id = session.get('empresa_id')
        u_id = session.get('user_id')

        lanc = Lancamento(empresa_id=e_id, usuario_id=u_id)
        lanc.tipo = request.form.get('tipo', 'RECEITA').upper()
        lanc.descricao = request.form.get('descricao', '').upper()
        lanc.valor = parse_money(request.form.get('valor') or '0')
        lanc.status = 'PAGO' # Lançamento direto já entra como pago no fluxo

        dt_str = request.form.get('data_pagamento')
        if dt_str:
            dt_obj = datetime.datetime.strptime(dt_str, '%Y-%m-%d')
            lanc.data_pagamento = dt_obj
            lanc.data_vencimento = dt_obj
            lanc.data_competencia = dt_obj
            lanc.data_lancamento = dt_obj
        else:
            agora = datetime.datetime.now()
            lanc.data_pagamento = agora
            lanc.data_vencimento = agora
            lanc.data_competencia = agora
            lanc.data_lancamento = agora

        pc_id = request.form.get('plano_contas_id')
        lanc.plano_contas_id = int(pc_id) if pc_id and pc_id.isdigit() else None

        cc_id = request.form.get('centro_custo_id')
        lanc.centro_custo_id = int(cc_id) if cc_id and cc_id.isdigit() else None

        fp_id = request.form.get('forma_pagamento_id')
        lanc.forma_pagamento_id = int(fp_id) if fp_id and fp_id.isdigit() else None

        lanc.observacoes = request.form.get('observacoes', 'Lançamento Rápido Direto')

        db.session.add(lanc)
        db.session.commit()
        return {"success": True, "message": f"Movimentação direta de {lanc.tipo} registrada com sucesso!"}
    except Exception as e:
        db.session.rollback()
        return {"success": False, "error": str(e)}, 500

@financeiro_bp.route('/card/bancos')
@login_required
def card_bancos():
    is_modal = request.args.get('modal', '0') == '1'
    return render_template('financeiro/cards/form_financeiro_bancos.html', is_modal=is_modal)

@financeiro_bp.route('/card/contas-bancarias')
@login_required
def card_contas_bancarias():
    is_modal = request.args.get('modal', '0') == '1'
    return render_template('financeiro/cards/form_financeiro_contas_bancarias.html', is_modal=is_modal)

@financeiro_bp.route('/card/extratos')
@login_required
def card_extratos():
    is_modal = request.args.get('modal', '0') == '1'
    return render_template('financeiro/cards/form_financeiro_extratos.html', is_modal=is_modal)

@financeiro_bp.route('/card/fluxo-caixa-graficos')
@login_required
def card_fluxo_caixa_graficos():
    """Exibe gráficos de evolução do fluxo de caixa com diferentes granularidades."""
    from app.models.gestao.lancamento import Lancamento
    from sqlalchemy import func, extract
    from datetime import datetime, timedelta
    import calendar
    
    empresa_id = session.get('empresa_id')
    
    # Dados para gráfico anual (por mês)
    dados_anual = db.session.query(
        extract('month', Lancamento.data_pagamento).label('mes'),
        func.sum(
            case([(Lancamento.tipo == 'RECEITA', Lancamento.valor)], else_=0)
        ).label('receitas'),
        func.sum(
            case([(Lancamento.tipo == 'DESPESA', Lancamento.valor)], else_=0)
        ).label('despesas')
    ).filter(
        Lancamento.empresa_id == empresa_id,
        Lancamento.status == 'PAGO',
        Lancamento.data_pagamento.isnot(None)
    ).group_by(
        extract('month', Lancamento.data_pagamento)
    ).order_by(
        extract('month', Lancamento.data_pagamento)
    ).all()
    
    # Prepara dados do gráfico anual
    meses_nomes = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
    receitas_anual = [0] * 12
    despesas_anual = [0] * 12
    
    for mes, receita, despesa in dados_anual:
        idx = int(mes) - 1
        if 0 <= idx < 12:
            receitas_anual[idx] = float(receita or 0)
            despesas_anual[idx] = float(despesa or 0)
    
    # Dados para gráfico mensal (por dia do mês - mês atual)
    hoje = datetime.now()
    dados_mensal = db.session.query(
        extract('day', Lancamento.data_pagamento).label('dia'),
        func.sum(
            case([(Lancamento.tipo == 'RECEITA', Lancamento.valor)], else_=0)
        ).label('receitas'),
        func.sum(
            case([(Lancamento.tipo == 'DESPESA', Lancamento.valor)], else_=0)
        ).label('despesas')
    ).filter(
        Lancamento.empresa_id == empresa_id,
        Lancamento.status == 'PAGO',
        Lancamento.data_pagamento.isnot(None),
        extract('year', Lancamento.data_pagamento) == hoje.year,
        extract('month', Lancamento.data_pagamento) == hoje.month
    ).group_by(
        extract('day', Lancamento.data_pagamento)
    ).order_by(
        extract('day', Lancamento.data_pagamento)
    ).all()
    
    # Prepara dados do gráfico mensal
    dias_mes = calendar.monthrange(hoje.year, hoje.month)[1]
    dias_nomes = list(range(1, dias_mes + 1))
    receitas_mensal = [0] * dias_mes
    despesas_mensal = [0] * dias_mes
    
    for dia, receita, despesa in dados_mensal:
        idx = int(dia) - 1
        if 0 <= idx < dias_mes:
            receitas_mensal[idx] = float(receita or 0)
            despesas_mensal[idx] = float(despesa or 0)
    
    # Dados para gráfico semanal (por dia da semana - últimos 7 dias)
    dados_semanal = db.session.query(
        Lancamento.data_pagamento.label('data'),
        func.sum(
            case([(Lancamento.tipo == 'RECEITA', Lancamento.valor)], else_=0)
        ).label('receitas'),
        func.sum(
            case([(Lancamento.tipo == 'DESPESA', Lancamento.valor)], else_=0)
        ).label('despesas')
    ).filter(
        Lancamento.empresa_id == empresa_id,
        Lancamento.status == 'PAGO',
        Lancamento.data_pagamento.isnot(None),
        Lancamento.data_pagamento >= hoje - timedelta(days=6)
    ).group_by(
        Lancamento.data_pagamento
    ).order_by(
        Lancamento.data_pagamento
    ).all()
    
    # Prepara dados do gráfico semanal
    dias_semana_nomes = ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom']
    receitas_semanal = [0] * 7
    despesas_semanal = [0] * 7
    
    # Mapeia cada data para o dia da semana correspondente
    for data, receita, despesa in dados_semanal:
        dia_semana = data.weekday()  # 0 = segunda, 6 = domingo
        if 0 <= dia_semana < 7:
            receitas_semanal[dia_semana] += float(receita or 0)
            despesas_semanal[dia_semana] += float(despesa or 0)
    
    return render_template(
        'financeiro/cards/form_financeiro_fluxo_caixa_graficos.html',
        meses_anual=meses_nomes,
        receitas_anual=receitas_anual,
        despesas_anual=despesas_anual,
        dias_mensal=dias_nomes,
        receitas_mensal=receitas_mensal,
        despesas_mensal=despesas_mensal,
        dias_semana=dias_semana_nomes,
        receitas_semanal=receitas_semanal,
        despesas_semanal=despesas_semanal
    )

@financeiro_bp.route('/card/conciliacao')
@login_required
def card_conciliacao():
    is_modal = request.args.get('modal', '0') == '1'
    return render_template('financeiro/cards/form_financeiro_conciliacao.html', is_modal=is_modal)