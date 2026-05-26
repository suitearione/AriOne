from app import db
from models.estoque import Produto, MovimentacaoEstoque, OrdemProducao, ItemOrdemProducao
from app.models.catalogos import ProdutoComposicao
from decimal import Decimal, ROUND_HALF_UP

def registrar_retorno_oficina(op_id, local_oficina_id, custo_servico_oficina=0.0, local_central_id=1, usuario_id=None):
    """
    Processa o retorno da oficina:
    1. Baixa a Matéria-Prima (MP) do estoque da Oficina.
    2. Dá entrada no Produto Acabado (PA) no estoque Central.
    3. Calcula o custo unitário do PA baseado em MP + Serviço.
    """
    try:
        op = OrdemProducao.query.get(op_id)
        if not op:
            return False, "Ordem de Produção não encontrada."

        total_custo_materiais = Decimal('0.0')
        custo_servico_oficina = Decimal(str(custo_servico_oficina))

        # --- PASSO 1: BAIXA DAS MATÉRIAS-PRIMAS (CONSUMO) ---
        for item in op.materiais:
            mp = Produto.query.get(item.produto_mp_id)
            qtd_consumo = item.quantidade_real_consumida or item.quantidade_estimada
            
            # Acumula o custo das matérias-primas (Qtd Real * Custo Médio da MP)
            total_custo_materiais += Decimal(str(qtd_consumo)) * Decimal(str(mp.custo_medio))

            # Atualiza o saldo físico (considerando que o saldo estava na oficina)
            mp.saldo_fisico -= qtd_consumo
            
            # Registra o log de saída por consumo
            mov_saida = MovimentacaoEstoque(
                produto_id=mp.id,
                local_id=local_oficina_id,
                quantidade=qtd_consumo * -1,
                tipo_operacao='CONSUMO_RETORNO_OFICINA',
                documento_origem=f"OP-{op.id}",
                usuario_id=usuario_id # Cumpre PAA-DATA v2.0 Item 4
            )
            db.session.add(mov_saida)

        # --- PASSO 2: ENTRADA DO PRODUTO ACABADO (PRODUÇÃO) ---
        pa = Produto.query.get(op.produto_pa_id)
        
        # Cálculo do custo total desta produção (MP + Mão de Obra)
        total_custo_producao = total_custo_materiais + custo_servico_oficina
        
        # Atualização do Custo Médio do PA (Regra de Custo Médio Ponderado AriOne)
        saldo_anterior = Decimal(str(pa.saldo_fisico))
        custo_anterior = Decimal(str(pa.custo_medio))
        
        # Prioriza a quantidade real produzida, caso exista, senão usa a planejada
        qtd_nova = Decimal(str(op.quantidade_real_produzida)) if op.quantidade_real_produzida is not None else Decimal(str(op.quantidade_planejada))

        if (saldo_anterior + qtd_nova) > 0:
            novo_custo_medio = ((saldo_anterior * custo_anterior) + total_custo_producao) / (saldo_anterior + qtd_nova)
            # Garante precisão centesimal conforme PAA-DATA 2.1
            pa.custo_medio = novo_custo_medio.quantize(Decimal('0.00'), rounding=ROUND_HALF_UP)

        pa.saldo_fisico += qtd_nova # Adiciona a quantidade real produzida ao saldo
        
        # Registra o log de entrada do novo produto
        mov_entrada = MovimentacaoEstoque(
            produto_id=pa.id,
            local_id=local_central_id,
            quantidade=qtd_nova, # Registra a quantidade real produzida
            tipo_operacao='ENTRADA_PRODUTO_ACABADO',
            documento_origem=f"OP-{op.id}",
            usuario_id=usuario_id # Cumpre PAA-DATA v2.0 Item 4
        )
        db.session.add(mov_entrada)

        # --- PASSO 3: FINALIZAÇÃO ---
        op.status = 'CONCLUIDA'
        
        # Persiste todas as alterações de uma vez (Atomicidade)
        db.session.commit()
        return True, "Retorno de oficina processado com sucesso."

    except Exception as e:
        db.session.rollback()
        return False, f"Erro ao processar retorno: {str(e)}"

def informar_quantidade_produzida(op_id, quantidade_real):
    """
    Interface para registrar a quantidade exata que a oficina entregou.
    Isso deve ser feito antes de chamar registrar_retorno_oficina.
    """
    try:
        op = OrdemProducao.query.get(op_id)
        if not op:
            return False, "Ordem de Produção não encontrada."

        if op.status == 'CONCLUIDA':
            return False, "Não é possível alterar a quantidade de uma OP já concluída."

        # Garantimos que o valor seja tratado como Decimal para o banco
        op.quantidade_real_produzida = Decimal(str(quantidade_real))
        
        db.session.commit()
        return True, f"Quantidade real da OP {op_id} atualizada para {quantidade_real}."

    except Exception as e:
        db.session.rollback()
        return False, f"Erro ao atualizar quantidade real: {str(e)}"

def informar_consumo_real_materia_prima(op_id, produto_mp_id, quantidade_real_consumida):
    """
    Interface para registrar a quantidade real consumida de uma matéria-prima
    em uma Ordem de Produção específica.
    Isso deve ser feito antes de chamar registrar_retorno_oficina.
    """
    try:
        op = OrdemProducao.query.get(op_id)
        if not op:
            return False, "Ordem de Produção não encontrada."

        if op.status == 'CONCLUIDA':
            return False, "Não é possível alterar o consumo de uma OP já concluída."

        item_op = ItemOrdemProducao.query.filter_by(op_id=op_id, produto_mp_id=produto_mp_id).first()
        if not item_op:
            return False, f"Matéria-prima (ID: {produto_mp_id}) não encontrada para a OP (ID: {op_id})."

        # Garantimos que o valor seja tratado como Decimal para o banco
        item_op.quantidade_real_consumida = Decimal(str(quantidade_real_consumida))

        db.session.commit()
        return True, f"Consumo real da MP {produto_mp_id} na OP {op_id} atualizado para {quantidade_real_consumida}."

    except Exception as e:
        db.session.rollback()
        return False, f"Erro ao atualizar consumo real da matéria-prima: {str(e)}"

def ler_composicao_produto(produto_id, variacao_id=None):
    """
    Lê a composição de um produto usando o novo modelo ProdutoComposicao.
    Retorna lista de dicionários com os itens da composição.
    """
    try:
        query = ProdutoComposicao.query.filter_by(produto_id=produto_id)

        # Se variacao_id for fornecido, busca composição específica da variação
        # Senão, busca composição geral (variacao_id IS NULL)
        if variacao_id is not None:
            query = query.filter_by(variacao_id=variacao_id)
        else:
            query = query.filter(ProdutoComposicao.variacao_id.is_(None))

        itens = query.all()

        composicao = []
        for item in itens:
            composicao.append({
                'tipo_componente': item.tipo_componente,
                'item_id': item.item_id,
                'nome': item.nome,
                'unidade': item.unidade,
                'custo_unitario': float(item.custo_unitario or 0),
                'quantidade': float(item.quantidade or 1.0),
                'total_custo': float(item.total_custo or 0)
            })

        return True, composicao

    except Exception as e:
        return False, f"Erro ao ler composição: {str(e)}"

def baixar_insumos_composicao(produto_id, quantidade_produzida, local_estoque_id, variacao_id=None, usuario_id=None, documento_origem=None):
    """
    Baixa os insumos do estoque baseado na composição do produto.
    Esta função deve ser chamada ao iniciar a produção de um produto.

    Args:
        produto_id: ID do produto a ser produzido
        quantidade_produzida: Quantidade a ser produzida
        local_estoque_id: ID do local de estoque para baixa
        variacao_id: ID da variação (opcional, para produtos com grade)
        usuario_id: ID do usuário que está realizando a operação
        documento_origem: Documento de origem (ex: OP-123)

    Returns:
        (sucesso, mensagem)
    """
    try:
        # Lê a composição do produto
        sucesso, composicao = ler_composicao_produto(produto_id, variacao_id)
        if not sucesso:
            return False, f"Erro ao ler composição: {composicao}"

        if not composicao:
            return False, "Produto não possui composição definida."

        total_custo_insumos = Decimal('0.0')
        itens_baixados = []

        for item in composicao:
            # Calcula quantidade total a baixar (quantidade na composição * quantidade produzida)
            qtd_baixa = Decimal(str(item['quantidade'])) * Decimal(str(quantidade_produzida))

            # Busca o produto insumo no catálogo
            # Nota: item['item_id'] pode não corresponder diretamente a Produto.id
            # Precisamos buscar pelo nome ou criar um mapeamento
            from app.models.catalogos import Produto as CatalogoProduto
            insumo = CatalogoProduto.query.filter_by(descricao=item['nome']).first()

            if not insumo:
                # Se não encontrar pelo nome, tenta pelo item_id se for um produto do catálogo
                insumo = CatalogoProduto.query.get(item['item_id'])

            if not insumo:
                return False, f"Insumo não encontrado: {item['nome']}"

            # Verifica se há estoque suficiente
            if insumo.estoque_atual < float(qtd_baixa):
                return False, f"Estoque insuficiente para {item['nome']}. Disponível: {insumo.estoque_atual}, Necessário: {qtd_baixa}"

            # Baixa do estoque
            insumo.estoque_atual -= float(qtd_baixa)

            # Registra movimentação de saída
            mov_saida = MovimentacaoEstoque(
                produto_id=insumo.id,
                local_id=local_estoque_id,
                quantidade=float(qtd_baixa) * -1,
                tipo_operacao='CONSUMO_PRODUCAO',
                documento_origem=documento_origem or f"PROD-{produto_id}",
                usuario_id=usuario_id
            )
            db.session.add(mov_saida)

            # Acumula custo
            custo_item = Decimal(str(item['custo_unitario'])) * qtd_baixa
            total_custo_insumos += custo_item

            itens_baixados.append({
                'nome': item['nome'],
                'quantidade': float(qtd_baixa),
                'custo': float(custo_item)
            })

        db.session.commit()

        return True, {
            'mensagem': f"Baixa de {len(itens_baixados)} insumos realizada com sucesso.",
            'custo_total': float(total_custo_insumos),
            'itens': itens_baixados
        }

    except Exception as e:
        db.session.rollback()
        return False, f"Erro ao baixar insumos: {str(e)}"