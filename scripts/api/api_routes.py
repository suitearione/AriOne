from flask import request, jsonify
from functools import wraps
from app import app # Assumindo que 'app' é sua instância do Flask
from app.utils.producao_service import informar_consumo_real_materia_prima, informar_quantidade_produzida, registrar_retorno_oficina
from app.utils.vendas_service import confirmar_pedido_venda

# Token de exemplo para validação (Em produção, use variáveis de ambiente)
API_TOKEN = "Ar1On3_S3cur3_T0k3n_2024"

def requer_autorizacao(f):
    """
    Decorador para verificar o token de autorização no Header.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        # Verifica se o token existe e se segue o padrão 'Bearer <token>'
        if not token or token != f"Bearer {API_TOKEN}":
            return jsonify({"status": "erro", "mensagem": "Acesso negado: Token de autorização inválido ou ausente."}), 401
        
        return f(*args, **kwargs)
    return decorated_function

@app.route('/op/informar-consumo-mp', methods=['POST'])
@requer_autorizacao
def api_informar_consumo_mp():
    """
    Rota API para informar a quantidade real consumida de uma matéria-prima
    em uma Ordem de Produção.
    """
    dados = request.get_json()
    
    op_id = dados.get('op_id')
    produto_mp_id = dados.get('produto_mp_id')
    quantidade_real_consumida = dados.get('quantidade_real_consumida')

    if not all([op_id, produto_mp_id, quantidade_real_consumida]):
        return jsonify({"status": "erro", "mensagem": "Dados incompletos. op_id, produto_mp_id e quantidade_real_consumida são obrigatórios."}), 400

    sucesso, mensagem = informar_consumo_real_materia_prima(op_id, produto_mp_id, quantidade_real_consumida)

    if sucesso:
        return jsonify({"status": "sucesso", "mensagem": mensagem}), 200
    else:
        return jsonify({"status": "erro", "mensagem": mensagem}), 400

@app.route('/venda/confirmar', methods=['POST'])
@requer_autorizacao
def api_confirmar_venda():
    dados = request.get_json()
    pedido_id = dados.get('pedido_id')
    
    if not pedido_id:
        return jsonify({"status": "erro", "mensagem": "pedido_id é obrigatório."}), 400
        
    sucesso, mensagem = confirmar_pedido_venda(pedido_id)
    if sucesso:
        return jsonify({"status": "sucesso", "mensagem": mensagem}), 200
    return jsonify({"status": "erro", "mensagem": mensagem}), 400

@app.route('/op/registrar-retorno', methods=['POST'])
@requer_autorizacao
def api_registrar_retorno_oficina():
    """
    Rota API para processar o retorno efetivo da oficina.
    Executa as baixas de MP, entrada de PA e cálculo de custo médio.
    """
    dados = request.get_json()
    
    op_id = dados.get('op_id')
    local_oficina_id = dados.get('local_oficina_id')
    custo_servico = dados.get('custo_servico', 0.0) # Valor cobrado pela oficina
    local_central_id = dados.get('local_central_id', 1) # Destino do produto acabado

    if not op_id or not local_oficina_id:
        return jsonify({"status": "erro", "mensagem": "op_id e local_oficina_id são obrigatórios."}), 400

    sucesso, mensagem = registrar_retorno_oficina(
        op_id=op_id, 
        local_oficina_id=local_oficina_id, 
        custo_servico_oficina=custo_servico,
        local_central_id=local_central_id
    )

    if sucesso:
        return jsonify({"status": "sucesso", "mensagem": mensagem}), 200
    else:
        return jsonify({"status": "erro", "mensagem": mensagem}), 400

@app.route('/op/informar-producao', methods=['POST'])
@requer_autorizacao
def api_informar_quantidade_produzida():
    """
    Rota API para informar a quantidade real produzida de uma Ordem de Produção.
    """
    dados = request.get_json()
    
    op_id = dados.get('op_id')
    quantidade = dados.get('quantidade')

    if not all([op_id, quantidade]):
        return jsonify({"status": "erro", "mensagem": "Dados incompletos. op_id e quantidade são obrigatórios."}), 400

    sucesso, mensagem = informar_quantidade_produzida(op_id, quantidade)

    if sucesso:
        return jsonify({"status": "sucesso", "mensagem": mensagem}), 200
    else:
        return jsonify({"status": "erro", "mensagem": mensagem}), 400