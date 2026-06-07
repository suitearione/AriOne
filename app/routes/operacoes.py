# =============================================================================
# Caminho  : app/routes/operacoes.py
# Arquivo  : operacoes.py
# Função   : Gestão de Fluxo Operacional (Vendas, Compras, Produção).
# Padrão   : Testes_de_Integridades.md (Seção 9, 11)
# =============================================================================

from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, flash
from flask_login import login_required, current_user
from app.extensions import db
from app.models.operacoes.vendas import OrcamentoVenda, PedidoVenda, OrcamentoVendaItem, PedidoVendaItem, MetaVenda
from app.models.operacoes.compras import OrcamentoCompra, PedidoCompra
from app.models.operacoes.producao import OrdemProducao
from app.models.cadastros.cliente import Cliente
from app.models.cadastros.funcionario import Funcionario
from app.models.cadastros.fornecedor import Fornecedor
from app.models.comercial.models import TabelaPreco, TabelaPrecoItem, PerfilVenda, Revendedor, FormaPagamento
from app.models.catalogos import Produto, Insumo, MateriaPrima, ProdutoVariacao
from app.models.sistema.status import StatusWorkflow
from app.models.sistema.parametro import ParametroSistema
from app.utils.helpers import calcular_cronograma, parse_date, parse_money
from app.utils.avisos import enviar_aviso
from app.services.logistica import LogisticaService
from datetime import datetime

operacoes_bp = Blueprint('operacoes', __name__, url_prefix='/operacoes')

# 🛠️ AUTO-MIGRAÇÃO: Garante que a coluna 'numero' exista em PedidoVenda e OrdemProducao
def verificar_schema_operacoes():
    from sqlalchemy import text
    try:
        MetaVenda.__table__.create(db.engine, checkfirst=True)
    except Exception:
        db.session.rollback()

    try:
        # Verifica Pedidos
        db.session.execute(text("SELECT numero FROM op_vendas_pedidos LIMIT 1"))
    except Exception:
        db.session.rollback()
        try:
            db.session.execute(text("ALTER TABLE op_vendas_pedidos ADD COLUMN numero VARCHAR(20)"))
            db.session.commit()
        except: db.session.rollback()
    
    try:
        # Verifica Produção
        db.session.execute(text("SELECT numero FROM op_producao_ordens LIMIT 1"))
    except Exception:
        db.session.rollback()
        try:
            db.session.execute(text("ALTER TABLE op_producao_ordens ADD COLUMN numero VARCHAR(20)"))
            db.session.commit()
        except: db.session.rollback()

@operacoes_bp.route('/vendas/central')
@login_required
def central_vendas():
    """🚀 Central Visual de Vendas (Cockpit Profissional)"""
    verificar_schema_operacoes()
    from sqlalchemy import func
    from datetime import datetime, date
    
    e_id = session.get('empresa_id') or (current_user.empresa_id if current_user.is_authenticated else None)
    
    # 1. Listagens Base
    orçamentos_pendentes = OrcamentoVenda.query.order_by(OrcamentoVenda.data_emissao.desc()).all()
    pedidos_ativos = PedidoVenda.query.order_by(PedidoVenda.data_pedido.desc()).all()
    
    # Filtros de Status Estratégicos (O que ainda está em negociação ou enviado)
    status_orc = [
        'AG. APROVAÇÃO', 'AGUARDANDO APROVAÇÃO', 'ABERTO', 'EM EDIÇÃO', 
        'ENVIADO AO CLIENTE', 'ENV. AO CLIENTE', 'EM EDICAO', 'PENDENTE'
    ]
    orçamentos_lista = [o for o in orçamentos_pendentes if not o.status or o.status.upper() in [s.upper() for s in status_orc]]
    
    # 2. Cálculo de KPIs (Mês Atual)
    hoje = date.today()
    primeiro_dia = hoje.replace(day=1)
    
    # Total de Vendas (Pedidos Confirmados no Mês)
    vendas_val = db.session.query(func.sum(PedidoVenda.total_liquido))\
        .filter(PedidoVenda.data_pedido >= primeiro_dia).scalar() or 0
    vendas_mes = float(vendas_val)
        
    # Meta do Mês: 1º Busca Meta Geral da Empresa (vendedor nulo); 2º Soma metas individuais; 3º Padrão 1.2M
    meta_geral = db.session.query(MetaVenda.valor_meta)\
        .filter(MetaVenda.ano == hoje.year, MetaVenda.mes == hoje.month, MetaVenda.vendedor_id.is_(None)).scalar()
        
    if meta_geral is not None:
        meta_val = meta_geral
    else:
        meta_soma = db.session.query(func.sum(MetaVenda.valor_meta))\
            .filter(MetaVenda.ano == hoje.year, MetaVenda.mes == hoje.month, MetaVenda.vendedor_id.isnot(None)).scalar()
        meta_val = meta_soma if meta_soma is not None else 1200000.00
        
    meta_mes = float(meta_val)
    
    perc_meta = (vendas_mes / meta_mes) * 100 if meta_mes > 0 else 0
    
    import calendar
    dias_mes = calendar.monthrange(hoje.year, hoje.month)[1]
    meta_diaria = meta_mes / dias_mes if dias_mes > 0 else 0
    
    # Vendas de Hoje
    vendas_hoje_val = db.session.query(func.sum(PedidoVenda.total_liquido))\
        .filter(func.date(PedidoVenda.data_pedido) == hoje).scalar() or 0
    vendas_hoje = float(vendas_hoje_val)
    
    falta_atingir = meta_mes - vendas_mes if meta_mes > vendas_mes else 0.0
        
    # Ticket Médio
    total_pedidos_mes = db.session.query(func.count(PedidoVenda.id))\
        .filter(PedidoVenda.data_pedido >= primeiro_dia).scalar() or 1
    ticket_medio = vendas_mes / total_pedidos_mes if total_pedidos_mes > 0 else 0
    
    # Taxa de Conversão (Aproximada: Pedidos / Orçamentos Totais do Mês)
    total_orc_mes = db.session.query(func.count(OrcamentoVenda.id))\
        .filter(OrcamentoVenda.data_emissao >= primeiro_dia).scalar() or 1
    taxa_conversao = (total_pedidos_mes / total_orc_mes) * 100 if total_orc_mes > 0 else 0

    # Logística: Pedidos com Frete/Rastreio ativo
    pedidos_transito = db.session.query(func.count(PedidoVenda.id))\
        .filter(PedidoVenda.transportadora_api_id.isnot(None), PedidoVenda.status != 'ENTREGUE').scalar() or 0
        
    # Atrasos Críticos: Pedidos não entregues com data de entrega prometida vencida
    atrasos_criticos = db.session.query(func.count(PedidoVenda.id))\
        .filter(PedidoVenda.status != 'ENTREGUE', PedidoVenda.data_entrega_prometida < hoje).scalar() or 0

    # Ranking de Eficiência de Vendedores (Mês Atual)
    vendas_por_vendedor = db.session.query(
        PedidoVenda.vendedor_id,
        func.sum(PedidoVenda.total_liquido).label('total_vendas')
    ).filter(PedidoVenda.data_pedido >= primeiro_dia, PedidoVenda.vendedor_id.isnot(None))\
     .group_by(PedidoVenda.vendedor_id).all()
     
    mapa_vendas = {v_id: float(tot or 0) for v_id, tot in vendas_por_vendedor}
    
    vendedores = Funcionario.query.filter_by(ativo=True).all()
    ranking = []
    for v in vendedores:
        tot = mapa_vendas.get(v.id, 0.0)
        ranking.append({
            'nome': getattr(v, 'nome_exibivel', None) or v.nome,
            'total': tot
        })
    ranking.sort(key=lambda x: x['total'], reverse=True)
    
    max_venda = ranking[0]['total'] if ranking and ranking[0]['total'] > 0 else 1.0
    for r in ranking:
        r['perc'] = (r['total'] / max_venda) * 100 if r['total'] > 0 else (15.0 if max_venda == 1.0 else 0.0)

    is_modal = False # Forçado para respeitar a sidebar
    return render_template('operacoes/vendas/central_vendas.html', 
                           orçamentos_pendentes=orçamentos_lista, 
                           pedidos_ativos=pedidos_ativos,
                           vendedores=vendedores,
                           kpi={
                               'vendas_mes': vendas_mes,
                               'meta_mes': meta_mes,
                               'perc_meta': perc_meta,
                               'meta_diaria': meta_diaria,
                               'vendas_hoje': vendas_hoje,
                               'falta_atingir': falta_atingir,
                               'ticket_medio': ticket_medio,
                               'taxa_conversao': taxa_conversao,
                               'transito': pedidos_transito,
                               'atrasos_criticos': atrasos_criticos,
                               'ranking': ranking
                           },
                           is_modal=is_modal)

@operacoes_bp.route('/')
@login_required
def index():
    return redirect(url_for('operacoes.abas'))

@operacoes_bp.route('/abas')
@login_required
def abas():
    # Detecta aba ativa pela URL ou padrão 'vendas'
    aba_ativa = request.args.get('aba', 'vendas')
    abas_lista = [
        {'id': 'vendas',   'label': 'Vendas',    'icon': 'fas fa-hand-holding-dollar'},
        {'id': 'compras',  'label': 'Compras',   'icon': 'fas fa-cart-shopping'},
        {'id': 'producao', 'label': 'Produção',  'icon': 'fas fa-industry'},
        {'id': 'estoque',  'label': 'Estoque',   'icon': 'fas fa-boxes-stacked'},
        {'id': 'expedicao','label': 'Expedição', 'icon': 'fas fa-truck-fast'},
    ]
    try:
        return render_template('operacoes/abas_operacoes.html', abas=abas_lista, aba_ativa=aba_ativa)
    except Exception as e:
        return f"Erro ao renderizar abas de operações: {str(e)}", 500

@operacoes_bp.route('/gateway')
@login_required
def gateway_modulos_operacoes():
    return render_template('operacoes/cards/form_gateway_modulos_operacoes.html')

@operacoes_bp.route('/cards/vendas/orcamento')
@operacoes_bp.route('/vendas/orcamento/form')
@operacoes_bp.route('/vendas/orcamento/edit/<int:id>')
@login_required
def card_vendas_orcamento(id=None):
    clientes = Cliente.query.filter_by(ativo=True).all()
    vendedores = Funcionario.query.filter_by(ativo=True).all()
    revendedores = Revendedor.query.filter_by(ativa=True).all()
    tabelas = TabelaPreco.query.all()
    perfis = PerfilVenda.query.filter_by(ativa=True).all()
    formas_pagamento = FormaPagamento.query.filter_by(ativa=True).order_by(FormaPagamento.nome).all()
    
    # Busca produtos e suas variações para o datalist de busca rápida
    produtos = Produto.query.filter_by(ativo=True).order_by(Produto.descricao).all()
    variacoes = ProdutoVariacao.query.join(Produto).filter(Produto.ativo == True).all()
    
    # Status Dinâmicos (Filtrados por Tipo Orcamento)
    status_lista = StatusWorkflow.query.filter_by(tipo='ORÇAMENTO DE VENDA', ativa=True).order_by(StatusWorkflow.ordem).all()
    if not status_lista:
        status_lista = StatusWorkflow.query.filter_by(tipo='VENDAS', ativa=True).order_by(StatusWorkflow.ordem).all()
    
    # 📋 Registro Ativo (se for edição)
    target_id = id or request.args.get('id')
    orcamento = OrcamentoVenda.query.get(target_id) if target_id else None

    # 📋 Últimos Orçamentos (Pilar Auditoria)
    orcamentos_recentes = OrcamentoVenda.query.filter_by(empresa_id=session.get('empresa_id'))\
                          .order_by(OrcamentoVenda.data_emissao.desc()).limit(12).all()
    
    today = datetime.now().strftime('%Y-%m-%d')
    is_modal = request.args.get('modal') == '1'
    from app.models.comercial.models import CanalVenda
    canais_digitais = CanalVenda.query.filter_by(empresa_id=session.get('empresa_id', 1)).order_by(CanalVenda.nome).all()
    return render_template('operacoes/cards/vendas/form_vendas_orcamentos.html', 
                           clientes=clientes, vendedores=vendedores, revendedores=revendedores, 
                           tabelas=tabelas, perfis=perfis, produtos=produtos, variacoes=variacoes, 
                           today=today, is_modal=is_modal, status_lista=status_lista,
                           formas_pagamento=formas_pagamento, orcamentos_recentes=orcamentos_recentes,
                           orcamento=orcamento, canais_digitais=canais_digitais)

@operacoes_bp.route('/cards/vendas/pedido')
@operacoes_bp.route('/vendas/pedido/form')
@operacoes_bp.route('/vendas/pedido/edit/<int:id>')
@login_required
def card_vendas_pedido(id=None):
    from app.models.comercial.models import Revendedor, TabelaPreco, PerfilVenda, FormaPagamento
    from app.models.catalogos import Produto, ProdutoVariacao
    from app.models.sistema.status import StatusWorkflow
    clientes = Cliente.query.filter_by(ativo=True).all()
    vendedores = Funcionario.query.filter_by(ativo=True).all()
    revendedores = Revendedor.query.filter_by(ativa=True).all()
    tabelas = TabelaPreco.query.all()
    perfis = PerfilVenda.query.filter_by(ativa=True).all()
    formas_pagamento = FormaPagamento.query.filter_by(ativa=True).order_by(FormaPagamento.nome).all()
    
    produtos = Produto.query.filter_by(ativo=True).order_by(Produto.descricao).all()
    variacoes = ProdutoVariacao.query.join(Produto).filter(Produto.ativo == True).all()
    
    # Status Dinâmicos (Filtrados por Tipo Pedido)
    status_lista = StatusWorkflow.query.filter_by(tipo='PEDIDO DE VENDA', ativa=True).order_by(StatusWorkflow.ordem).all()
    if not status_lista:
        status_lista = StatusWorkflow.query.filter_by(tipo='VENDAS', ativa=True).order_by(StatusWorkflow.ordem).all()
    
    # 📋 Registro Ativo (se for edição)
    target_id = id or request.args.get('id')
    pedido = PedidoVenda.query.get(target_id) if target_id else None

    # 📋 Últimos Pedidos (Pilar Auditoria)
    pedidos_recentes = PedidoVenda.query.filter_by(empresa_id=session.get('empresa_id'))\
                        .order_by(PedidoVenda.data_pedido.desc()).limit(12).all()
    
    is_modal = request.args.get('modal') == '1'
    from app.models.comercial.models import CanalVenda
    canais_digitais = CanalVenda.query.filter_by(empresa_id=session.get('empresa_id', 1)).order_by(CanalVenda.nome).all()
    return render_template('operacoes/cards/vendas/form_vendas_pedidos.html', 
                           clientes=clientes, vendedores=vendedores, revendedores=revendedores, 
                           tabelas=tabelas, perfis=perfis, produtos=produtos, variacoes=variacoes, 
                           is_modal=is_modal, status_lista=status_lista, 
                           formas_pagamento=formas_pagamento, today=datetime.now().strftime('%Y-%m-%d'),
                           pedidos_recentes=pedidos_recentes, pedido=pedido, canais_digitais=canais_digitais)

@operacoes_bp.route('/vendas/pedido/novo/de_orcamento/<int:orc_id>')
@login_required
def pedido_de_orcamento(orc_id):
    """🚀 Converte Orçamento em Pedido (Pilar Workflow)"""
    orcamento = OrcamentoVenda.query.get_or_404(orc_id)
    
    # Busca dependências padrão
    clientes = Cliente.query.filter_by(ativo=True).all()
    vendedores = Funcionario.query.filter_by(ativo=True).all()
    revendedores = Revendedor.query.filter_by(ativa=True).all()
    tabelas = TabelaPreco.query.all()
    perfis = PerfilVenda.query.filter_by(ativa=True).all()
    formas_pagamento = FormaPagamento.query.filter_by(ativa=True).order_by(FormaPagamento.nome).all()
    produtos = Produto.query.filter_by(ativo=True).order_by(Produto.descricao).all()
    variacoes = ProdutoVariacao.query.join(Produto).filter(Produto.ativo == True).all()
    
    status_lista = StatusWorkflow.query.filter_by(tipo='PEDIDO DE VENDA', ativa=True).order_by(StatusWorkflow.ordem).all()
    if not status_lista:
        status_lista = StatusWorkflow.query.filter_by(tipo='VENDAS', ativa=True).order_by(StatusWorkflow.ordem).all()

    # Passamos o orcamento como base para o NOVO pedido
    return render_template('operacoes/cards/vendas/form_vendas_pedidos.html', 
                           clientes=clientes, vendedores=vendedores, revendedores=revendedores, 
                           tabelas=tabelas, perfis=perfis, produtos=produtos, variacoes=variacoes, 
                           is_modal=False, status_lista=status_lista, 
                           formas_pagamento=formas_pagamento, today=datetime.now().strftime('%Y-%m-%d'),
                           orcamento=orcamento, pedido=None)






# ── COMPRAS - CARDS ──────────────────────────────────────────────────────────

@operacoes_bp.route('/cards/compras/orcamento')
@login_required
def card_compras_orcamento():
    from app.models.sistema.status import StatusWorkflow
    fornecedores = Fornecedor.query.filter_by(ativo=True).all()
    compradores = Funcionario.query.filter_by(ativo=True).all()
    produtos = Produto.query.filter_by(ativo=True).all()
    status_lista = StatusWorkflow.query.filter_by(tipo='ORÇAMENTO DE COMPRA', ativa=True).order_by(StatusWorkflow.ordem).all()
    today = datetime.now().strftime('%Y-%m-%d')
    is_modal = request.args.get('modal') == '1'
    return render_template('operacoes/cards/compras/form_compras_orcamentos.html', 
                           fornecedores=fornecedores, compradores=compradores, produtos=produtos, 
                           tipo='orcamento', titulo='Orçamento de Compra', today=today, is_modal=is_modal, status_lista=status_lista)

@operacoes_bp.route('/cards/compras/pedido')
@login_required
def card_compras_pedido():
    from app.models.sistema.status import StatusWorkflow
    fornecedores = Fornecedor.query.filter_by(ativo=True).all()
    compradores = Funcionario.query.filter_by(ativo=True).all()
    produtos = Produto.query.filter_by(ativo=True).all()
    status_lista = StatusWorkflow.query.filter_by(tipo='PEDIDO DE COMPRA', ativa=True).order_by(StatusWorkflow.ordem).all()
    today = datetime.now().strftime('%Y-%m-%d')
    is_modal = request.args.get('modal') == '1'
    return render_template('operacoes/cards/compras/form_compras_pedidos.html', 
                           fornecedores=fornecedores, compradores=compradores, produtos=produtos, 
                           tipo='pedido', titulo='Pedido de Compra', today=today, is_modal=is_modal, status_lista=status_lista)

@operacoes_bp.route('/cards/compras/consignados')
@login_required
def card_compras_consignados():
    return render_template('operacoes/cards/compras/form_compras_consignados.html')

@operacoes_bp.route('/cards/compras/devolucoes')
@login_required
def card_compras_devolucoes():
    return render_template('operacoes/cards/compras/form_compras_devolucoes.html')

@operacoes_bp.route('/cards/compras/servicos')
@login_required
def card_compras_servicos():
    return render_template('operacoes/cards/compras/form_compras_servicos.html')

@operacoes_bp.route('/cards/compras/precos')
@login_required
def card_compras_precos():
    return render_template('operacoes/cards/compras/form_compras_precos.html')

@operacoes_bp.route('/cards/compras/emaberto')
@login_required
def card_compras_emaberto():
    return render_template('operacoes/cards/compras/form_compras_emaberto.html')

# ── PRODUÇÃO - CARDS ─────────────────────────────────────────────────────────

@operacoes_bp.route('/cards/producao/op')
@login_required
def card_producao_op():
    from app.models.sistema.status import StatusWorkflow
    produtos = Produto.query.filter_by(ativo=True).all()
    funcionarios = Funcionario.query.filter_by(ativo=True).all()
    status_lista = StatusWorkflow.query.filter_by(tipo='ORDEM DE PRODUÇÃO', ativa=True).order_by(StatusWorkflow.ordem).all()
    return render_template('operacoes/cards/producao/form_producao_op.html', produtos=produtos, funcionarios=funcionarios, status_lista=status_lista)

@operacoes_bp.route('/cards/producao/plm')
@login_required
def card_producao_plm():
    return render_template('operacoes/cards/producao/form_producao_plm.html')

@operacoes_bp.route('/cards/producao/vmc')
@login_required
def card_producao_vmc():
    return render_template('operacoes/cards/producao/form_producao_vmc.html')

@operacoes_bp.route('/cards/producao/oficinas')
@login_required
def card_producao_oficinas():
    return render_template('operacoes/cards/producao/form_producao_oficinas.html')

@operacoes_bp.route('/api/producao/retorno_oficina', methods=['POST'])
@login_required
def api_retorno_oficina():
    """API para processar retorno de oficina (consumo MP + entrada PA)"""
    from producao_service import registrar_retorno_oficina

    data = request.get_json()
    op_id = data.get('op_id')
    local_oficina_id = data.get('local_oficina_id')
    custo_servico_oficina = data.get('custo_servico_oficina', 0.0)
    local_central_id = data.get('local_central_id', 1)

    if not op_id or not local_oficina_id:
        return jsonify({'success': False, 'message': 'OP ID e Local da Oficina são obrigatórios'}), 400

    success, message = registrar_retorno_oficina(op_id, local_oficina_id, custo_servico_oficina, local_central_id)

    if success:
        return jsonify({'success': True, 'message': message})
    else:
        return jsonify({'success': False, 'message': message}), 500

@operacoes_bp.route('/api/producao/baixar_insumos', methods=['POST'])
@login_required
def api_baixar_insumos():
    """API para baixar insumos do estoque baseado na composição do produto"""
    from producao_service import baixar_insumos_composicao

    data = request.get_json()
    produto_id = data.get('produto_id')
    quantidade_produzida = data.get('quantidade_produzida')
    local_estoque_id = data.get('local_estoque_id')
    variacao_id = data.get('variacao_id')
    documento_origem = data.get('documento_origem')

    if not produto_id or not quantidade_produzida or not local_estoque_id:
        return jsonify({'success': False, 'message': 'Produto ID, Quantidade e Local de Estoque são obrigatórios'}), 400

    usuario_id = current_user.id if current_user.is_authenticated else None

    success, result = baixar_insumos_composicao(
        produto_id=produto_id,
        quantidade_produzida=quantidade_produzida,
        local_estoque_id=local_estoque_id,
        variacao_id=variacao_id,
        usuario_id=usuario_id,
        documento_origem=documento_origem
    )

    if success:
        return jsonify({'success': True, 'data': result})
    else:
        return jsonify({'success': False, 'message': result}), 500

@operacoes_bp.route('/cards/producao/insumos')
@login_required
def card_producao_insumos():
    return render_template('operacoes/cards/producao/form_producao_insumos.html')

@operacoes_bp.route('/cards/producao/relatorios')
@login_required
def card_producao_relatorios():
    return render_template('operacoes/cards/producao/form_producao_relatorios.html')

@operacoes_bp.route('/cards/producao/parametros')
@login_required
def card_producao_parametros():
    return render_template('operacoes/cards/producao/form_producao_parametros.html')

# ── ESTOQUE - CARDS ──────────────────────────────────────────────────────────

@operacoes_bp.route('/cards/estoque/consulta')
@login_required
def card_estoque_consulta():
    return render_template('operacoes/cards/estoque/form_estoque_consulta.html')

@operacoes_bp.route('/cards/estoque/movimentacoes')
@login_required
def card_estoque_movimentacoes():
    return render_template('operacoes/cards/estoque/form_estoque_movimento.html')

@operacoes_bp.route('/cards/estoque/inventario')
@login_required
def card_estoque_inventario():
    return render_template('operacoes/cards/estoque/form_estoque_inventario.html')

@operacoes_bp.route('/cards/estoque/locais')
@login_required
def card_estoque_locais():
    return render_template('operacoes/cards/estoque/form_estoque_locais.html')

@operacoes_bp.route('/cards/estoque/regras')
@login_required
def card_estoque_regras():
    return render_template('operacoes/cards/estoque/form_estoque_regras.html')

@operacoes_bp.route('/cards/estoque/indicadores')
@login_required
def card_estoque_indicadores():
    return render_template('operacoes/cards/estoque/form_estoque_indicadores.html')

# ── EXPEDIÇÃO - CARDS ────────────────────────────────────────────────────────

@operacoes_bp.route('/cards/expedicao/checkout')
@login_required
def card_expedicao_checkout():
    return render_template('operacoes/cards/expedicao/form_expedicao_checkout.html')

@operacoes_bp.route('/cards/expedicao/romaneio')
@login_required
def card_expedicao_romaneio():
    return render_template('operacoes/cards/expedicao/form_expedicao_romaneio.html')

@operacoes_bp.route('/cards/expedicao/rastreamento')
@login_required
def card_expedicao_rastreamento():
    return render_template('operacoes/cards/expedicao/form_expedicao_rastreamento.html')

@operacoes_bp.route('/cards/expedicao/relatorios')
@login_required
def card_expedicao_relatorios():
    return render_template('operacoes/cards/expedicao/form_expedicao_relatorios.html')

# ── RELATÓRIOS GERAIS ────────────────────────────────────────────────────────

@operacoes_bp.route('/cards/relatorios')
@login_required
def card_operacoes_relatorios():
    is_modal = False # Forçado para respeitar a sidebar
    modulo = request.args.get('modulo', 'vendas')
    
    # ── CÁLCULO DOS INDICADORES REAIS DE VENDAS (IA OPERACIONAL) ──
    from sqlalchemy import func
    import datetime
    hoje = datetime.date.today()
    primeiro_dia = hoje.replace(day=1)
    
    # Mês anterior
    if hoje.month == 1:
        primeiro_dia_ant = datetime.date(hoje.year - 1, 12, 1)
        ultimo_dia_ant = datetime.date(hoje.year - 1, 12, 31)
    else:
        primeiro_dia_ant = datetime.date(hoje.year, hoje.month - 1, 1)
        ultimo_dia_ant = primeiro_dia - datetime.timedelta(days=1)
        
    # 1. Vendas Geral
    vendas_mes_val = db.session.query(func.sum(PedidoVenda.total_liquido))\
        .filter(PedidoVenda.data_pedido >= primeiro_dia, PedidoVenda.status != 'CANCELADO').scalar() or 0
    vendas_mes = float(vendas_mes_val)
    
    vendas_ant_val = db.session.query(func.sum(PedidoVenda.total_liquido))\
        .filter(PedidoVenda.data_pedido >= primeiro_dia_ant, PedidoVenda.data_pedido <= ultimo_dia_ant, PedidoVenda.status != 'CANCELADO').scalar() or 0
    vendas_ant = float(vendas_ant_val)
    
    if vendas_ant > 0:
        crescimento_vendas = ((vendas_mes - vendas_ant) / vendas_ant) * 100
    else:
        crescimento_vendas = 100.0 if vendas_mes > 0 else 0.0

    # 2. ABC Clientes (Top Cliente do Mês)
    top_cliente = db.session.query(Cliente.nome, func.sum(PedidoVenda.total_liquido).label('tot'))\
        .join(PedidoVenda, PedidoVenda.cliente_id == Cliente.id)\
        .filter(PedidoVenda.data_pedido >= primeiro_dia, PedidoVenda.status != 'CANCELADO')\
        .group_by(Cliente.id, Cliente.nome).order_by(func.sum(PedidoVenda.total_liquido).desc()).first()
        
    top_cliente_nome = top_cliente[0] if top_cliente else "NENHUM REGISTRO"
    top_cliente_valor = float(top_cliente[1]) if top_cliente else 0.0

    # 3. Ticket Médio
    total_pedidos_mes = db.session.query(func.count(PedidoVenda.id))\
        .filter(PedidoVenda.data_pedido >= primeiro_dia, PedidoVenda.status != 'CANCELADO').scalar() or 0
    ticket_medio = vendas_mes / total_pedidos_mes if total_pedidos_mes > 0 else 0.0
    
    total_pedidos_ant = db.session.query(func.count(PedidoVenda.id))\
        .filter(PedidoVenda.data_pedido >= primeiro_dia_ant, PedidoVenda.data_pedido <= ultimo_dia_ant, PedidoVenda.status != 'CANCELADO').scalar() or 0
    ticket_medio_ant = vendas_ant / total_pedidos_ant if total_pedidos_ant > 0 else 0.0

    # 4. Consultores (Top Vendedor do Mês)
    top_vendedor = db.session.query(Funcionario.nome, func.sum(PedidoVenda.total_liquido).label('tot'))\
        .join(PedidoVenda, PedidoVenda.vendedor_id == Funcionario.id)\
        .filter(PedidoVenda.data_pedido >= primeiro_dia, PedidoVenda.status != 'CANCELADO')\
        .group_by(Funcionario.id, Funcionario.nome).order_by(func.sum(PedidoVenda.total_liquido).desc()).first()
        
    top_vendedor_nome = top_vendedor[0] if top_vendedor else "NENHUM REGISTRO"
    top_vendedor_valor = float(top_vendedor[1]) if top_vendedor else 0.0

    # 5. ABC Produtos (Top Produto do Mês em Qtd)
    top_produto = db.session.query(Produto.descricao, func.sum(PedidoVendaItem.quantidade).label('qtd'))\
        .join(PedidoVendaItem, PedidoVendaItem.produto_id == Produto.id)\
        .join(PedidoVenda, PedidoVenda.id == PedidoVendaItem.pedido_id)\
        .filter(PedidoVenda.data_pedido >= primeiro_dia, PedidoVenda.status != 'CANCELADO')\
        .group_by(Produto.id, Produto.descricao).order_by(func.sum(PedidoVendaItem.quantidade).desc()).first()
        
    top_produto_nome = top_produto[0] if top_produto else "NENHUM REGISTRO"
    top_produto_qtd = float(top_produto[1]) if top_produto else 0.0

    # 6. Devoluções / Cancelamentos no Mês
    qtd_devolucoes = db.session.query(func.count(PedidoVenda.id))\
        .filter(PedidoVenda.data_pedido >= primeiro_dia, PedidoVenda.status == 'CANCELADO').scalar() or 0
    valor_devolucoes_val = db.session.query(func.sum(PedidoVenda.total_liquido))\
        .filter(PedidoVenda.data_pedido >= primeiro_dia, PedidoVenda.status == 'CANCELADO').scalar() or 0
    valor_devolucoes = float(valor_devolucoes_val)

    kpi = {
        'vendas_mes': vendas_mes,
        'vendas_ant': vendas_ant,
        'crescimento_vendas': crescimento_vendas,
        'top_cliente_nome': top_cliente_nome,
        'top_cliente_valor': top_cliente_valor,
        'ticket_medio': ticket_medio,
        'ticket_medio_ant': ticket_medio_ant,
        'top_vendedor_nome': top_vendedor_nome,
        'top_vendedor_valor': top_vendedor_valor,
        'top_produto_nome': top_produto_nome,
        'top_produto_qtd': top_produto_qtd,
        'qtd_devolucoes': qtd_devolucoes,
        'valor_devolucoes': valor_devolucoes
    }
    
    template = f'operacoes/cards/{modulo}/form_{modulo}_relatorios.html'
    try:
        return render_template(template, is_modal=is_modal, kpi=kpi)
    except:
        return render_template('operacoes/cards/vendas/form_vendas_relatorios.html', is_modal=is_modal, kpi=kpi)


# ── VENDAS ──────────────────────────────────────────────────────────────────

@operacoes_bp.route('/vendas/relatorios/ultimos-pedidos')
@login_required
def relatorio_ultimos_pedidos():
    """📊 Listagem Executiva dos Últimos Pedidos Realizados (Quiet Luxury)"""
    verificar_schema_operacoes()
    pedidos = PedidoVenda.query.order_by(PedidoVenda.data_pedido.desc()).limit(100).all()
    is_modal = request.args.get('modal') == '1'
    return render_template('operacoes/cards/vendas/rel_ultimos_pedidos.html', pedidos=pedidos, is_modal=is_modal)

@operacoes_bp.route('/vendas/relatorios/abc-clientes')
@login_required
def relatorio_abc_clientes():
    """📊 Listagem Executiva ABC de Clientes (Quiet Luxury)"""
    verificar_schema_operacoes()
    from sqlalchemy import func
    
    total_geral_val = db.session.query(func.sum(PedidoVenda.total_liquido)).filter(PedidoVenda.status != 'CANCELADO').scalar() or 0
    total_geral = float(total_geral_val) if float(total_geral_val) > 0 else 1.0

    clientes_abc = db.session.query(
        Cliente.nome,
        func.count(PedidoVenda.id).label('qtd_pedidos'),
        func.sum(PedidoVenda.total_liquido).label('total_comprado')
    ).join(PedidoVenda, PedidoVenda.cliente_id == Cliente.id)\
     .filter(PedidoVenda.status != 'CANCELADO')\
     .group_by(Cliente.id, Cliente.nome)\
     .order_by(func.sum(PedidoVenda.total_liquido).desc()).all()

    lista = []
    for idx, row in enumerate(clientes_abc):
        tot = float(row.total_comprado or 0)
        perc = (tot / total_geral) * 100
        lista.append({
            'posicao': idx + 1,
            'nome': row.nome,
            'qtd_pedidos': row.qtd_pedidos,
            'total_comprado': tot,
            'participacao': perc
        })

    is_modal = request.args.get('modal') == '1'
    return render_template('operacoes/cards/vendas/rel_abc_clientes.html', clientes=lista, total_geral=total_geral, is_modal=is_modal)

@operacoes_bp.route('/vendas/relatorios/painel-ticket')
@login_required
def relatorio_painel_ticket():
    """📊 Painel Executivo de Ticket Médio (Quiet Luxury)"""
    verificar_schema_operacoes()
    from sqlalchemy import func
    import datetime
    hoje = datetime.date.today()
    primeiro_dia = hoje.replace(day=1)

    vendas_mes_val = db.session.query(func.sum(PedidoVenda.total_liquido))\
        .filter(PedidoVenda.data_pedido >= primeiro_dia, PedidoVenda.status != 'CANCELADO').scalar() or 0
    vendas_mes = float(vendas_mes_val)

    qtd_pedidos_mes = db.session.query(func.count(PedidoVenda.id))\
        .filter(PedidoVenda.data_pedido >= primeiro_dia, PedidoVenda.status != 'CANCELADO').scalar() or 0
        
    ticket_medio_mes = vendas_mes / qtd_pedidos_mes if qtd_pedidos_mes > 0 else 0.0

    vendas_geral_val = db.session.query(func.sum(PedidoVenda.total_liquido))\
        .filter(PedidoVenda.status != 'CANCELADO').scalar() or 0
    vendas_geral = float(vendas_geral_val)

    qtd_pedidos_geral = db.session.query(func.count(PedidoVenda.id))\
        .filter(PedidoVenda.status != 'CANCELADO').scalar() or 0

    ticket_medio_geral = vendas_geral / qtd_pedidos_geral if qtd_pedidos_geral > 0 else 0.0

    ultimos_pedidos = PedidoVenda.query.filter(PedidoVenda.status != 'CANCELADO').order_by(PedidoVenda.data_pedido.desc()).limit(10).all()

    dados = {
        'vendas_mes': vendas_mes,
        'qtd_pedidos_mes': qtd_pedidos_mes,
        'ticket_medio_mes': ticket_medio_mes,
        'vendas_geral': vendas_geral,
        'qtd_pedidos_geral': qtd_pedidos_geral,
        'ticket_medio_geral': ticket_medio_geral,
        'ultimos_pedidos': ultimos_pedidos
    }

    is_modal = request.args.get('modal') == '1'
    return render_template('operacoes/cards/vendas/rel_painel_ticket.html', dados=dados, is_modal=is_modal)

@operacoes_bp.route('/vendas/relatorios/consultores')
@login_required
def relatorio_consultores():
    """📊 Listagem Executiva de Consultores/Vendedores (Quiet Luxury)"""
    verificar_schema_operacoes()
    from sqlalchemy import func
    
    vendedores_dados = db.session.query(
        Funcionario.nome,
        func.count(PedidoVenda.id).label('qtd_pedidos'),
        func.sum(PedidoVenda.total_liquido).label('total_vendido')
    ).join(PedidoVenda, PedidoVenda.vendedor_id == Funcionario.id)\
     .filter(PedidoVenda.status != 'CANCELADO')\
     .group_by(Funcionario.id, Funcionario.nome)\
     .order_by(func.sum(PedidoVenda.total_liquido).desc()).all()

    lista = []
    for idx, row in enumerate(vendedores_dados):
        tot = float(row.total_vendido or 0)
        comissao = tot * 0.05
        lista.append({
            'posicao': idx + 1,
            'nome': row.nome,
            'qtd_pedidos': row.qtd_pedidos,
            'total_vendido': tot,
            'comissao': comissao
        })

    is_modal = request.args.get('modal') == '1'
    return render_template('operacoes/cards/vendas/rel_consultores.html', consultores=lista, is_modal=is_modal)

@operacoes_bp.route('/vendas/relatorios/abc-produtos')
@login_required
def relatorio_abc_produtos():
    """📊 Listagem Executiva ABC de Produtos (Quiet Luxury)"""
    verificar_schema_operacoes()
    from sqlalchemy import func
    from app.models.catalogos import Produto

    produtos_abc = db.session.query(
        Produto.sku,
        Produto.descricao.label('item'),
        func.sum(PedidoVendaItem.quantidade).label('qtd'),
        PedidoVendaItem.valor_unitario.label('uni'),
        func.sum(PedidoVendaItem.valor_total).label('total')
    ).join(PedidoVendaItem, PedidoVendaItem.produto_id == Produto.id)\
     .join(PedidoVenda, PedidoVenda.id == PedidoVendaItem.pedido_id)\
     .filter(PedidoVenda.status != 'CANCELADO')\
     .group_by(Produto.id, Produto.sku, Produto.descricao, PedidoVendaItem.valor_unitario)\
     .order_by(func.sum(PedidoVendaItem.valor_total).desc()).all()

    lista = []
    for idx, row in enumerate(produtos_abc):
        lista.append({
            'ordem': idx + 1,
            'sku': row.sku or 'N/A',
            'item': row.item or 'Produto sem descrição',
            'qtd': float(row.qtd or 0),
            'uni': float(row.uni or 0),
            'total': float(row.total or 0)
        })

    is_modal = request.args.get('modal') == '1'
    return render_template('operacoes/cards/vendas/rel_abc_produtos.html', produtos=lista, is_modal=is_modal)

@operacoes_bp.route('/vendas/funil')
@login_required
def funil_vendas():
    """🚀 Kanban/Funil de Vendas (Quiet Luxury)"""
    verificar_schema_operacoes()
    orçamentos = OrcamentoVenda.query.order_by(OrcamentoVenda.data_emissao.desc()).all()
    
    enviada_status = ['ENVIADO AO CLIENTE', 'ENV. AO CLIENTE', 'AG. APROVAÇÃO', 'AGUARDANDO APROVAÇÃO', 'PENDENTE', 'ENVIADO']
    negociacao_status = ['EM NEGOCIAÇÃO', 'NEGOCIANDO']
    ganho_status = ['CONVERTIDO', 'APROVADO', 'GANHO', 'FINALIZADO']
    
    etapas = {
        'PROSPECÇÃO': [o for o in orçamentos if not o.status or o.status.upper() not in (enviada_status + negociacao_status + ganho_status)],
        'PROPOSTA ENVIADA': [o for o in orçamentos if o.status and o.status.upper() in enviada_status],
        'EM NEGOCIAÇÃO': [o for o in orçamentos if o.status and o.status.upper() in negociacao_status],
        'GANHO / CONVERTIDO': [o for o in orçamentos if o.status and o.status.upper() in ganho_status]
    }
    
    is_modal = False # Forçado para respeitar a sidebar
    return render_template('operacoes/cards/vendas/form_vendas_funil.html', etapas=etapas, is_modal=is_modal)

@operacoes_bp.route('/vendas/metas')
@login_required
def metas_vendas():
    """🏆 Gestão de Metas de Vendas"""
    verificar_schema_operacoes()
    metas = MetaVenda.query.order_by(MetaVenda.ano.desc(), MetaVenda.mes.desc()).all()
    vendedores = Funcionario.query.filter_by(ativo=True).all()
    
    is_modal = False # Forçado para respeitar a sidebar
    return render_template('operacoes/cards/vendas/form_vendas_metas.html', metas=metas, vendedores=vendedores, is_modal=is_modal)

@operacoes_bp.route('/vendas/metas/salvar', methods=['POST'])
@login_required
def salvar_meta_venda():
    verificar_schema_operacoes()
    data = request.form
    try:
        meta_id = data.get('meta_id')
        if meta_id:
            meta = MetaVenda.query.get(meta_id)
            if not meta:
                flash("Meta não encontrada", "danger")
                return redirect(url_for('operacoes.metas_vendas', modal=request.args.get('modal')))
        else:
            meta = MetaVenda(empresa_id=session.get('empresa_id') or (current_user.empresa_id if current_user.is_authenticated else 1))
            
        v_id = data.get('vendedor_id')
        meta.vendedor_id = int(v_id) if v_id else None
        meta.ano = int(data.get('ano') or datetime.now().year)
        meta.mes = int(data.get('mes') or datetime.now().month)
        meta.valor_meta = parse_money(data.get('valor_meta'))
        meta.observacoes = data.get('observacoes')
        
        db.session.add(meta)
        db.session.commit()
        
        flash("Meta salva com sucesso!", "success")
        return redirect(url_for('operacoes.metas_vendas', modal=request.args.get('modal')))
    except Exception as e:
        db.session.rollback()
        flash(f"Erro ao salvar meta: {str(e)}", "danger")
        return redirect(url_for('operacoes.metas_vendas', modal=request.args.get('modal')))

def gerar_proximo_numero(tipo='pedido', emp_id=1):
    """
    Gera o próximo número de documento (Orçamento ou Pedido) respeitando:
    - usar_sequencia_automatica
    - incremento
    - prefixo (pref_orc / pref_ped)
    - reiniciar_anual
    - sincronização com o banco para evitar colisões
    """
    from app.models.sistema.parametro import ParametroSistema
    from app.models.operacoes.vendas import OrcamentoVenda, PedidoVenda
    
    sufixo_param = 'orcamento' if tipo == 'orcamento' else 'pedido'
    pref_key = 'pref_orc' if tipo == 'orcamento' else 'pref_ped'
    
    usar_auto = ParametroSistema.get_valor(f'usar_sequencia_automatica_{sufixo_param[:3]}', '1') != '0'
    if not usar_auto:
        return "" # Deixa o usuário digitar manualmente
        
    try: incremento = int(ParametroSistema.get_valor('incremento', 1))
    except: incremento = 1
    
    prefixo = ParametroSistema.get_valor(pref_key, 'ORV-' if tipo == 'orcamento' else 'PV-')
    reiniciar_anual = ParametroSistema.get_valor('reiniciar_anual', '0') == '1'
    
    ano_atual = datetime.now().strftime('%Y')
    if reiniciar_anual and ano_atual not in prefixo:
        prefixo = f"{prefixo.rstrip('-')}-{ano_atual}-"
        
    ult_val = ParametroSistema.get_valor(f'ult_{sufixo_param}')
    try: ult_num = int(ult_val) if ult_val and ult_val.isdigit() else (5348 if tipo == 'orcamento' else 8210)
    except: ult_num = 5348 if tipo == 'orcamento' else 8210
    
    proximo_num = ult_num + incremento
    doc_num_str = f"{prefixo}{proximo_num}"
    
    model = OrcamentoVenda if tipo == 'orcamento' else PedidoVenda
    while True:
        existente = model.query.filter_by(numero=doc_num_str, empresa_id=emp_id).first()
        if not existente:
            existente_sem_pref = model.query.filter_by(numero=str(proximo_num), empresa_id=emp_id).first()
            if not existente_sem_pref:
                break
        proximo_num += incremento
        doc_num_str = f"{prefixo}{proximo_num}"
        
    ParametroSistema.set_valor(f'ult_{sufixo_param}', str(proximo_num - incremento), grupo='vendas')
    return doc_num_str

@operacoes_bp.route('/vendas/orcamento/salvar', methods=['POST'])
@login_required
def salvar_orcamento_venda():
    """🛡️ Salvamento Mestre de Orçamento (Seção 7 e 10)"""
    verificar_schema_operacoes()
    data = request.form
    try:
        emp_id = session.get('empresa_id') or (current_user.empresa_id if current_user.is_authenticated else 1)
        orc_id = data.get('orcamento_id')
        if orc_id:
            orc = OrcamentoVenda.query.get(orc_id)
            if not orc:
                return jsonify(success=False, error="Orçamento não encontrado"), 404
            # Limpa itens antigos para reinserção
            OrcamentoVendaItem.query.filter_by(orcamento_id=orc.id).delete()
        else:
            orc = OrcamentoVenda(empresa_id=emp_id)

        orc.cliente_id = data.get('cliente_id')
        orc.vendedor_id = data.get('vendedor_id') if data.get('vendedor_id') else None
        orc.tipo_venda = data.get('tipo_venda') or 'Produtos'
        orc.condicao_pagamento = data.get('condicao_pagamento')
        orc.data_emissao = parse_date(data.get('data_emissao')) or datetime.now()
        orc.prazo_validade = parse_date(data.get('prazo_validade'))
        orc.data_entrega = parse_date(data.get('data_entrega'))
        orc.hora_entrega = data.get('hora_entrega')
        orc.tabela_preco = data.get('tabela_preco')
        orc.canal_venda = data.get('canal_venda')
        
        # 🛡️ Validação de Unicidade de Número (AriOne Integrity)
        num_doc = data.get('numero')
        if not num_doc and not orc_id:
            num_doc = gerar_proximo_numero('orcamento', emp_id)
            
        if num_doc:
            orc_id_int = int(orc_id) if orc_id else None
            existente = OrcamentoVenda.query.filter(
                OrcamentoVenda.numero == num_doc,
                OrcamentoVenda.empresa_id == emp_id,
                OrcamentoVenda.id != orc_id_int if orc_id_int else True
            ).first()
            if existente:
                return jsonify(success=False, error=f"O Orçamento nº {num_doc} já existe no sistema."), 400
        orc.numero = num_doc
        
        # Resumo Financeiro
        orc.valor_desconto = parse_money(data.get('valor_desconto'))
        orc.outros_custos = parse_money(data.get('outros_custos'))
        orc.total_frete = parse_money(data.get('total_frete'))
        
        # Logística (Entrega Customizada)
        orc.forma_envio = data.get('frete_tipo')
        orc.ent_cep = data.get('ent_cep')
        orc.ent_logradouro = data.get('ent_logradouro')
        orc.ent_numero = data.get('ent_numero')
        orc.ent_bairro = data.get('ent_bairro')
        orc.ent_cidade = data.get('ent_cidade')
        orc.ent_uf = data.get('ent_uf')
        orc.ent_complemento = data.get('ent_complemento')
        
        orc.observacoes = data.get('observacoes')
        orc.status = data.get('status_documento') or 'Aberto'
        
        db.session.add(orc)
        db.session.flush() # Para pegar o ID
        
        # 🧩 Processamento de Itens (Dinâmico)
        itens_ids = request.form.getlist('item_produto_id[]')
        itens_qtds = request.form.getlist('item_qtd[]')
        itens_precos = request.form.getlist('item_preco[]')
        
        total_bruto = 0
        for i in range(len(itens_ids)):
            if not itens_ids[i]: continue
            
            qtd = float(itens_qtds[i] or 1)
            preco = parse_money(itens_precos[i] or '0')
            total_item = qtd * preco
            total_bruto += total_item
            
            item = OrcamentoVendaItem(
                orcamento_id=orc.id,
                produto_id=itens_ids[i],
                quantidade=qtd,
                valor_unitario=preco,
                total_item=total_item
            )
            db.session.add(item)
            
        orc.total_bruto = total_bruto
        orc.total_liquido = total_bruto - orc.valor_desconto + orc.outros_custos + orc.total_frete
        
        db.session.commit()
        
        # 📊 Sincroniza Parâmetro de Numeração (Apenas se for novo)
        if not orc_id and orc.numero:
            prefixo = ParametroSistema.get_valor('pref_orc', 'ORV-')
            reiniciar_anual = ParametroSistema.get_valor('reiniciar_anual', '0') == '1'
            if reiniciar_anual:
                ano_atual = datetime.now().strftime('%Y')
                if ano_atual not in prefixo: prefixo = f"{prefixo.rstrip('-')}-{ano_atual}-"
            num_str = str(orc.numero)
            if num_str.startswith(prefixo): num_str = num_str[len(prefixo):]
            num_limpo = ''.join(filter(str.isdigit, num_str))
            if num_limpo:
                ParametroSistema.set_valor('ult_orcamento', num_limpo, grupo='vendas')
        
        # Notifica Vendas
        enviar_aviso(orc.empresa_id, 'Vendas', 'Novo Orçamento', f'Orçamento #{orc.id} criado para o cliente {orc.cliente_id}.', f'/operacoes/abas?aba=vendas')
        
        return jsonify(success=True, 
                       message=f"Orçamento #{orc.id} gerado com sucesso!", 
                       id=orc.id,
                       central=url_for("operacoes.central_vendas", modal=1),
                       orcamentos=url_for("operacoes.card_vendas_orcamento", modal=1),
                       pedidos=url_for("operacoes.card_vendas_pedido", modal=1),
                       redirect=url_for('operacoes.card_vendas_orcamento', id=orc.id, modal=request.args.get('modal')))
    except Exception as e:
        db.session.rollback()
        return jsonify(success=False, error=str(e)), 500

@operacoes_bp.route('/vendas/pedido/salvar', methods=['POST'])
@login_required
def salvar_pedido_venda():
    """🛡️ Salvamento Mestre de Pedido (Seção 7 e 10)"""
    verificar_schema_operacoes()
    data = request.form
    try:
        emp_id = session.get('empresa_id') or (current_user.empresa_id if current_user.is_authenticated else 1)
        ped_id = data.get('pedido_id')
        if ped_id:
            ped = PedidoVenda.query.get(ped_id)
            if not ped:
                return jsonify(success=False, error="Pedido não encontrado"), 404
        else:
            ped = PedidoVenda(
                empresa_id=emp_id,
                status='Aberto',
                data_pedido=datetime.now()
            )

        ped.cliente_id = data.get('cliente_id')
        ped.vendedor_id = data.get('vendedor_id') if data.get('vendedor_id') else None
        ped.tipo_venda = data.get('tipo_venda') or 'Produtos'
        ped.orcamento_id = data.get('orcamento_id') if data.get('orcamento_id') else None
        ped.canal_venda = data.get('canal_venda')
        
        # 🛡️ Validação de Unicidade de Número (AriOne Integrity)
        num_doc = data.get('numero')
        if not num_doc and not ped_id:
            num_doc = gerar_proximo_numero('pedido', emp_id)
            
        if num_doc:
            ped_id_int = int(ped_id) if ped_id else None
            existente = PedidoVenda.query.filter(
                PedidoVenda.numero == num_doc,
                PedidoVenda.empresa_id == emp_id,
                PedidoVenda.id != ped_id_int if ped_id_int else True
            ).first()
            if existente:
                return jsonify(success=False, error=f"O Pedido nº {num_doc} já existe no sistema."), 400
        ped.numero = num_doc
        
        if data.get('data_promessa'):
            ped.data_entrega_prometida = datetime.strptime(data.get('data_promessa'), '%Y-%m-%d').date()
        elif data.get('data_entrega'):
            ped.data_entrega_prometida = datetime.strptime(data.get('data_entrega'), '%Y-%m-%d').date()
        
        # Resumo Financeiro
        ped.total_bruto = parse_money(data.get('total_bruto'))
        ped.valor_desconto = parse_money(data.get('valor_desconto'))
        ped.total_liquido = parse_money(data.get('total_liquido'))
        ped.total_frete = parse_money(data.get('total_frete'))
        ped.outros_custos = parse_money(data.get('outros_custos'))
        
        # Logística (Entrega Customizada)
        ped.forma_envio = data.get('frete_tipo')
        ped.ent_cep = data.get('ent_cep')
        ped.ent_logradouro = data.get('ent_logradouro')
        ped.ent_numero = data.get('ent_numero')
        ped.ent_bairro = data.get('ent_bairro')
        ped.ent_cidade = data.get('ent_cidade')
        ped.ent_uf = data.get('ent_uf')
        ped.ent_complemento = data.get('ent_complemento')
        
        ped.status = data.get('status_documento') or 'Aberto'
        
        db.session.add(ped)
        db.session.flush()
        
        # 🔄 Workflow: Se originado de orçamento, marca como Convertido
        if ped.orcamento_id:
            orc = OrcamentoVenda.query.get(ped.orcamento_id)
            if orc:
                orc.status = 'CONVERTIDO'
        
        # 🧩 Processamento de Itens
        if ped_id:
            PedidoVendaItem.query.filter_by(pedido_id=ped.id).delete()

        itens_ids = request.form.getlist('item_produto_id[]')
        itens_qtds = request.form.getlist('item_qtd[]')
        itens_precos = request.form.getlist('item_preco[]')
        
        total_bruto = 0
        for i in range(len(itens_ids)):
            if not itens_ids[i]: continue
            
            qtd = float(itens_qtds[i] or 1)
            preco = parse_money(itens_precos[i] or '0')
            total_item = qtd * preco
            total_bruto += total_item
            
            item = PedidoVendaItem(
                pedido_id=ped.id,
                produto_id=itens_ids[i],
                quantidade=qtd,
                valor_unitario=preco,
                total_item=total_item
            )
            db.session.add(item)
            
        ped.frete = parse_money(data.get('total_frete'))
        
        db.session.commit()

        # 📊 Sincroniza Parâmetro de Numeração (Apenas se for novo)
        if not ped_id and ped.numero:
            prefixo = ParametroSistema.get_valor('pref_ped', 'PV-')
            reiniciar_anual = ParametroSistema.get_valor('reiniciar_anual', '0') == '1'
            if reiniciar_anual:
                ano_atual = datetime.now().strftime('%Y')
                if ano_atual not in prefixo: prefixo = f"{prefixo.rstrip('-')}-{ano_atual}-"
            num_str = str(ped.numero)
            if num_str.startswith(prefixo): num_str = num_str[len(prefixo):]
            num_limpo = ''.join(filter(str.isdigit, num_str))
            if num_limpo:
                ParametroSistema.set_valor('ult_pedido', num_limpo, grupo='vendas')
        return jsonify(success=True, 
                       message=f"Pedido #{ped.id} salvo com sucesso!", 
                       id=ped.id,
                       redirect=url_for('operacoes.card_vendas_pedido', id=ped.id, modal=request.args.get('modal')))
    except Exception as e:
        db.session.rollback()
        return jsonify(success=False, error=str(e)), 500

@operacoes_bp.route('/vendas/pedido/gerar', methods=['POST'])
@login_required
def gerar_pedido_venda():
    """Converte Orçamento em Pedido e engatilha o Cronograma."""
    orc_id = request.form.get('orcamento_id')
    orc = OrcamentoVenda.query.get_or_404(orc_id)
    
    try:
        # 📊 Gera número sequencial para o pedido
        novo_num_str = gerar_proximo_numero('pedido', orc.empresa_id)
        if not novo_num_str:
            ult_ped = int(ParametroSistema.get_valor('ult_pedido', 8210))
            novo_num_str = str(ult_ped + 1)
            ParametroSistema.set_valor('ult_pedido', novo_num_str, grupo='vendas')

        pedido = PedidoVenda(
            empresa_id=orc.empresa_id,
            orcamento_id=orc.id,
            numero=novo_num_str,
            data_entrega_prometida=request.form.get('data_entrega'),
            status='Aberto'
        )
        
        orc.status = 'Aprovado'
        db.session.add(pedido)
        db.session.commit()
        
        # 🚀 Gatilho de Backward Scheduling
        cronograma = calcular_cronograma(pedido.id)
        
        # Notifica Produção e Compras
        enviar_aviso(pedido.empresa_id, 'Producao', 'Novo Pedido p/ Produção', 
                     f'Pedido #{pedido.id} aguarda cronograma.', f'/producao/op/novo?pedido={pedido.id}')
        
        return jsonify(success=True, message=f"Pedido #{pedido.id} gerado! Cronograma calculado.", cronograma=cronograma)
    except Exception as e:
        db.session.rollback()
        return jsonify(success=False, error=str(e)), 500

@operacoes_bp.route('/logistica/simular', methods=['POST'])
@login_required
def simular_frete():
    """🚀 API de Simulação de Frete (Unificada)"""
    data = request.get_json() or {}
    cep = data.get('cep_destino') or data.get('cep') or request.form.get('cep')
    peso = data.get('peso') or request.form.get('peso') or 0.5
    qtd = data.get('qtd') or request.form.get('qtd') or 1
    
    if not cep:
        return jsonify(ok=False, error="CEP de destino é obrigatório"), 400
        
    try:
        altura = data.get('altura')
        largura = data.get('largura')
        comprimento = data.get('comprimento')
        total_vol = data.get('total_volume')
        max_l = data.get('max_largura')
        max_c = data.get('max_comprimento')
        
        opcoes = LogisticaService.simular_frete(
            cep, float(peso), 
            qtd=int(qtd),
            altura=altura, 
            largura=largura, 
            comprimento=comprimento,
            total_volume=total_vol,
            max_largura=max_l,
            max_comprimento=max_c
        )
        return jsonify(ok=True, opcoes=opcoes)
    except Exception as e:
        return jsonify(ok=False, error=str(e)), 500

@operacoes_bp.route('/vendas/fix-weights', methods=['POST'])
@login_required
def fix_weights():
    """🛡️ AriOne Emergency: Sincroniza pesos dos produtos no banco"""
    try:
        from app.models.catalogos import Produto
        # Força peso 0.185 para o produto ID 1 (o do exemplo)
        p = Produto.query.get(1)
        if p:
            old_peso = p.peso
            p.peso = 0.185
            db.session.add(p)
            db.session.commit()
            return jsonify(success=True, message=f"Pesos sincronizados! ID 1: {old_peso} -> {p.peso}")
        
        # Tenta buscar por SKU se ID falhar
        p_sku = Produto.query.filter_by(cod_interno='FP-AP-31').first()
        if p_sku:
            p_sku.peso = 0.185
            db.session.commit()
            return jsonify(success=True, message="Sincronizado via SKU FP-AP-31")

        return jsonify(success=False, error="Produto não encontrado (ID 1 e SKU FP-AP-31)"), 404
    except Exception as e:
        db.session.rollback()
        return jsonify(success=False, error=str(e)), 500

# ── PRODUTIVIDADE E INTEGRIDADE ──────────────────────────────────────────────

@operacoes_bp.route('/check-duplicate', methods=['POST'])
@login_required
def check_duplicate():
    """🛡️ Oráculo de Integridade (Seção 9)"""
    tabela = request.form.get('tabela')
    campo = request.form.get('campo')
    valor = request.form.get('valor')
    
    # Lógica de consulta dinâmica simplificada
    # ... (implementar conforme necessidade de cada tabela)
    
    return jsonify(duplicate=False)

@operacoes_bp.route('/vendas/orcamento/converter/<int:id>', methods=['POST'])
@login_required
def converter_orcamento_pedido(id):
    """🛡️ Conversão de Orçamento em Pedido (Seção 11)"""
    orc = OrcamentoVenda.query.get_or_404(id)
    if orc.status == 'Aprovado':
        return jsonify(success=False, error="Este orçamento já foi convertido."), 400
        
    try:
        # 📊 Gera número sequencial para o pedido
        ult_ped = int(ParametroSistema.get_valor('ult_pedido', 0))
        novo_num = ult_ped + 1
        pedido = PedidoVenda(
            empresa_id=orc.empresa_id,
            orcamento_id=orc.id,
            numero=str(novo_num),
            data_entrega_prometida=orc.data_entrega or date.today(),
            frete=orc.total_frete,
            status='Aberto'
        )
        ParametroSistema.set_valor('ult_pedido', str(novo_num), grupo='vendas')

        orc.status = 'Aprovado'
        db.session.add(pedido)
        db.session.commit()
        
        return jsonify(success=True, message=f"Pedido #{pedido.id} gerado com sucesso!")
    except Exception as e:
        db.session.rollback()
        return jsonify(success=False, error=str(e)), 500

@operacoes_bp.route('/vendas/orcamento/clonar/<int:id>', methods=['POST'])
@login_required
def clonar_orcamento_venda(id):
    """🛡️ Lógica de Clonagem de Orçamento (Seção 11)"""
    old = OrcamentoVenda.query.get_or_404(id)
    try:
        new_orc = OrcamentoVenda(
            empresa_id=old.empresa_id,
            cliente_id=old.cliente_id,
            vendedor_id=old.vendedor_id,
            data_emissao=datetime.now(),
            tabela_preco=old.tabela_preco,
            status='Aberto',
            total_bruto=old.total_bruto,
            total_liquido=old.total_liquido
        )
        db.session.add(new_orc)
        db.session.flush()
        
        for item in old.itens:
            new_item = OrcamentoVendaItem(
                orcamento_id=new_orc.id,
                produto_id=item.produto_id,
                quantidade=item.quantidade,
                valor_unitario=item.valor_unitario,
                total_item=item.total_item
            )
            db.session.add(new_item)
            
        db.session.commit()
        return jsonify(success=True, message=f"Orçamento #{new_orc.id} clonado!", id=new_orc.id)
    except Exception as e:
        db.session.rollback()
        return jsonify(success=False, error=str(e)), 500


@operacoes_bp.route('/api/produtos/get-by-sku')
@login_required
def get_produto_by_sku():
    sku_raw = request.args.get('sku', '').strip()
    perfil = request.args.get('perfil', 'Consumidor')
    
    if not sku_raw:
        return jsonify({'ok': False, 'msg': 'SKU vazio'})
    
    sku_clean = sku_raw.replace('.', '').replace('-', '').replace(' ', '')
    from app.models.catalogos import ProdutoVariacao, Produto, Insumo
    
    # 1. Busca em Variações (Filhos)
    v = ProdutoVariacao.query.filter(
        (ProdutoVariacao.sku == sku_raw) | 
        (db.func.replace(db.func.replace(db.func.replace(ProdutoVariacao.sku, '.', ''), '-', ''), ' ', '') == sku_clean)
    ).first()
    
    if v:
        p = v.produto_pai
        valor_venda = float(v.preco_venda) if v.preco_venda and v.preco_venda > 0 else 0
        if valor_venda == 0:
            valor_venda = float(p.preco_atacado if perfil == 'Revenda' else p.preco_varejo) or 0
        
        return jsonify({
            'ok': True,
            'id': p.id,
            'variacao_id': v.id,
            'sku': v.sku.upper() if v.sku else "",
            'descricao': f"{p.descricao} - {v.nome}".upper(),
            'valor_venda': valor_venda,
            'custo_bruto': float(v.custo_producao or p.preco_custo or 0),
            'unidade': p.unidade or "UN",
            'peso': float(p.peso or 0.185),
            'altura': float(p.dim_altura or 1.5),
            'largura': float(p.dim_largura or 22.0),
            'comprimento': float(p.dim_comprimento or 22.0)
        })

    # 2. Busca em Produtos (Vendas - SKU Base)
    p = Produto.query.filter(
        (Produto.referencia == sku_raw) | 
        (Produto.cod_interno == sku_raw) |
        (db.func.replace(db.func.replace(db.func.replace(Produto.referencia, '.', ''), '-', ''), ' ', '') == sku_clean) |
        (db.func.replace(db.func.replace(db.func.replace(Produto.cod_interno, '.', ''), '-', ''), ' ', '') == sku_clean) |
        (db.cast(Produto.id, db.String) == sku_raw) | 
        (Produto.cod_barras == sku_raw)
    ).first()
    
    if p:
        # 🛡️ AriOne Master Logic: Se o produto é grade, força a busca pela primeira variação
        if p.tipo_estoque == 'grade':
            v_first = ProdutoVariacao.query.filter_by(produto_id=p.id).first()
            if v_first:
                valor_venda = float(v_first.preco_venda) if v_first.preco_venda and v_first.preco_venda > 0 else 0
                if valor_venda == 0:
                    valor_venda = float(p.preco_atacado if perfil == 'Revenda' else p.preco_varejo) or 0
                
                return jsonify({
                    'ok': True,
                    'id': p.id,
                    'variacao_id': v_first.id,
                    'sku': v_first.sku.upper() if v_first.sku else (p.referencia or p.cod_interno or "").upper(),
                    'descricao': f"{p.descricao} - {v_first.nome}".upper(),
                    'valor_venda': valor_venda,
                    'custo_bruto': float(v_first.custo_producao or p.preco_custo or 0),
                    'unidade': p.unidade or "UN",
                    'peso': float(p.peso or 0.185),
                    'altura': float(p.dim_altura or 1.5),
                    'largura': float(p.dim_largura or 22.0),
                    'comprimento': float(p.dim_comprimento or 22.0)
                })

        valor_venda = float(p.preco_atacado if perfil == 'Revenda' else p.preco_varejo) or 0
        return jsonify({
            'ok': True,
            'id': p.id,
            'sku': (p.referencia or p.cod_interno or "").upper(),
            'descricao': p.descricao.upper() if p.descricao else "",
            'valor_venda': valor_venda,
            'custo_bruto': float(p.preco_custo or 0),
            'unidade': p.unidade or "UN",
            'peso': float(p.peso or 0.185),
            'altura': float(p.dim_altura or 1.5),
            'largura': float(p.dim_largura or 22.0),
            'comprimento': float(p.dim_comprimento or 22.0)
        })
    
    # 3. Busca em Insumos (Compras)
    i = Insumo.query.filter(
        (Insumo.sku == sku_raw) | 
        (db.func.replace(db.func.replace(db.func.replace(Insumo.sku, '.', ''), '-', ''), ' ', '') == sku_clean) |
        (db.cast(Insumo.id, db.String) == sku_raw)
    ).first()
    
    if i:
         return jsonify({
            'ok': True,
            'id': i.id,
            'descricao': i.descricao.upper() if i.descricao else (i.nome.upper() if hasattr(i, 'nome') else "INSUMO"),
            'valor_venda': float(i.preco_custo or 0),
            'custo_bruto': float(i.preco_custo or 0)
        })

    return jsonify({'ok': False, 'msg': 'Item não encontrado'}), 404


# ── API: TRANSPORTADORAS POR CLIENTE ──────────────────────────────────────────
# ── API: FORMAS DE PAGAMENTO COM OPERADORA ────────────────────────────────────
@operacoes_bp.route('/api/formas-pagamento')
@login_required
def api_formas_pagamento():
    """
    Retorna todas as formas de pagamento com dados da operadora associada.
    NOVO: Detecta automaticamente tipo e destinação baseado no NOME da forma
    
    Regras de destinação:
    - OPERADORA: Cartão Crédito, Cartão Débito, Link de pagamentos, PIX Gateway, Gateways
    - BANCO: Transferências, PIX Bancário, Outras formas bancárias
    - CAIXA: Dinheiro, Crédito Especial, Vale, Permuta, Carnê, Receber, Outros
    """
    from app.models.comercial.models import FormaPagamento, OperadoraFinanceira
    from app.models.gestao.caixa import Caixa
    
    formas = FormaPagamento.query.filter_by(ativa=True).all()
    
    # Carrega caixas disponíveis
    caixas = Caixa.query.filter_by(status='ABERTO').all()
    caixas_dados = [{'id': c.id, 'nome': c.nome, 'saldo': float(c.saldo_atual or 0)} for c in caixas]
    
    def detectar_tipo_e_destinacao(nome_forma, operadora_id, operadora_obj):
        """
        Detecta tipo e destinação baseado no nome da forma
        """
        nome_upper = (nome_forma or '').upper()
        
        # ═══ REGRA 1: OPERADORA (Cartão, Gateway, Link, PIX Gateway) ═══
        if any(x in nome_upper for x in ['CARTÃO', 'CARTAO', 'CREDIT', 'CRÉDITO', 'DÉBITO', 'DEBITO']):
            tipo = 'CARTAO'
            op_nome = operadora_obj.nome if operadora_obj else 'Operadora'
            return {
                'tipo_forma': tipo,
                'tipo_destino': 'OPERADORA',
                'descricao_destino': f'Operadora: {op_nome}',
                'requer_seletor': False,
                'opcoes': []
            }
        
        if any(x in nome_upper for x in ['GATEWAY', 'LINK PAGAMENTO']):
            tipo = 'GATEWAY'
            op_nome = operadora_obj.nome if operadora_obj else 'Gateway'
            return {
                'tipo_forma': tipo,
                'tipo_destino': 'OPERADORA',
                'descricao_destino': f'Gateway: {op_nome}',
                'requer_seletor': False,
                'opcoes': []
            }
        
        if 'PIX' in nome_upper and ('GATEWAY' in nome_upper or 'OPERADORA' in nome_upper):
            tipo = 'PIX'
            op_nome = operadora_obj.nome if operadora_obj else 'Gateway PIX'
            return {
                'tipo_forma': tipo,
                'tipo_destino': 'OPERADORA',
                'descricao_destino': f'Gateway PIX: {op_nome}',
                'requer_seletor': False,
                'opcoes': []
            }
        
        # ═══ REGRA 2: BANCO (Transferência, PIX Bancário, etc) ═══
        if any(x in nome_upper for x in ['TRANSFERÊNCIA', 'TRANSFERENCIA', 'BANCÁRIO', 'BANCARIO']):
            tipo = 'BANCO'
            return {
                'tipo_forma': tipo,
                'tipo_destino': 'BANCO',
                'descricao_destino': 'Banco/Conta Bancária',
                'requer_seletor': False,
                'opcoes': []
            }
        
        if 'PIX' in nome_upper and 'BANCO' in nome_upper:
            tipo = 'PIX_BANCO'
            return {
                'tipo_forma': tipo,
                'tipo_destino': 'BANCO',
                'descricao_destino': 'Banco/Conta via PIX',
                'requer_seletor': False,
                'opcoes': []
            }
        
        # ═══ REGRA 3: CAIXA (Dinheiro, Vale, Carnê, Receber, Crédito Especial, etc) ═══
        # Por padrão, tudo que não é Operadora ou Banco vai para Caixa
        if 'DINHEIRO' in nome_upper or 'ESPÉCIE' in nome_upper:
            tipo = 'DINHEIRO'
        elif any(x in nome_upper for x in ['VALE', 'ADIANTAMENTO']):
            tipo = 'VALE'
        elif any(x in nome_upper for x in ['CARNÊ', 'CARNE']):
            tipo = 'CARNE'
        elif any(x in nome_upper for x in ['RECEBER', 'PRAZO']):
            tipo = 'RECEBER'
        elif 'CRÉDITO' in nome_upper or 'CREDITO' in nome_upper:
            tipo = 'CREDITO_ESPECIAL'
        elif 'PERMUTA' in nome_upper:
            tipo = 'PERMUTA'
        else:
            tipo = 'OUTROS'
        
        return {
            'tipo_forma': tipo,
            'tipo_destino': 'CAIXA',
            'descricao_destino': 'Caixa da Empresa',
            'requer_seletor': True,
            'opcoes': caixas_dados
        }
    
    resultado = []
    for f in formas:
        operadora_dados = None
        if f.operadora_id and f.operadora:
            operadora_dados = {
                'id': f.operadora.id,
                'nome': f.operadora.nome,
                'nome_fantasia': f.operadora.nome_fantasia,
                'cnpj': f.operadora.cnpj,
                'taxa_debito': f.operadora.taxa_debito or 0,
                'taxa_pix': f.operadora.taxa_pix or 0,
                'taxa_credito_vista': f.operadora.taxa_credito_vista or 0,
                'taxa_credito_parcelado': f.operadora.taxa_credito_parcelado or 0,
                'icone': f.operadora.icone,
                'cor': f.operadora.cor
            }
        
        # ⭐ DETECTA TIPO E DESTINAÇÃO baseado no NOME
        info_dest = detectar_tipo_e_destinacao(f.nome, f.operadora_id, f.operadora)
        
        # Gera opções de parcelamento (1 até max_parcelas)
        parcelas_opcoes = []
        for i in range(1, (f.max_parcelas or 1) + 1):
            parcelas_opcoes.append({
                'numero': i,
                'intervalo_dias': (f.intervalo_dias or 0) * (i - 1) if f.intervalo_dias else 0,
                'descricao': f"{i}x" if i == 1 else f"{i}x de {f.intervalo_dias or 30} em {f.intervalo_dias or 30} dias"
            })
        
        resultado.append({
            'id': f.id,
            'nome': f.nome,
            'tipo': info_dest['tipo_forma'],
            'agrupador_operacional': f.agrupador_operacional,
            'operadora_id': f.operadora_id,
            'operadora': operadora_dados,
            'max_parcelas': f.max_parcelas or 1,
            'intervalo_dias': f.intervalo_dias or 0,
            'parcela_minima': f.parcela_minima or 0,
            'taxa_juros': f.taxa_juros or 0,
            'percentual_desconto': f.percentual_desconto or 0,
            'icone': f.icone,
            'cor': f.cor,
            'parcelas': parcelas_opcoes,
            'destinacao': {
                'tipo_destino': info_dest['tipo_destino'],
                'descricao_destino': info_dest['descricao_destino'],
                'requer_seletor': info_dest['requer_seletor'],
                'opcoes': info_dest['opcoes']
            }
        })
    
    return jsonify({
        'ok': True,
        'formas_pagamento': resultado
    })

# ── API: TRANSPORTADORAS POR CLIENTE ────────────────────────────────────────────
@operacoes_bp.route('/api/transportadoras/por-cliente')
@login_required
def api_transportadoras_por_cliente():
    """
    Retorna as transportadoras ativas que atendem a cidade do cliente informado.
    Query: ?cliente_id=<id>
    """
    from app.models.cadastros.transportadora import Transportadora
    
    cliente_id = request.args.get('cliente_id', '').strip()
    peso_total = float(request.args.get('peso', 0) or 0)
    if not cliente_id:
        return jsonify({'ok': False, 'msg': 'cliente_id obrigatório'}), 400

    cliente = Cliente.query.get(cliente_id)
    if not cliente:
        return jsonify({'ok': False, 'msg': 'Cliente não encontrado'}), 404

    # Obtém cidade e UF do endereço de entrega (ou faturamento, com fallback)
    cidade = (getattr(cliente, 'end_ent_cidade', None) or
              getattr(cliente, 'end_fat_cidade', None) or
              getattr(cliente, 'end_cidade', None) or '').strip().upper()
    uf = (getattr(cliente, 'end_ent_uf', None) or
          getattr(cliente, 'end_fat_uf', None) or
          getattr(cliente, 'end_uf', None) or '').strip().upper()

    # Busca todas as transportadoras ativas
    print(f"[API] Buscando transportadoras para {cidade}/{uf} (ID Cliente: {cliente_id}) | Peso: {peso_total}kg")
    todas = Transportadora.query.filter_by(ativo=True).all()
    
    # 🏢 Busca CEP de Origem (Prioridade: Parâmetro > Empresa)
    from app.models.sistema.parametro import ParametroSistema
    from app.models.cadastros.empresa import Empresa
    
    cep_config = ParametroSistema.get_valor('cep_origem_vendas')
    empresa = Empresa.query.first()
    
    cep_origem = (cep_config or (empresa.end_fat_cep if empresa else '01000-000')).replace('-', '').replace('.', '').strip()
    cep_destino = (cliente.end_ent_cep or cliente.end_fat_cep or '01000-000').replace('-', '').replace('.', '').strip()

    import json
    resultado = []
    for t in todas:
        rotas = []
        try:
            if t.rotas_data: rotas = json.loads(t.rotas_data)
        except: continue
        
        atende_rota = False
        precos = {'p': 'R$ --', 'm': 'R$ --', 'g': 'R$ --'}
        prazo_rota = None
        
        for r in rotas:
            if r.get('local', '').upper() == uf:
                cidades_txt = r.get('cidades', '').upper()
                if not cidades_txt or 'TODO' in cidades_txt or cidade in [c.strip() for c in cidades_txt.split(',')]:
                    atende_rota = True
                    # 🛡️ AriOne Route Intelligence: Garante que os valores sejam capturados mesmo se os flags peq/med/gra variarem
                    def format_price(v):
                        if not v or v == '—' or v == 'R$ --': return 'R$ --'
                        v_str = str(v).replace('R$ ', '').strip()
                        if not v_str: return 'R$ --'
                        return f"R$ {v_str}"

                    if r.get('peq') or r.get('val_peq'): precos['p'] = format_price(r.get('val_peq'))
                    if r.get('med') or r.get('val_med'): precos['m'] = format_price(r.get('val_med'))
                    if r.get('gra') or r.get('val_gra'): precos['g'] = format_price(r.get('val_gra'))
                    prazo_rota = r.get('prazo')
                    break
        
        if atende_rota:
            nome_upper = (t.razao_social or t.nome_fantasia or f'Transportadora #{t.id}').upper()
            logo_url = getattr(t, 'logo', '') or ''
            if not logo_url:
                if 'CORREIOS' in nome_upper or 'SEDEX' in nome_upper or 'PAC' in nome_upper:
                    logo_url = 'https://logospng.org/download/correios/logo-correios-256.png'
                elif 'MELHOR ENVIO' in nome_upper:
                    logo_url = 'https://assinatura.melhorenvio.com.br/img/logo.png'
                elif 'JADLOG' in nome_upper:
                    logo_url = 'https://logospng.org/download/jadlog/logo-jadlog-256.png'
                elif 'AZUL' in nome_upper:
                    logo_url = 'https://logospng.org/download/azul-cargo-express/logo-azul-cargo-express-256.png'
                elif 'BRASPRESS' in nome_upper:
                    logo_url = 'https://logospng.org/download/braspress/logo-braspress-256.png'
                elif 'LOGGI' in nome_upper:
                    logo_url = 'https://logospng.org/download/loggi/logo-loggi-256.png'
                elif 'FEDEX' in nome_upper:
                    logo_url = 'https://logospng.org/download/fedex/logo-fedex-256.png'
                elif 'DHL' in nome_upper:
                    logo_url = 'https://logospng.org/download/dhl/logo-dhl-256.png'
                elif 'TOTAL' in nome_upper:
                    logo_url = 'https://logospng.org/download/total-express/logo-total-express-256.png'

            resultado.append({
                'id': t.id,
                'nome': nome_upper,
                'logo': logo_url,
                'modal': t.modal_transporte if hasattr(t, 'modal_transporte') else '',
                'prazo_entrega': prazo_rota if (prazo_rota and prazo_rota != '—') else (t.prazo_entrega if hasattr(t, 'prazo_entrega') else None),
                'avaliacao': t.avaliacao if hasattr(t, 'avaliacao') else 'B',
                'whatsapp': t.whatsapp or '',
                'precos': precos
            })

    # 📦 Módulo de Simulação Externa (Correios / Melhor Envio)
    # Aqui simulamos a chamada de API externa
    if peso_total > 0:
        # Simulação de PAC
        resultado.append({
            'id': 'correios_pac',
            'nome': 'CORREIOS - PAC',
            'logo': 'https://logospng.org/download/correios/logo-correios-256.png',
            'modal': 'terrestre',
            'prazo_entrega': 8,
            'avaliacao': 'B',
            'precos': {
                'p': f"R$ {15 + (peso_total * 2):.2f}".replace('.', ','),
                'm': f"R$ {25 + (peso_total * 3):.2f}".replace('.', ','),
                'g': f"R$ {45 + (peso_total * 5):.2f}".replace('.', ',')
            },
            'external': True
        })
        # Simulação de SEDEX
        resultado.append({
            'id': 'correios_sedex',
            'nome': 'CORREIOS - SEDEX',
            'logo': 'https://logospng.org/download/correios/logo-correios-256.png',
            'modal': 'aereo',
            'prazo_entrega': 2,
            'avaliacao': 'A',
            'precos': {
                'p': f"R$ {35 + (peso_total * 5):.2f}".replace('.', ','),
                'm': f"R$ {55 + (peso_total * 8):.2f}".replace('.', ','),
                'g': f"R$ {95 + (peso_total * 12):.2f}".replace('.', ',')
            },
            'external': True
        })

    return jsonify({
        'ok': True,
        'cidade': cidade,
        'uf': uf,
        'transportadoras': resultado
    })






# ── GESTÃO DE TABELAS DE PREÇOS (OPERACIONAL) ────────────────────────────────

@operacoes_bp.route('/cards/vendas/tabelas-precos', methods=['GET', 'POST'])
@login_required
def card_tabelas_precos():
    from app.models.comercial.models import TabelaPreco, TabelaPrecoItem
    from app.models.catalogos import Categoria, Subcategoria
    try:
        if request.method == 'POST':
            tab_id = request.form.get('id')
            if tab_id:
                tabela = TabelaPreco.query.get(tab_id)
            else:
                tabela = TabelaPreco()

            tabela.nome = request.form.get('nome')
            tabela.descricao = request.form.get('descricao')
            tabela.base_calculo = request.form.get('base_calculo')
            tabela.ajuste_tipo = request.form.get('ajuste_tipo')
            tabela.ajuste_valor = float(request.form.get('ajuste_valor', 0).replace('.', '').replace(',', '.'))
            tabela.data_inicio = parse_date(request.form.get('data_inicio'))
            tabela.data_fim = parse_date(request.form.get('data_fim'))
            tabela.perfil_cliente = request.form.get('perfil_cliente')

            db.session.add(tabela)
            db.session.flush()

            # Processa Itens
            itens_ids = request.form.getlist('item_produto_id[]')
            itens_precos = request.form.getlist('item_preco[]')
            
            TabelaPrecoItem.query.filter_by(tabela_id=tabela.id).delete()
            
            for i in range(len(itens_ids)):
                if itens_ids[i]:
                    novo_item = TabelaPrecoItem()
                    novo_item.tabela_id = tabela.id
                    novo_item.produto_id = itens_ids[i]
                    preco_str = itens_precos[i].replace('.', '').replace(',', '.')
                    novo_item.preco_venda = float(preco_str if preco_str else 0)
                    db.session.add(novo_item)

            db.session.commit()
            flash('Tabela de Preços e Itens salvos com sucesso!', 'success')
            return redirect(url_for('operacoes.card_tabelas_precos', id=tabela.id, modal=1))

        tabelas = TabelaPreco.query.all()
        target_id = request.args.get('id')
        tabela_ativa = TabelaPreco.query.get(target_id) if target_id else (tabelas[0] if tabelas else None)

        categorias = Categoria.query.order_by(Categoria.nome).all()
        subcategorias = Subcategoria.query.order_by(Subcategoria.nome).all()
        fornecedores = Fornecedor.query.order_by(Fornecedor.razao_social).all()
        produtos_catalogo = Produto.query.filter_by(ativo=True).order_by(Produto.descricao).all()
        perfis = PerfilVenda.query.filter_by(ativa=True).order_by(PerfilVenda.nome).all()
        is_modal = request.args.get('modal') == '1'
        
        return render_template('operacoes/cards/vendas/form_vendas_tabelas_precos.html', 
                               tabelas=tabelas, 
                               tabela=tabela_ativa,
                               categorias=categorias,
                               subcategorias=subcategorias,
                               fornecedores=fornecedores,
                               perfis=perfis,
                               produtos_catalogo=produtos_catalogo, 
                               is_modal=is_modal)
    except Exception as e:
        db.session.rollback()
        return f"Erro Crítico nas Tabelas Operacionais: {str(e)}", 500

@operacoes_bp.route('/cards/vendas/tabelas-precos/excluir/<int:id>')
@login_required
def excluir_tabela_preco(id):
    from app.models.comercial.models import TabelaPreco, TabelaPrecoItem
    try:
        tabela = TabelaPreco.query.get_or_404(id)
        TabelaPrecoItem.query.filter_by(tabela_id=id).delete()
        db.session.delete(tabela)
        db.session.commit()
        flash('Política comercial excluída com sucesso!', 'success')
        return redirect(url_for('operacoes.card_tabelas_precos', modal=1))
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao excluir: {str(e)}', 'danger')
        return redirect(url_for('operacoes.card_tabelas_precos', id=id, modal=1))

@operacoes_bp.route('/api/comercial/buscar-lote-produtos')
@login_required
def buscar_lote_produtos():
    try:
        cat_id = request.args.get('categoria')
        sub_id = request.args.get('subcategoria')
        for_id = request.args.get('fornecedor')
        fp_filter = request.args.get('fp')
        tudo = request.args.get('tudo') == 'true'

        query = Produto.query.filter_by(ativo=True)
        
        if not tudo:
            if cat_id and cat_id.isdigit(): query = query.filter_by(categoria_id=int(cat_id))
            if sub_id and sub_id.isdigit(): query = query.filter_by(subcategoria_id=int(sub_id))
            if for_id and for_id.isdigit(): query = query.filter_by(fornecedor_id=int(for_id))
            
            if fp_filter == 'somente_fp':
                from app.models.cadastros.fornecedor import Fornecedor
                query = query.join(Fornecedor).filter(Fornecedor.is_fp == True)
        
        produtos = query.all()
        return jsonify({
            'success': True,
            'produtos': [{
                'id': p.id,
                'sku': p.cod_interno or p.referencia or f"PROD-{p.id}",
                'descricao': p.descricao,
                'preco_base': float(p.preco_varejo or 0)
            } for p in produtos]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@operacoes_bp.route('/debug/counts')
def debug_counts():
    from app.models.operacoes.vendas import OrcamentoVenda, PedidoVenda
    orc_count = OrcamentoVenda.query.count()
    ped_count = PedidoVenda.query.count()
    return jsonify(orc_count=orc_count, ped_count=ped_count, empresa_id=session.get('empresa_id'))

@operacoes_bp.route('/vendas/debug-product/<sku>', methods=['GET'])
@login_required
def debug_product(sku):
    """🔍 AriOne Debug: Inspeciona dados reais de um SKU"""
    from app.models.catalogos import Produto, ProdutoVariacao
    
    # Busca por ID ou SKU
    if sku.isdigit():
        p = Produto.query.filter((Produto.id == int(sku)) | (Produto.cod_interno == sku) | (Produto.referencia == sku)).all()
    else:
        p = Produto.query.filter((Produto.cod_interno == sku) | (Produto.referencia == sku)).all()
        
    v = ProdutoVariacao.query.filter_by(sku=sku).all()
    
    res = {
        'search_sku': sku,
        'products_found': [{
            'id': item.id,
            'desc': item.descricao,
            'peso': item.peso,
            'cod_interno': item.cod_interno,
            'referencia': item.referencia,
            'tipo_estoque': item.tipo_estoque
        } for item in p],
        'variations_found': [{
            'id': item.id,
            'sku': item.sku,
            'produto_pai_id': item.produto_id,
            'produto_pai_peso': item.produto_pai.peso if item.produto_pai else 'N/A'
        } for item in v]
    }
    return jsonify(res)
