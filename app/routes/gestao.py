# =============================================================================
# Caminho  : app/routes/gestao.py
# Arquivo  : gestao.py
# Função   : Rotas do módulo de Gestão.
# Descrição: 
#            1. /gestao/dashboard — dashboard standalone pós-login
#            2. /gestao/ — módulo com abas
#            3. /gestao/cards/* — formulários dinâmicos do dashboard (AJAX)
# =============================================================================

from flask import Blueprint, render_template, request, session, jsonify, make_response
from flask_login import login_required, current_user
from app.models.cadastros.empresa import Empresa
from app.models.gestao.ponto import Ponto
from app.extensions import db
from datetime import datetime, date, time
import json

gestao_bp = Blueprint('gestao', __name__, url_prefix='/gestao')


# =============================================================================
# 🔹 DADOS DO DASHBOARD
# =============================================================================
def _dados_dashboard():
    """Dados agregados reutilizados pelo dashboard standalone e pela aba."""
    from app.models.cadastros.funcionario import Funcionario
    from app.models.operacoes.vendas import OrcamentoVenda, PedidoVenda
    from sqlalchemy import func
    
    hoje = date.today()
    inicio_mes = date(hoje.year, hoje.month, 1)
    emp_id = session.get('empresa_id')

    # --- MAPEAMENTO DINÂMICO DE STATUS (AriOne Smart Dashboard) ---
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
    #         
    #         # 🛡️ Auto-Migração Pedidos/Produção (Garante que colunas 'numero' existam)
    #         res_ped = conn.execute(text("PRAGMA table_info(op_vendas_pedidos)"))
    #         if 'numero' not in [r[1] for r in res_ped]:
    #             conn.execute(text("ALTER TABLE op_vendas_pedidos ADD COLUMN numero VARCHAR(20)"))
    #             
    #         res_prod = conn.execute(text("PRAGMA table_info(op_producao_ordens)"))
    #         if 'numero' not in [r[1] for r in res_prod]:
    #             conn.execute(text("ALTER TABLE op_producao_ordens ADD COLUMN numero VARCHAR(20)"))
    # except Exception as e:
    #     pass # Silencioso no dashboard para não travar a UI

    status_config = StatusWorkflow.query.filter_by(dashboard_conta=True).all()
    
    # Dicionários de busca rápida (Agrupados por Módulo e Indicador)
    map_orc = {
        'Ag. Aprovação': [s.nome.upper().strip() for s in status_config if s.dashboard_modulo == 'ORCAMENTOS' and s.dashboard_indicador == 'Ag. Aprovação'],
        'Aprovados': [s.nome.upper().strip() for s in status_config if s.dashboard_modulo == 'ORCAMENTOS' and s.dashboard_indicador == 'Aprovados'],
        'Reprovados': [s.nome.upper().strip() for s in status_config if s.dashboard_modulo == 'ORCAMENTOS' and s.dashboard_indicador == 'Reprovados']
    }
    
    map_ped = {
        'Aguardando': [s.nome.upper().strip() for s in status_config if s.dashboard_modulo == 'VENDAS' and s.dashboard_indicador == 'Aguardando'],
        'Em Produção': [s.nome.upper().strip() for s in status_config if s.dashboard_modulo == 'VENDAS' and s.dashboard_indicador == 'Em Produção'],
        'Finalizados': [s.nome.upper().strip() for s in status_config if s.dashboard_modulo == 'VENDAS' and s.dashboard_indicador == 'Finalizados'],
        'Atrasados': [s.nome.upper().strip() for s in status_config if s.dashboard_modulo == 'VENDAS' and s.dashboard_indicador == 'Atrasados'],
        'Cancelados': [s.nome.upper().strip() for s in status_config if s.dashboard_modulo == 'VENDAS' and s.dashboard_indicador == 'Cancelados']
    }
    
    map_prod = {
        'Em Corte': [s.nome.upper().strip() for s in status_config if s.dashboard_modulo == 'PRODUCAO' and s.dashboard_indicador == 'Em Corte'],
        'Prensa/Pintura': [s.nome.upper().strip() for s in status_config if s.dashboard_modulo == 'PRODUCAO' and s.dashboard_indicador == 'Prensa/Pintura'],
        'Costura': [s.nome.upper().strip() for s in status_config if s.dashboard_modulo == 'PRODUCAO' and s.dashboard_indicador == 'Costura'],
        'Acabamento': [s.nome.upper().strip() for s in status_config if s.dashboard_modulo == 'PRODUCAO' and s.dashboard_indicador == 'Acabamento'],
        'Cancelados': [s.nome.upper().strip() for s in status_config if s.dashboard_modulo == 'PRODUCAO' and s.dashboard_indicador == 'Cancelados']
    }

    map_comp = {
        'Ag. Autorização': [s.nome.upper().strip() for s in status_config if s.dashboard_modulo == 'COMPRAS' and s.dashboard_indicador == 'Ag. Autorização'],
        'Ag. Entrega': [s.nome.upper().strip() for s in status_config if s.dashboard_modulo == 'COMPRAS' and s.dashboard_indicador == 'Ag. Entrega'],
        'Recebidos': [s.nome.upper().strip() for s in status_config if s.dashboard_modulo == 'COMPRAS' and s.dashboard_indicador == 'Recebidos'],
        'Atrasados': [s.nome.upper().strip() for s in status_config if s.dashboard_modulo == 'COMPRAS' and s.dashboard_indicador == 'Atrasados'],
        'Cancelados': [s.nome.upper().strip() for s in status_config if s.dashboard_modulo == 'COMPRAS' and s.dashboard_indicador == 'Cancelados']
    }

    # Fallbacks de segurança (Caso o usuário ainda não tenha configurado nada)
    if not any(map_orc.values()):
        map_orc['Ag. Aprovação'] = ['ABERTO', 'EM EDIÇÃO', 'AGUARDANDO APROVAÇÃO', 'ENVIADO AO CLIENTE']
        map_orc['Aprovados'] = ['APROVADO', 'CONVERTIDO']
        map_orc['Reprovados'] = ['REPROVADO', 'CANCELADO']
    
    if not any(map_ped.values()):
        map_ped['Aguardando'] = ['ABERTO', 'EM EDIÇÃO', 'AGUARDANDO APROVAÇÃO']
        map_ped['Em Produção'] = ['EM PRODUÇÃO', 'EM SEPARAÇÃO', 'PRODUÇÃO', 'COSTURA', 'PINTURA', 'PRENSA']
        map_ped['Finalizados'] = ['FATURADO', 'ENTREGUE', 'FINALIZADO']
        map_ped['Cancelados'] = ['CANCELADO']
        
    if not any(map_prod.values()):
        map_prod['Em Corte'] = ['CORTE', 'EM CORTE']
        map_prod['Prensa/Pintura'] = ['PRENSA', 'PINTURA']
        map_prod['Costura'] = ['COSTURA', 'EM COSTURA']
        map_prod['Acabamento'] = ['ACABAMENTO']
        map_prod['Cancelados'] = ['CANCELADO']

    if not any(map_comp.values()):
        map_comp['Ag. Autorização'] = ['AG. AUTORIZAÇÃO', 'PENDENTE']
        map_comp['Ag. Entrega'] = ['ENVIADO', 'EM TRÂNSITO']
        map_comp['Recebidos'] = ['RECEBIDO', 'FINALIZADO']
        map_comp['Cancelados'] = ['CANCELADO']

    # --- ORÇAMENTOS REALIZADOS NO MÊS ---
    q_orc = OrcamentoVenda.query.filter(OrcamentoVenda.data_emissao >= inicio_mes)
    if emp_id: q_orc = q_orc.filter(OrcamentoVenda.empresa_id == emp_id)
    orc_rows = q_orc.all()
    
    orc_total_qtd = len(orc_rows)
    orc_total_val = sum(float(o.total_liquido or 0) for o in orc_rows)
    
    orc_detalhes = {
        'Ag. Aprovação': {'qtd': 0, 'val': 0.0},
        'Aprovados':     {'qtd': 0, 'val': 0.0},
        'Reprovados':    {'qtd': 0, 'val': 0.0}
    }
    
    for o in orc_rows:
        v = float(o.total_liquido or 0)
        st = (o.status or '').upper().strip()
        
        if st in map_orc['Ag. Aprovação']:
            orc_detalhes['Ag. Aprovação']['qtd'] += 1
            orc_detalhes['Ag. Aprovação']['val'] += v
        elif st in map_orc['Aprovados']:
            orc_detalhes['Aprovados']['qtd'] += 1
            orc_detalhes['Aprovados']['val'] += v
        elif st in map_orc['Reprovados']:
            orc_detalhes['Reprovados']['qtd'] += 1
            orc_detalhes['Reprovados']['val'] += v

    # --- PEDIDOS (VENDAS) REALIZADOS NO MÊS ---
    q_ped = PedidoVenda.query.filter(PedidoVenda.data_pedido >= inicio_mes)
    if emp_id: q_ped = q_ped.filter(PedidoVenda.empresa_id == emp_id)
    ped_rows = q_ped.all()
    
    ped_total_qtd = len(ped_rows)
    ped_total_val = sum(float(p.total_liquido or 0) for p in ped_rows)
    
    ped_detalhes = {
        'Aguardando': {'qtd': 0, 'val': 0.0},
        'Em Produção': {'qtd': 0, 'val': 0.0},
        'Finalizados': {'qtd': 0, 'val': 0.0},
        'Atrasados':    {'qtd': 0, 'val': 0.0},
        'Cancelados':   {'qtd': 0, 'val': 0.0}
    }
    
    for p in ped_rows:
        v = float(p.total_liquido or 0)
        st = (p.status or '').upper().strip()

        # Prioridade para Atrasados
        if p.data_entrega_prometida and p.data_entrega_prometida < hoje and st not in ['ENTREGUE', 'CANCELADO', 'FATURADO']:
            ped_detalhes['Atrasados']['qtd'] += 1
            ped_detalhes['Atrasados']['val'] += v
        elif st in map_ped['Aguardando']:
            ped_detalhes['Aguardando']['qtd'] += 1
            ped_detalhes['Aguardando']['val'] += v
        elif st in map_ped['Em Produção']:
            ped_detalhes['Em Produção']['qtd'] += 1
            ped_detalhes['Em Produção']['val'] += v
        elif st in map_ped['Finalizados']:
            ped_detalhes['Finalizados']['qtd'] += 1
            ped_detalhes['Finalizados']['val'] += v
        elif st in map_ped['Cancelados']:
            ped_detalhes['Cancelados']['qtd'] += 1
            ped_detalhes['Cancelados']['val'] += v

    # --- COMPRAS (PEDIDOS DE COMPRA) ---
    from app.models.operacoes.compras import PedidoCompra
    q_comp = PedidoCompra.query.filter(PedidoCompra.data_pedido >= inicio_mes)
    if emp_id: q_comp = q_comp.filter(PedidoCompra.empresa_id == emp_id)
    comp_rows = q_comp.all()
    
    comp_total_qtd = len(comp_rows)
    comp_total_val = 0.0
    
    comp_detalhes = {
        'Ag. Autorização': {'qtd': 0, 'val': 0.0},
        'Ag. Entrega':     {'qtd': 0, 'val': 0.0},
        'Recebidos':       {'qtd': 0, 'val': 0.0},
        'Atrasados':       {'qtd': 0, 'val': 0.0},
        'Cancelados':      {'qtd': 0, 'val': 0.0}
    }
    
    for cp in comp_rows:
        st = (cp.status or '').upper().strip()
        # Calculando valor baseado nos itens (Seção 10)
        v = sum(float(it.total_item or 0) for it in cp.itens)
        comp_total_val += v
        
        # Prioridade para Atrasados
        if cp.data_entrega and cp.data_entrega < hoje and st not in ['RECEBIDO', 'CANCELADO', 'FINALIZADO']:
            comp_detalhes['Atrasados']['qtd'] += 1
            comp_detalhes['Atrasados']['val'] += v
        elif st in map_comp['Ag. Autorização']:
            comp_detalhes['Ag. Autorização']['qtd'] += 1
            comp_detalhes['Ag. Autorização']['val'] += v
        elif st in map_comp['Ag. Entrega']:
            comp_detalhes['Ag. Entrega']['qtd'] += 1
            comp_detalhes['Ag. Entrega']['val'] += v
        elif st in map_comp['Recebidos']:
            comp_detalhes['Recebidos']['qtd'] += 1
            comp_detalhes['Recebidos']['val'] += v
        elif st in map_comp['Cancelados']:
            comp_detalhes['Cancelados']['qtd'] += 1
            comp_detalhes['Cancelados']['val'] += v

    # --- PRODUÇÃO (ORDENS DE PRODUÇÃO) ---
    from app.models.operacoes.producao import OrdemProducao
    q_prod = OrdemProducao.query.filter(OrdemProducao.data_inicio >= inicio_mes)
    if emp_id: q_prod = q_prod.filter(OrdemProducao.empresa_id == emp_id)
    prod_rows = q_prod.all()
    
    prod_total_qtd = len(prod_rows)
    prod_total_val = 0.0 # Valor de produção pode ser calculado por custo, deixaremos como ref
    
    prod_detalhes = {
        'Em Corte': {'qtd': 0, 'val': 0.0},
        'Prensa/Pintura': {'qtd': 0, 'val': 0.0},
        'Costura':  {'qtd': 0, 'val': 0.0},
        'Acabamento': {'qtd': 0, 'val': 0.0},
        'Cancelados': {'qtd': 0, 'val': 0.0}
    }
    
    for op in prod_rows:
        st = (op.status or '').upper().strip()
        # Aqui simulamos valor baseado na quantidade para o gráfico
        v = float(op.quantidade_planejada or 0) * 10 
        
        if st in map_prod['Em Corte']:
            prod_detalhes['Em Corte']['qtd'] += 1
            prod_detalhes['Em Corte']['val'] += v
        elif st in map_prod['Prensa/Pintura']:
            prod_detalhes['Prensa/Pintura']['qtd'] += 1
            prod_detalhes['Prensa/Pintura']['val'] += v
        elif st in map_prod['Costura']:
            prod_detalhes['Costura']['qtd'] += 1
            prod_detalhes['Costura']['val'] += v
        elif st in map_prod['Acabamento']:
            prod_detalhes['Acabamento']['qtd'] += 1
            prod_detalhes['Acabamento']['val'] += v
        elif st in map_prod['Cancelados']:
            prod_detalhes['Cancelados']['qtd'] += 1
            prod_detalhes['Cancelados']['val'] += v

    # --- FINANCEIRO (LANCAMENTOS REAIS) ---
    from app.models.gestao.lancamento import Lancamento
    q_lanc = Lancamento.query
    if emp_id: q_lanc = q_lanc.filter(Lancamento.empresa_id == emp_id)
    lanc_rows = q_lanc.all()

    receita_mes = 0.0
    despesa_mes = 0.0
    a_receber = 0.0
    a_pagar = 0.0

    ano_atual = hoje.year
    grafico_receitas = [0.0] * 12
    grafico_despesas = [0.0] * 12

    for l in lanc_rows:
        v = float(l.valor or 0)
        st = (l.status or '').upper().strip()
        t = (l.tipo or '').upper().strip()

        if t == 'RECEITA':
            if st == 'PAGO':
                dt = l.data_pagamento or l.data_vencimento
                if dt:
                    dt_val = dt.date() if isinstance(dt, datetime) else dt
                    if dt_val >= inicio_mes:
                        receita_mes += v
            elif st != 'CANCELADO':
                a_receber += v
        elif t == 'DESPESA':
            if st == 'PAGO':
                dt = l.data_pagamento or l.data_vencimento
                if dt:
                    dt_val = dt.date() if isinstance(dt, datetime) else dt
                    if dt_val >= inicio_mes:
                        despesa_mes += v
            elif st != 'CANCELADO':
                a_pagar += v

        # Lógica Anual (Gráfico de Barras do Fluxo de Caixa Anual)
        dt_anual = l.data_pagamento if st == 'PAGO' else l.data_vencimento
        if dt_anual:
            dt_a_val = dt_anual.date() if isinstance(dt_anual, datetime) else dt_anual
            if dt_a_val.year == ano_atual and st != 'CANCELADO':
                mes_idx = dt_a_val.month - 1 # 0 a 11
                if t == 'RECEITA':
                    grafico_receitas[mes_idx] += v
                elif t == 'DESPESA':
                    grafico_despesas[mes_idx] += v

    saldo_mes = receita_mes - despesa_mes

    # Simulação de Auditoria de Integridade
    integrity_issues = []
    dupes = db.session.query(Funcionario.cpf, func.count(Funcionario.id)).group_by(Funcionario.cpf).having(func.count(Funcionario.id) > 1).all()
    if dupes:
        integrity_issues.append({'tipo': 'danger', 'msg': f'{len(dupes)} CPFs Duplicados Detectados!', 'icone': 'fa-id-card'})
    
    orfaos = Funcionario.query.filter(Funcionario.empresa_id == None).count()
    if orfaos > 0:
        integrity_issues.append({'tipo': 'warning', 'msg': f'{orfaos} Funcionários sem Empresa!', 'icone': 'fa-building-circle-exclamation'})

    integrity_score = 100 - (len(integrity_issues) * 15)
    if integrity_score < 0: integrity_score = 0

    return dict(
        total_empresas   = Empresa.query.filter_by(ativa=True).count(),
        resumo           = {'receita_mes': receita_mes, 'despesa_mes': despesa_mes, 'saldo': saldo_mes, 'a_receber': a_receber, 'a_pagar': a_pagar},
        operacoes        = {
            'pedidos_abertos': ped_detalhes['Em Produção']['qtd'], 
            'orcamentos': {
                'total': orc_total_qtd, 'valor': orc_total_val,
                'detalhes': [
                    {'label': 'Ag. Aprovação', 'qtd': orc_detalhes['Ag. Aprovação']['qtd'], 'valor': orc_detalhes['Ag. Aprovação']['val']},
                    {'label': 'Aprovados', 'qtd': orc_detalhes['Aprovados']['qtd'], 'valor': orc_detalhes['Aprovados']['val']},
                    {'label': 'Reprovados', 'qtd': orc_detalhes['Reprovados']['qtd'], 'valor': orc_detalhes['Reprovados']['val']}
                ]
            },
            'vendas': {
                'total': ped_total_qtd, 'valor': ped_total_val,
                'detalhes': [
                    {'label': 'Aguardando', 'qtd': ped_detalhes['Aguardando']['qtd'], 'valor': ped_detalhes['Aguardando']['val']},
                    {'label': 'Em Produção', 'qtd': ped_detalhes['Em Produção']['qtd'], 'valor': ped_detalhes['Em Produção']['val']},
                    {'label': 'Finalizados', 'qtd': ped_detalhes['Finalizados']['qtd'], 'valor': ped_detalhes['Finalizados']['val']},
                    {'label': 'Atrasados', 'qtd': ped_detalhes['Atrasados']['qtd'], 'valor': ped_detalhes['Atrasados']['val']},
                    {'label': 'Cancelados', 'qtd': ped_detalhes['Cancelados']['qtd'], 'valor': ped_detalhes['Cancelados']['val']}
                ]
            },
            'compras': {
                'total': comp_total_qtd, 'valor': comp_total_val,
                'detalhes': [
                    {'label': 'Ag. Autorização', 'qtd': comp_detalhes['Ag. Autorização']['qtd'], 'valor': comp_detalhes['Ag. Autorização']['val']},
                    {'label': 'Ag. Entrega', 'qtd': comp_detalhes['Ag. Entrega']['qtd'], 'valor': comp_detalhes['Ag. Entrega']['val']},
                    {'label': 'Recebidos', 'qtd': comp_detalhes['Recebidos']['qtd'], 'valor': comp_detalhes['Recebidos']['val']},
                    {'label': 'Atrasados', 'qtd': comp_detalhes['Atrasados']['qtd'], 'valor': comp_detalhes['Atrasados']['val']},
                    {'label': 'Cancelados', 'qtd': comp_detalhes['Cancelados']['qtd'], 'valor': comp_detalhes['Cancelados']['val']}
                ]
            },
            'producao': {
                'total': prod_total_qtd, 'valor': prod_total_val,
                'detalhes': [
                    {'label': 'Em Corte', 'qtd': prod_detalhes['Em Corte']['qtd'], 'valor': prod_detalhes['Em Corte']['val']},
                    {'label': 'Prensa/Pintura', 'qtd': prod_detalhes['Prensa/Pintura']['qtd'], 'valor': prod_detalhes['Prensa/Pintura']['val']},
                    {'label': 'Costura', 'qtd': prod_detalhes['Costura']['qtd'], 'valor': prod_detalhes['Costura']['val']},
                    {'label': 'Acabamento', 'qtd': prod_detalhes['Acabamento']['qtd'], 'valor': prod_detalhes['Acabamento']['val']},
                    {'label': 'Cancelados', 'qtd': prod_detalhes['Cancelados']['qtd'], 'valor': prod_detalhes['Cancelados']['val']}
                ]
            },
            'pedidos_atrasados': ped_detalhes['Atrasados']['qtd']
        },
        alertas          = [
            {'link': '#', 'tipo': 'warning', 'icone': 'fa-triangle-exclamation', 'texto': 'Estoque de Tecido Ouro abaixo do mínimo'},
            {'link': '#', 'tipo': 'danger', 'icone': 'fa-clock', 'texto': f"{ped_detalhes['Atrasados']['qtd']} Pedidos de Produção Atrasados"}
        ],
        integrity_score  = integrity_score,
        integrity_issues = integrity_issues,
        grafico_meses    = ['Jan','Fev','Mar','Abr','Mai','Jun','Jul','Ago','Set','Out','Nov','Dez'],
        grafico_receitas = grafico_receitas,
        grafico_despesas = grafico_despesas,
        usuario          = current_user,
    )


# =============================================================================
# 🔹 1. Dashboard standalone — pós-login
# =============================================================================
@gestao_bp.route('/dashboard')
@login_required
def dashboard():
    """Dashboard limpo, sem abas — primeira tela após o login."""
    return render_template('gestao/dashboard.html', **_dados_dashboard())


# =============================================================================
# 🔹 2. Módulo Gestão com abas (Padrão do Sistema)
# =============================================================================
@gestao_bp.route('/')
@gestao_bp.route('/abas')
@login_required
def abas():
    """Módulo Gestão com abas — tela principal com o Dashboard clássico."""

    abas_lista = [
        {'id': 'dashboard', 'label': 'Dashboard', 'icon': 'fas fa-chart-line'},
        {'id': 'marketing', 'label': 'Marketing', 'icon': 'fas fa-bullhorn'},
        {'id': 'pessoas',   'label': 'Pessoal RH', 'icon': 'fas fa-user-tie'},
        {'id': 'relatorios', 'label': 'Central de Relatórios', 'icon': 'fas fa-file-invoice-dollar'},
    ]

    ids_validos = [a['id'] for a in abas_lista]

    aba_ativa = request.args.get('aba', 'dashboard')
    if aba_ativa not in ids_validos:
        aba_ativa = 'dashboard'

    ctx = {'abas': abas_lista, 'aba_ativa': aba_ativa}

    if aba_ativa == 'dashboard':
        ctx.update(_dados_dashboard())

    return render_template('gestao/abas_gestao.html', **ctx)


# ── ROTA: AUDITORIA DETALHADA (PAA AUDIT HUB) ──
@gestao_bp.route('/auditoria/detalhes')
@login_required
def auditoria_detalhes():
    from app.models.cadastros.funcionario import Funcionario
    from app.models.cadastros.empresa import Empresa
    from app.models.catalogos import Servico # Corrigido
    from sqlalchemy import func

    erros = []
    
    # 1. Busca Duplicidades de CPF
    dupes = db.session.query(Funcionario.cpf, func.count(Funcionario.id)).group_by(Funcionario.cpf).having(func.count(Funcionario.id) > 1).all()
    for cpf, qtd in dupes:
        if cpf:
            erros.append({
                'modulo': 'Pessoas',
                'tipo': 'Duplicidade',
                'descricao': f'CPF {cpf} encontrado em {qtd} registros.',
                'gravidade': 'Alta',
                'icone': 'fa-id-card'
            })

    # 2. Busca Funcionários Órfãos (Sem Empresa)
    orfaos = Funcionario.query.filter(Funcionario.empresa_id == None).all()
    for f in orfaos:
        erros.append({
            'modulo': 'Pessoas',
            'tipo': 'Vínculo Ausente',
            'descricao': f'Funcionário {f.nome} não possui empresa vinculada.',
            'gravidade': 'Média',
            'icone': 'fa-user-slash'
        })

    # 3. Busca Empresas sem CNPJ (Exemplo de dados incompletos)
    empresas_incompletas = Empresa.query.filter((Empresa.cnpj == '') | (Empresa.cnpj == None)).all()
    for emp in empresas_incompletas:
        erros.append({
            'modulo': 'Cadastros',
            'tipo': 'Dado Incompleto',
            'descricao': f'Empresa {emp.razao_social} está sem CNPJ cadastrado.',
            'gravidade': 'Média',
            'icone': 'fa-building'
        })

    # Cálculo final de Score para o relatório
    score = 100 - (len(erros) * 5)
    if score < 0: score = 0

    return render_template('gestao/modais/modal_auditoria_detalhes.html', erros=erros, score=score)

@gestao_bp.route("/card/gateway/modulos")
@login_required
def gateway_modulos_gestao():
    return render_template('gestao/cards/form_gateway_modulos_gestao.html')

@gestao_bp.route("/cards/gestao/relatorios")
@login_required
def card_gestao_relatorios():
    modulo = request.args.get('modulo', 'dashboard')
    titulos = {
        'dashboard': 'Indicadores Gerenciais',
        'marketing': 'Análise de Marketing',
        'pessoas':   'Relatórios de H.C.M'
    }
    cores = {
        'dashboard': '#2C3E50',
        'marketing': '#D35400',
        'pessoas':   '#7A255F'
    }
    return render_template('gestao/cards/form_gestao_relatorios.html', 
                            titulo=titulos.get(modulo, 'Gestão'), 
                            cor=cores.get(modulo, '#2c3e50'), 
                            modulo=modulo)

# =============================================================================
# 🔹 3. CARDS DO DASHBOARD (AJAX)
# =============================================================================

def _filtrar_vendas_query(query, Model, ItemModel, args):
    from app.models.cadastros.cliente import Cliente
    from app.models.catalogos import Produto, ProdutoVariacao
    from datetime import date, timedelta
    
    # 1. Período
    hoje = date.today()
    periodo = args.get('periodo', 'mes').strip()
    dt_inicio = None
    dt_fim = None
    
    if periodo == 'hoje':
        dt_inicio = hoje
        dt_fim = hoje
    elif periodo == 'semana':
        dt_inicio = hoje - timedelta(days=hoje.weekday())
        dt_fim = dt_inicio + timedelta(days=6)
    elif periodo == 'mes':
        dt_inicio = date(hoje.year, hoje.month, 1)
        if hoje.month == 12: dt_fim = date(hoje.year, 12, 31)
        else: dt_fim = date(hoje.year, hoje.month + 1, 1) - timedelta(days=1)
    elif periodo == 'ano':
        dt_inicio = date(hoje.year, 1, 1)
        dt_fim = date(hoje.year, 12, 31)
    elif periodo == 'personalizado':
        d_ini_str = args.get('data_inicio')
        d_fim_str = args.get('data_final')
        if d_ini_str:
            try: dt_inicio = date.fromisoformat(d_ini_str)
            except: pass
        if d_fim_str:
            try: dt_fim = date.fromisoformat(d_fim_str)
            except: pass

    campo_data = Model.data_emissao if hasattr(Model, 'data_emissao') else Model.data_pedido
    if dt_inicio:
        query = query.filter(campo_data >= dt_inicio)
    if dt_fim:
        query = query.filter(campo_data <= dt_fim)

    # 2. Código / Tabela
    cod = args.get('codigo_orcamento' if hasattr(Model, 'data_emissao') else 'codigo_pedido', '').strip()
    if cod:
        query = query.filter((Model.numero.ilike(f"%{cod}%")) | (Model.tabela_preco.ilike(f"%{cod}%")))

    # 3. Consultor
    consultor_id = args.get('consultor', '').strip()
    if consultor_id and consultor_id.isdigit():
        query = query.filter(Model.vendedor_id == int(consultor_id))

    # 3b. Status
    status = args.get('status', '').strip()
    if status and status != 'Todos':
        query = query.filter(Model.status.ilike(f"%{status}%"))

    # 4. Cliente & Tipo de Cliente
    cliente_str = args.get('cliente', '').strip()
    tipo_cli = args.get('tipo_cliente', '').strip()
    
    if cliente_str or tipo_cli:
        query = query.join(Cliente, Model.cliente_id == Cliente.id)
        if cliente_str:
            if ' - ' in cliente_str:
                partes = [p.strip() for p in cliente_str.split(' - ')]
                query = query.filter((Cliente.nome.ilike(f"%{partes[0]}%")) | (Cliente.cpf_cnpj.ilike(f"%{partes[1]}%")))
            else:
                query = query.filter((Cliente.nome.ilike(f"%{cliente_str}%")) | (Cliente.cpf_cnpj.ilike(f"%{cliente_str}%")))
        if tipo_cli == 'pessoa_fisica':
            query = query.filter(Cliente.tipo_pessoa == 'F')
        elif tipo_cli == 'pessoa_juridica':
            query = query.filter(Cliente.tipo_pessoa == 'J')

    # 5. Geografia (País, Estado, Cidade, Bairro)
    estado = args.get('estado', '').strip()
    cidade = args.get('cidade', '').strip()
    bairro = args.get('bairro', '').strip()
    if estado and estado != 'Todos':
        query = query.filter(Model.ent_uf.ilike(f"%{estado}%"))
    if cidade:
        query = query.filter(Model.ent_cidade.ilike(f"%{cidade}%"))
    if bairro:
        query = query.filter(Model.ent_bairro.ilike(f"%{bairro}%"))

    # 6. Produtos (Produto, Cor, Tamanho, Categoria, Subcategoria)
    produto_str = args.get('produto', '').strip()
    cor = args.get('cor', '').strip()
    tamanho = args.get('tamanho', '').strip()
    categoria = args.get('categoria', '').strip()
    subcategoria = args.get('subcategoria', '').strip()

    if cor.lower() in ['todas', 'todos', '']: cor = ''
    if tamanho.lower() in ['todos', 'todas', '']: tamanho = ''
    if categoria.lower() in ['todas', 'todos', '']: categoria = ''
    if subcategoria.lower() in ['todas', 'todos', '']: subcategoria = ''

    if any([produto_str, cor, tamanho, categoria, subcategoria]):
        query = query.join(ItemModel, Model.id == (ItemModel.orcamento_id if hasattr(ItemModel, 'orcamento_id') else ItemModel.pedido_id))
        query = query.join(Produto, ItemModel.produto_id == Produto.id)
        if produto_str:
            query = query.filter((Produto.descricao.ilike(f"%{produto_str}%")) | (Produto.cod_interno.ilike(f"%{produto_str}%")))
        if categoria:
            query = query.filter(Produto.categoria.ilike(f"%{categoria}%"))
        if subcategoria:
            query = query.filter(Produto.subcategoria.ilike(f"%{subcategoria}%"))
        if cor or tamanho:
            query = query.join(ProdutoVariacao, ItemModel.variacao_id == ProdutoVariacao.id)
            if cor:
                query = query.filter(ProdutoVariacao.cor.ilike(f"%{cor}%"))
            if tamanho:
                query = query.filter(ProdutoVariacao.tamanho.ilike(f"%{tamanho}%"))

    # 7. Canais de Venda e Centro de Custo
    canalvenda = args.get('canalvenda', '').strip()
    centrocusto = args.get('centrocusto', '').strip()
    if canalvenda:
        if hasattr(Model, 'canal_venda'):
            query = query.filter((Model.canal_venda.ilike(f"%{canalvenda}%")) | (Model.observacoes.ilike(f"%{canalvenda}%")))
        else:
            if canalvenda == 'ShopOne':
                query = query.filter((Model.observacoes.ilike("%ShopOne%")) | (Model.observacoes.ilike("%E-commerce%")) | (Model.observacoes.ilike("%Loja Virtual%")))
            elif canalvenda == 'ChatOne':
                query = query.filter((Model.observacoes.ilike("%ChatOne%")) | (Model.observacoes.ilike("%WhatsApp%")) | (Model.observacoes.ilike("%Chat%")))
            elif canalvenda == 'SiteOne':
                query = query.filter((Model.observacoes.ilike("%SiteOne%")) | (Model.observacoes.ilike("%Site%")) | (Model.observacoes.ilike("%Portal%")))
            elif canalvenda == 'LinkOne':
                query = query.filter((Model.observacoes.ilike("%LinkOne%")) | (Model.observacoes.ilike("%Instagram%")) | (Model.observacoes.ilike("%Bio%")))
            elif canalvenda == 'LeadOne':
                query = query.filter((Model.observacoes.ilike("%LeadOne%")) | (Model.observacoes.ilike("%Landing%")) | (Model.observacoes.ilike("%Funil%")))
            else:
                query = query.filter(Model.observacoes.ilike(f"%{canalvenda}%"))

    if centrocusto:
        query = query.filter(Model.observacoes.ilike(f"%{centrocusto}%"))

    query = query.distinct()
    return query

@gestao_bp.route('/cards/orcamentos')
@login_required
def dash_orcamentos():
    from app.models.operacoes.vendas import OrcamentoVenda, OrcamentoVendaItem
    from app.models.cadastros.funcionario import Funcionario
    from app.models.cadastros.cliente import Cliente
    from app.models.catalogos import Categoria, Subcategoria, CorCatalogo, TamanhoCatalogo

    emp_id = session.get('empresa_id')
    query = OrcamentoVenda.query
    if emp_id: query = query.filter_by(empresa_id=emp_id)
    
    query = _filtrar_vendas_query(query, OrcamentoVenda, OrcamentoVendaItem, request.args)
    recentes = query.order_by(OrcamentoVenda.data_emissao.desc()).limit(20).all()

    consultores = Funcionario.query.filter_by(empresa_id=emp_id, ativo=True).all() if emp_id else Funcionario.query.filter_by(ativo=True).all()
    clientes = Cliente.query.filter_by(ativo=True).all()
    categorias = Categoria.query.filter_by(ativa=True).all()
    subcategorias = Subcategoria.query.filter_by(ativa=True).all()
    cores = CorCatalogo.query.filter_by(ativa=True).all()
    tamanhos = TamanhoCatalogo.query.filter_by(ativa=True).order_by(TamanhoCatalogo.ordem).all()
    
    from app.models.comercial.models import CanalVenda
    canais_db = CanalVenda.query.filter_by(empresa_id=emp_id or 1).order_by(CanalVenda.nome).all()
    canais_digitais = [{'nome': c.nome, 'valor': c.nome} for c in canais_db]
    if not canais_digitais:
        canais_digitais = [
            {'nome': 'ShopOne (E-commerce / Loja Virtual)', 'valor': 'ShopOne'},
            {'nome': 'ChatOne (WhatsApp & Chatbots)', 'valor': 'ChatOne'},
            {'nome': 'SiteOne (Portal Web / Site)', 'valor': 'SiteOne'},
            {'nome': 'LinkOne (Links de Bio & Campanhas)', 'valor': 'LinkOne'},
            {'nome': 'LeadOne (Landing Pages / Funis)', 'valor': 'LeadOne'},
            {'nome': 'Loja Física (Balcão / POS)', 'valor': 'Loja Física'},
            {'nome': 'Representante Comercial (B2B)', 'valor': 'Representante'},
            {'nome': 'API Externa / Integração Customizada', 'valor': 'API'}
        ]
    centrocusto = [{'nome': 'Comercial'}, {'nome': 'Marketing'}, {'nome': 'Operacional'}, {'nome': 'Diretoria'}, {'nome': 'Expedição'}]

    return render_template('gestao/cards/dashboard/form_orcamentos.html', 
                           recentes=recentes, consultores=consultores, clientes=clientes,
                           categorias=categorias, subcategorias=subcategorias,
                           cores=cores, tamanhos=tamanhos,
                           canalvenda=canais_digitais, centrocusto=centrocusto)

@gestao_bp.route('/cards/pedidos')
@login_required
def dash_pedidos():
    from app.models.operacoes.vendas import PedidoVenda, PedidoVendaItem
    from app.models.cadastros.funcionario import Funcionario
    from app.models.cadastros.cliente import Cliente
    from app.models.catalogos import Categoria, Subcategoria, CorCatalogo, TamanhoCatalogo

    emp_id = session.get('empresa_id')
    query = PedidoVenda.query
    if emp_id: query = query.filter_by(empresa_id=emp_id)
    
    query = _filtrar_vendas_query(query, PedidoVenda, PedidoVendaItem, request.args)
    recentes = query.order_by(PedidoVenda.data_pedido.desc()).limit(20).all()

    consultores = Funcionario.query.filter_by(empresa_id=emp_id, ativo=True).all() if emp_id else Funcionario.query.filter_by(ativo=True).all()
    clientes = Cliente.query.filter_by(ativo=True).all()
    categorias = Categoria.query.filter_by(ativa=True).all()
    subcategorias = Subcategoria.query.filter_by(ativa=True).all()
    cores = CorCatalogo.query.filter_by(ativa=True).all()
    tamanhos = TamanhoCatalogo.query.filter_by(ativa=True).order_by(TamanhoCatalogo.ordem).all()
    
    from app.models.comercial.models import CanalVenda
    canais_db = CanalVenda.query.filter_by(empresa_id=emp_id or 1).order_by(CanalVenda.nome).all()
    canais_digit_ped = [{'nome': c.nome, 'valor': c.nome} for c in canais_db]
    if not canais_digit_ped:
        canais_digit_ped = [
            {'nome': 'ShopOne (E-commerce / Loja Virtual)', 'valor': 'ShopOne'},
            {'nome': 'ChatOne (WhatsApp & Chatbots)', 'valor': 'ChatOne'},
            {'nome': 'SiteOne (Portal Web / Site)', 'valor': 'SiteOne'},
            {'nome': 'LinkOne (Links de Bio & Campanhas)', 'valor': 'LinkOne'},
            {'nome': 'LeadOne (Landing Pages / Funis)', 'valor': 'LeadOne'},
            {'nome': 'Loja Física (Balcão / POS)', 'valor': 'Loja Física'},
            {'nome': 'Representante Comercial (B2B)', 'valor': 'Representante'},
            {'nome': 'API Externa / Integração Customizada', 'valor': 'API'}
        ]
    centrocusto = [{'nome': 'Comercial'}, {'nome': 'Marketing'}, {'nome': 'Operacional'}, {'nome': 'Diretoria'}, {'nome': 'Expedição'}]

    return render_template('gestao/cards/dashboard/form_pedidos.html', 
                           recentes=recentes, consultores=consultores, clientes=clientes,
                           categorias=categorias, subcategorias=subcategorias,
                           cores=cores, tamanhos=tamanhos,
                           canalvenda=canais_digit_ped, centrocusto=centrocusto)

@gestao_bp.route('/cards/lucros')
@login_required
def dash_lucros():
    return render_template('gestao/cards/dashboard/form_lucros.html')

@gestao_bp.route('/cards/clientes')
@login_required
def dash_clientes():
    return render_template('gestao/cards/dashboard/form_clientes.html')

@gestao_bp.route('/cards/producao')
@login_required
def dash_producao():
    return render_template('gestao/cards/dashboard/form_producao.html')

@gestao_bp.route('/cards/prazos')
@login_required
def dash_prazos():
    return render_template('gestao/cards/dashboard/form_prazos.html')


# =============================================================================
# 🔹 CARDS DE MARKETING (AJAX)
# =============================================================================

@gestao_bp.route('/cards/canais')
@login_required
def mkt_canais():
    return render_template('gestao/cards/marketing/form_canais.html')


# =============================================================================
# 🔹 3. CARDS DE PESSOAS (AJAX)
# =============================================================================

@gestao_bp.route('/cards/recrutamento')
@login_required
def pes_recrutamento():
    return render_template('gestao/cards/pessoas/form_recrutamentos.html')


@gestao_bp.route('/cards/documentacao')
@login_required
def pes_documentacao():
    return render_template('gestao/cards/pessoas/form_documentação.html')


@gestao_bp.route('/cards/registro-legal')
@login_required
def pes_registro_legal():
    return render_template('gestao/cards/pessoas/form_registrolegal.html')


@gestao_bp.route('/cards/treinamento')
@login_required
def pes_treinamento():
    return render_template('gestao/cards/pessoas/form_treinamento.html')


@gestao_bp.route('/cards/pontos')
@login_required
def pes_pontos():
    hoje = date.today()
    
    # Permitir selecionar outro usuário (especialmente para RH)
    target_uid = request.args.get('uid', current_user.id, type=int)
    
    ponto_hoje = Ponto.query.filter_by(usuario_id=target_uid, data=hoje).first()
    historico = Ponto.query.filter_by(usuario_id=target_uid)\
                           .order_by(Ponto.data.desc())\
                           .limit(10).all()
                           
    # Buscar lista de funcionários (HCM) para o seletor
    from app.models.cadastros.funcionario import Funcionario
    funcionarios = Funcionario.query.filter_by(ativo=True).order_by(Funcionario.nome).all()
    
    # Identificar o usuário alvo (para o badge de identificação)
    from app.models.usuario import Usuario
    target_user = Usuario.query.get(target_uid) or current_user
                           
    return render_template('gestao/cards/pessoas/form_pontos.html', 
                           ponto=ponto_hoje, 
                           historico=historico,
                           hoje=hoje,
                           funcionarios=funcionarios,
                           target_user=target_user)


@gestao_bp.route('/cards/salvar-ponto', methods=['POST'])
@login_required
def salvar_ponto():
    """Registra batida de ponto automática (segura)"""
    from flask import jsonify
    
    try:
        agora = datetime.now()
        hoje = agora.date()
        hora_atual = agora.time()
        
        ponto = Ponto.query.filter_by(usuario_id=current_user.id, data=hoje).first()
        
        if not ponto:
            ponto = Ponto(
                usuario_id=current_user.id,
                empresa_id=session.get('empresa_id'),
                data=hoje,
                entrada=hora_atual
            )
            db.session.add(ponto)
            tipo = "Entrada"
        elif not ponto.saida_intervalo:
            ponto.saida_intervalo = hora_atual
            tipo = "Saída Intervalo"
        elif not ponto.retorno_intervalo:
            ponto.retorno_intervalo = hora_atual
            tipo = "Retorno Intervalo"
        elif not ponto.saida:
            ponto.saida = hora_atual
            tipo = "Saída Final"
        else:
            return jsonify(success=False, message="Todas as batidas de hoje já foram realizadas."), 400
        
        # Captura geolocalização se enviada
        ponto.geolocalizacao = request.form.get('geolocalizacao')
        
        db.session.commit()
        return jsonify(success=True, message=f"Registro de {tipo} realizado às {hora_atual.strftime('%H:%M')}!")
        
    except Exception as e:
        db.session.rollback()
        return jsonify(success=False, error=str(e)), 500


@gestao_bp.route('/cards/folha-pagamento')
@login_required
def pes_folha_pagamento():
    return render_template('gestao/cards/pessoas/form_folhapagamento.html')


@gestao_bp.route('/cards/salvar-ponto-manual', methods=['POST'])
@login_required
def salvar_ponto_manual():
    """Permite ajuste manual do ponto (com justificativa) - CRUD: Create/Update"""
    try:
        user_id = request.form.get('usuario_id', current_user.id, type=int)
        data_str = request.form.get('data')
        if not data_str:
            return jsonify(success=False, error="Data é obrigatória."), 400
        
        data_registro = date.fromisoformat(data_str)
        ponto = Ponto.query.filter_by(usuario_id=user_id, data=data_registro).first()
        
        if not ponto:
            ponto = Ponto(
                usuario_id=user_id,
                empresa_id=session.get('empresa_id'),
                data=data_registro
            )
            db.session.add(ponto)
            
        def parse_time(t_str):
            if not t_str or t_str.strip() == '': return None
            try:
                h, m = map(int, t_str.split(':'))
                return time(h, m)
            except: return None

        ponto.entrada = parse_time(request.form.get('entrada'))
        ponto.saida_intervalo = parse_time(request.form.get('saida_intervalo'))
        ponto.retorno_intervalo = parse_time(request.form.get('retorno_intervalo'))
        ponto.saida = parse_time(request.form.get('saida'))
        
        # A justificativa é obrigatória no ajuste manual
        obs = request.form.get('observacao', '').strip()
        ponto.observacao = f"[AJUSTE MANUAL] {obs}"
        
        db.session.commit()
        return jsonify(success=True, message=f"Registro de {data_registro.strftime('%d/%m/%Y')} salvo com sucesso!")
        
    except Exception as e:
        db.session.rollback()
        return jsonify(success=False, error=str(e)), 500


@gestao_bp.route('/cards/excluir-ponto/<int:id>', methods=['POST'])
@login_required
def excluir_ponto(id):
    """Exclui um registro de ponto - CRUD: Delete"""
    try:
        ponto = Ponto.query.get_or_404(id)
        # Permite excluir se for o dono ou se tiver permissão de RH (simplificado: se for Admin/RH no futuro)
        # Por enquanto mantemos a segurança básica
        if ponto.usuario_id != current_user.id and current_user.perfil != 'admin':
            return jsonify(success=False, error="Acesso negado."), 403
            
        db.session.delete(ponto)
        db.session.commit()
        return jsonify(success=True, message="Registro excluído com sucesso!")
    except Exception as e:
        db.session.rollback()
        return jsonify(success=False, error=str(e)), 500


@gestao_bp.route('/cards/indicadores')
@login_required
def pes_indicadores():
    return render_template('gestao/cards/pessoas/form_indicadores.html')


@gestao_bp.route('/relatorios/extrato-ponto')
@login_required
def gerar_extrato_ponto():
    """Gera o HTML do extrato de ponto para o período solicitado"""
    from datetime import timedelta
    
    data_inicio_str = request.args.get('data_inicio')
    data_fim_str = request.args.get('data_fim')
    usuario_id = request.args.get('funcionario_id')
    
    if not data_inicio_str or not data_fim_str:
        return "<p style='color:red;'>Datas inválidas.</p>"
        
    try:
        d_inicio = date.fromisoformat(data_inicio_str)
        d_fim = date.fromisoformat(data_fim_str)
        uid = current_user.id if usuario_id == 'all' else int(usuario_id)
        
        # Busca todos os pontos do período
        pontos = Ponto.query.filter(
            Ponto.usuario_id == uid,
            Ponto.data >= d_inicio,
            Ponto.data <= d_fim
        ).order_by(Ponto.data).all()
        
        # Mapeia para dicionário facilitando o loop de dias
        pontos_map = {p.data: p for p in pontos}
        
        extrato = []
        curr = d_inicio
        while curr <= d_fim:
            p = pontos_map.get(curr)
            total_sec = 0
            if p and p.entrada and p.saida:
                # Cálculo básico (simplificado)
                t1 = datetime.combine(p.data, p.entrada)
                t2 = datetime.combine(p.data, p.saida)
                diff = t2 - t1
                
                # Desconta almoço se houver
                if p.saida_intervalo and p.retorno_intervalo:
                    si = datetime.combine(p.data, p.saida_intervalo)
                    ri = datetime.combine(p.data, p.retorno_intervalo)
                    diff -= (ri - si)
                
                total_sec = diff.total_seconds()
            
            # Formata horas
            h = int(total_sec // 3600)
            m = int((total_sec % 3600) // 60)
            
            extrato.append({
                'data': curr,
                'ponto': p,
                'total': f"{h:02d}:{m:02d}" if total_sec > 0 else "--:--"
            })
            curr += timedelta(days=1)
            
        return render_template('gestao/relatorios/partial_extrato_ponto.html', 
                               extrato=extrato, 
                               d_inicio=d_inicio, 
                               d_fim=d_fim,
                               hoje=date.today())
    except Exception as e:
        return f"<p style='color:red;'>Erro: {str(e)}</p>"


@gestao_bp.route('/cards/pes_relatorios')
@login_required
def pes_relatorios():
    empresas_lista = Empresa.query.order_by(Empresa.razao_social).all()
    # Adicionando 'today' para o template usar nos campos de data
    return render_template('gestao/cards/pessoas/form_relatorios.html', 
                           empresas_lista=empresas_lista,
                           today=date.today())


@gestao_bp.route('/cards/setores')
@login_required
def card_setores():
    from app.models.cadastros.funcionario import Setor
    edit_id = request.args.get('id', type=int)
    setor_edit = Setor.query.get(edit_id) if edit_id else None
    setores = Setor.query.filter_by(parent_id=None).order_by(Setor.nome).all()
    resp = make_response(render_template('cadastros/cards/empresa/form_setor.html',
                           setores=setores, setor=setor_edit))
    resp.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate'
    return resp


@gestao_bp.route('/cards/departamentos')
@login_required
def card_departamentos():
    from app.models.cadastros.funcionario import Setor
    edit_id = request.args.get('id', type=int)
    depto_edit = Setor.query.get(edit_id) if edit_id else None
    departamentos = Setor.query.filter(Setor.parent_id != None).order_by(Setor.nome).all()
    setores_pais = Setor.query.filter_by(parent_id=None).order_by(Setor.nome).all()
    resp = make_response(render_template('cadastros/cards/empresa/form_departamentos.html',
                           departamentos=departamentos, setores_pais=setores_pais, depto=depto_edit))
    resp.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate'
    return resp


@gestao_bp.route('/cards/cargos')
@login_required
def card_cargos():
    from app.models.cadastros.funcionario import Cargo
    edit_id = request.args.get('id', type=int)
    cargo_edit = Cargo.query.get(edit_id) if edit_id else None
    cargos_lista = Cargo.query.order_by(Cargo.nome).all()
    resp = make_response(render_template('cadastros/cards/empresa/form_cargos.html',
                            cargos_lista=cargos_lista, cargo=cargo_edit))
    resp.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate'
    return resp


@gestao_bp.route('/cards/centro-custos', methods=['GET', 'POST'])
@login_required
def form_centro_custo():
    from app.models.gestao.centro_custo import CentroCusto
    if request.method == 'POST':
        try:
            codigo = request.form.get('codigo')
            nome = request.form.get('nome')
            tipo = request.form.get('tipo')
            contabil = request.form.get('contabil_cod')
            
            cc = CentroCusto(codigo=codigo, nome=nome, tipo=tipo, contabil_cod=contabil)
            db.session.add(cc)
            db.session.commit()
            return jsonify(success=True, message="Centro de Custo cadastrado!", id=cc.id, nome=cc.nome)
        except Exception as e:
            db.session.rollback()
            return jsonify(success=False, error=str(e)), 500
            
    return render_template('gestao/cards/form_centro_custo.html')

