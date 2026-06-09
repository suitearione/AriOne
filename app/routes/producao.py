# =============================================================================
#  Arquivo  : routes_producao_op.py
#  Caminho  : app/operacoes/routes.py  (adicionar ao blueprint 'operacoes')
#  Função   : Rotas de Ordens de Produção (OP) — multi-produto
#             Gerada automaticamente ao confirmar Pedido de Vendas.
# =============================================================================

from flask import Blueprint, render_template, request, jsonify
from datetime import date

# ─── Rotas ────────────────────────────────────────────────────────────────────

@operacoes.route('/op/nova')
def form_producao_op():
    """
    Exibe formulário de nova OP vazia.
    GET /operacoes/op/nova?modal=1
    """
    modal = request.args.get('modal', 0, type=int)
    return render_template(
        'operacoes/cards/producao/form_producao_op.html',
        modal          = modal,
        op_numero      = _gerar_numero_op(),
        lote           = _gerar_lote(),
        today          = date.today().isoformat(),
        produtos       = _get_produtos(),
        status_lista   = _get_status_lista(),
        produtos_op    = [],
        pedido_origem  = None,
    )


@operacoes.route('/op/from-pedido/<int:pedido_id>')
def op_from_pedido(pedido_id):
    """
    Gera OP automaticamente a partir de um Pedido de Vendas confirmado.
    Chamado pelo endpoint de confirmação do pedido.

    GET /operacoes/op/from-pedido/<pedido_id>?modal=1
    """
    modal = request.args.get('modal', 0, type=int)

    # ── Buscar pedido ──────────────────────────────────────────────────────
    # pedido = PedidoVenda.query.get_or_404(pedido_id)
    pedido = _get_pedido_fake(pedido_id)          # ← substituir pela query real

    # ── Montar lista de produtos da OP a partir dos itens do pedido ────────
    # produtos_op = [
    #     {
    #         'nome':        item.produto.nome,
    #         'referencia':  item.produto.referencia,
    #         'cor':         item.cor or '',
    #         'tamanho':     item.tamanho or '',
    #         'quantidade':  item.quantidade,
    #         'und':         item.produto.unidade,
    #         'custo_unit':  item.produto.custo_producao or 0,
    #     }
    #     for item in pedido.itens
    # ]
    produtos_op = pedido.get('itens', [])

    return render_template(
        'operacoes/cards/producao/form_producao_op.html',
        modal         = modal,
        op_numero     = _gerar_numero_op(),
        lote          = _gerar_lote(),
        today         = date.today().isoformat(),
        produtos      = _get_produtos(),
        status_lista  = _get_status_lista(),
        produtos_op   = produtos_op,
        pedido_origem = pedido,
    )


@operacoes.route('/op/salvar', methods=['POST'])
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


@operacoes.route('/op/confirmar', methods=['POST'])
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


@operacoes.route('/op/imprimir/<string:op_numero>')
def imprimir_op(op_numero):
    """Página de impressão da OP."""
    # op = OrdemProducao.query.filter_by(numero=op_numero).first_or_404()
    op = {'numero': op_numero}
    return render_template('operacoes/cards/producao/impressao_op.html', op=op)


# =============================================================================
# INTEGRAÇÃO: chamar ao confirmar Pedido de Vendas
# =============================================================================
# No seu endpoint de confirmação de pedido, adicione:
#
#   from flask import redirect, url_for
#
#   @operacoes.route('/pedido/<int:pedido_id>/confirmar', methods=['POST'])
#   def confirmar_pedido(pedido_id):
#       pedido = PedidoVenda.query.get_or_404(pedido_id)
#       pedido.status = 'CONFIRMADO'
#       db.session.commit()
#
#       # ─── Gera OP automaticamente ───────────────────────────────────────
#       if pedido.gera_op:                         # flag no modelo do pedido
#           return redirect(url_for(
#               'operacoes.op_from_pedido',
#               pedido_id=pedido.id,
#               modal=1
#           ))
#
#       return redirect(url_for('operacoes.card_vendas_pedido'))
#
# =============================================================================


# ── Helpers (substituir por queries reais) ─────────────────────────────────────

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


def _get_pedido_fake(pedido_id):
    """Simula pedido de vendas. Substituir por PedidoVenda.query.get_or_404()."""
    return {
        'id':      pedido_id,
        'numero':  f'PED-2026-{pedido_id:03d}',
        'cliente': 'Comercial Silva Ltda',
        'data':    date.today().strftime('%d/%m/%Y'),
        'itens': [
            {'nome':'CAMISA PIQUET ALGODÃO',   'referencia':'CAM-001','cor':'Branco','tamanho':'M', 'quantidade':200,'und':'PC','custo_unit':28.50},
            {'nome':'CAMISA PIQUET ALGODÃO',   'referencia':'CAM-001','cor':'Azul',  'tamanho':'G', 'quantidade':150,'und':'PC','custo_unit':28.50},
            {'nome':'BERMUDA TACTEL MASCULINA','referencia':'BER-007','cor':'Preto', 'tamanho':'M', 'quantidade':100,'und':'PC','custo_unit':22.00},
        ]
    }