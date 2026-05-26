from app import db
from estoque import PedidoVenda, OrdemProducao, OrdemCompra, Produto, ItemOrdemProducao, FichaTecnica, FinanceiroLancamento, ParametroSistema
from decimal import Decimal
from datetime import datetime, timedelta

def confirmar_pedido_venda(pedido_id):
    """
    Ao confirmar a venda, gera as necessidades de suprimento (OP ou OC).
    """
    try:
        pedido = PedidoVenda.query.get(pedido_id)
        if not pedido or pedido.status != 'ORCAMENTO':
            return False, "Pedido inválido para confirmação."

        # Busca parâmetro de imagem
        param_imagem = ParametroSistema.query.filter_by(chave='usar_imagem_vendas').first()
        usar_imagem = param_imagem.valor.lower() == 'true' if param_imagem else False

        for item in pedido.itens:
            produto = Produto.query.get(item.produto_id)
            
            if produto.origem == 'P': # PRODUCAO
                nova_op = OrdemProducao(
                    produto_pa_id=produto.id,
                    quantidade_planejada=item.quantidade,
                    status='ABERTA'
                )
                db.session.add(nova_op)
                
                # Validação de Imagem (PAA-REQ-VENDAS)
                if usar_imagem and item.requer_imagem:
                    if not item.anexos:
                        return False, f"O item {produto.descricao} requer imagens de personalização (Frente/Costa)."

                # Busca a Ficha Técnica do produto para explodir os materiais
                ficha = FichaTecnica.query.filter_by(produto_pa_id=produto.id).all()
                for comp in ficha:
                    item_consumo = ItemOrdemProducao(
                        op=nova_op,
                        produto_mp_id=comp.produto_mp_id,
                        quantidade_estimada=comp.quantidade_necessaria * item.quantidade
                    )
                    db.session.add(item_consumo)

            elif produto.origem == 'C': # COMPRA / REVENDA
                nova_oc = OrdemCompra(
                    produto_id=produto.id,
                    quantidade=item.quantidade,
                    status='ABERTA',
                    pedido_origem_id=pedido.id
                )
                db.session.add(nova_oc)

        # --- INTEGRAÇÃO FINANCEIRA ---
        novo_lancamento = FinanceiroLancamento(
            pedido_id=pedido.id,
            tipo='R', # Contas a Receber
            valor=pedido.total_liquido or pedido.valor_total,
            data_vencimento=(datetime.now() + timedelta(days=30)).date(),
            status='PENDENTE'
        )
        db.session.add(novo_lancamento)

        pedido.status = 'CONFIRMADO'
        db.session.commit()
        return True, "Pedido confirmado e suprimentos gerados com sucesso."

    except Exception as e:
        db.session.rollback()
        return False, f"Erro na confirmação logística: {str(e)}"