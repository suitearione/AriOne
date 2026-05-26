# =============================================================================
# Caminho  : app/utils/helpers.py
# Arquivo  : helpers.py
# Função   : Funções auxiliares de lógica de negócio (AriOne Engine).
# Lógica   : Backward Scheduling e cálculos operacionais.
# =============================================================================

from datetime import timedelta, date
from app.models.operacoes.vendas import PedidoVenda

def calcular_cronograma(pedido_id):
    """
    Lógica de Backward Scheduling (Padrão PLM AriOne).
    Calcula datas retroativas a partir da data de entrega do pedido.
    """
    pedido = PedidoVenda.query.get(pedido_id)
    if not pedido or not pedido.data_entrega_prometida:
        return None

    # Lead Times Padrão (Em dias) - Em um cenário real, viriam do cadastro de produtos/fornecedores
    LEAD_TIME_PRODUCAO = 7
    LEAD_TIME_COMPRA = 5
    MARGEM_SEGURANCA = 2

    data_entrega = pedido.data_entrega_prometida
    
    # 1. Data de Término da Produção (Entrega - Margem)
    data_termino_prod = data_entrega - timedelta(days=MARGEM_SEGURANCA)
    
    # 2. Data de Início da Produção (Término - Lead Time Prod)
    data_inicio_prod = data_termino_prod - timedelta(days=LEAD_TIME_PRODUCAO)
    
    # 3. Data Limite de Compra (Início Prod - Lead Time Compra)
    data_limite_compra = data_inicio_prod - timedelta(days=LEAD_TIME_COMPRA)

    return {
        'pedido_id': pedido_id,
        'data_entrega': data_entrega,
        'ordem_producao': {
            'inicio': data_inicio_prod,
            'termino': data_termino_prod
        },
        'compra': {
            'limite': data_limite_compra
        }
    }

def parse_date(date_str):
    """Converte string YYYY-MM-DD em objeto date."""
    if not date_str: return None
    try:
        from datetime import datetime
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    except:
        return None

def parse_money(money_str):
    """Converte string 'R$ 1.234,56' ou '1234.56' em float."""
    if not money_str: return 0.0
    if isinstance(money_str, (int, float)): return float(money_str)
    
    s = str(money_str).replace('R$', '').replace('.', '').replace(',', '.').strip()
    try:
        return float(s)
    except:
        return 0.0
