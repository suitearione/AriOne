# =============================================================================
#  Arquivo  : routes_producao_op.py
#  Caminho  : app/operacoes/routes.py  (adicionar ao blueprint 'operacoes')
#  Função   : Rotas de Ordens de Produção (OP) — multi-produto
#             Gerada automaticamente ao confirmar Pedido de Vendas.
# =============================================================================

from datetime import date
from app.routes.operacoes import operacoes_bp
from flask import render_template, request, jsonify

# ─── Rotas ────────────────────────────────────────────────────────────────────

@operacoes_bp.route('/op/salvar', methods=['POST'])
def salvar_op():
    """
    Salva/atualiza uma OP.
    POST /operacoes/op/salvar
    Body JSON: { op_numero, lote, prioridade, status, abertura,
                 entrega, obs, produtos: [...], pedido_origem_id }
    """
    dados = request.get_json(silent=True) or {}

    if not dados.get('produtos'):
        return jsonify({'sucesso': False, 'mensagem': 'Inclua ao menos 1 produto.'}), 400

    # ── Persistir no banco ─────────────────────────────────────────────────
    # op = OrdemProducao.query.filter_by(numero=dados['op_numero']).first()
    # if not op:
    #     op = OrdemProducao()
    #     db.session.add(op)
    # op.numero        = dados['op_numero']
    # op.lote          = dados['lote']
    # op.prioridade    = dados['prioridade']
    # op.status        = dados['status']
    # op.dt_abertura   = dados['abertura']
    # op.dt_entrega    = dados['entrega']
    # op.observacoes   = dados['obs']
    # op.pedido_id     = dados.get('pedido_origem_id') or None
    #
    # # Itens da OP
    # ItemOP.query.filter_by(op_id=op.id).delete()
    # for p in dados['produtos']:
    #     db.session.add(ItemOP(op=op, **p))
    #
    # db.session.commit()
    # op_numero = op.numero

    op_numero = dados.get('op_numero', _gerar_numero_op())

    return jsonify({
        'sucesso':   True,
        'op_numero': op_numero,
        'mensagem':  f'OP {op_numero} salva com sucesso!'
    })


@operacoes_bp.route('/op/confirmar', methods=['POST'])
def confirmar_op():
    """
    Confirma a OP e reserva matéria-prima no estoque.
    POST /operacoes/op/confirmar
    """
    dados = request.get_json(silent=True) or {}

    qtd_total = sum(p.get('qtd_plan', 0) for p in dados.get('produtos', []))
    if qtd_total == 0:
        return jsonify({'sucesso': False, 'mensagem': 'Quantidade planejada não pode ser zero.'}), 400

    # ── Reservar estoque de MP ─────────────────────────────────────────────
    # op = OrdemProducao.query.filter_by(numero=dados['op_numero']).first()
    # for item_op in op.itens:
    #     for insumo in item_op.bom:           # BOM = Bill of Materials
    #         mat = Estoque.query.filter_by(produto_id=insumo.material_id).first()
    #         if mat:
    #             mat.saldo_reservado += insumo.quantidade_requerida
    # op.status = 'CONFIRMADA'
    # db.session.commit()

    return jsonify({
        'sucesso':  True,
        'mensagem': f'✅ OP {dados.get("op_numero")} confirmada! '
                    f'{qtd_total} unidades planejadas. Matéria-Prima reservada.'
    })


# ── Helpers (substituir por queries reais) ─────────────────────────────────────

# Removidas as rotas específicas solicitadas e as referências órfãs associadas a elas.
# Mantidas somente as rotas reais do módulo de produção que continuam ativas.


def _gerar_numero_op():
    """Gera próximo número de OP sequencial."""
    # ultimo = OrdemProducao.query.order_by(OrdemProducao.id.desc()).first()
    # seq = (ultimo.id + 1) if ultimo else 1
    # return f'OP-{date.today().year}-{seq:04d}'
    return f'OP-{date.today().year}-0001'


def _gerar_lote():
    d = date.today()
    return f'LOT-{d.year}-{d.month:02d}-{d.day:02d}'


def _get_produtos():
    """Lista de produtos do catálogo para o datalist."""
    return [
        {'id': 1, 'nome': 'CAMISA PIQUET ALGODÃO',     'referencia': 'CAM-001', 'sku': 'SKU-101'},
        {'id': 2, 'nome': 'CALÇA JEANS SLIM FIT',       'referencia': 'CAL-045', 'sku': 'SKU-202'},
        {'id': 3, 'nome': 'VESTIDO ESTAMPADO FLORAL',   'referencia': 'VES-012', 'sku': 'SKU-303'},
        {'id': 4, 'nome': 'BERMUDA TACTEL MASCULINA',   'referencia': 'BER-007', 'sku': 'SKU-404'},
    ]


def _get_status_lista():
    return [
        {'nome': 'PLANEJADA',    'cor': '#E67E22'},
        {'nome': 'CONFIRMADA',   'cor': '#27AE60'},
        {'nome': 'EM PRODUCAO',  'cor': '#2980B9'},
        {'nome': 'FINALIZADA',   'cor': '#16A085'},
        {'nome': 'CANCELADA',    'cor': '#E74C3C'},
    ]