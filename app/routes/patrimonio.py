# app/routes/patrimonio.py
from flask import Blueprint, render_template, request
from flask_login import login_required

patrimonio_bp = Blueprint("patrimonio", __name__, url_prefix="/patrimonio")

@patrimonio_bp.route("/")
@login_required
def abas():
    abas = [
        {"id": "imoveis",      "label": "Imóveis",      "icon": "fas fa-city"},
        {"id": "maquinas",     "label": "Máquinas",     "icon": "fas fa-tools"},
        {"id": "equipamentos", "label": "Equipamentos", "icon": "fas fa-microchip"},
        {"id": "veiculos",     "label": "Veículos",     "icon": "fas fa-car"},
        {"id": "software",     "label": "Softwares",    "icon": "fas fa-laptop-code"},
        {"id": "moveis",       "label": "Móveis & Objetos", "icon": "fas fa-couch"},
    ]
    aba_ativa = request.args.get("aba", "imoveis")
    if aba_ativa not in [a["id"] for a in abas]:
        aba_ativa = "imoveis"

    return render_template(
        "patrimonio/abas_patrimonio.html",
        abas=abas,
        aba_ativa=aba_ativa
    )

@patrimonio_bp.route("/card/gateway/modulos")
@login_required
def gateway_modulos_patrimonio():
    return render_template('patrimonio/cards/form_gateway_modulos_patrimonio.html')

import json
from flask import jsonify
from app import db
from datetime import datetime

@patrimonio_bp.route("/cards/ativos/relatorios")
@login_required
def card_ativos_relatorios():
    # Rota genérica para relatórios de patrimônio
    modulo = request.args.get('modulo', 'imoveis')
    titulos = {
        'imoveis': 'Gestão de Imóveis',
        'maquinas': 'Ativos Industriais',
        'equipamentos': 'Inventário de TI/Equip',
        'veiculos': 'Gestão de Frota',
        'software': 'Ativos Digitais',
        'moveis': 'Mobiliário e Eletrônicos'
    }
    return render_template('patrimonio/cards/form_patrimonio_relatorios.html', 
                           titulo=titulos.get(modulo, 'Relatórios de Ativos'), 
                           cor='#7F8C8D', 
                           modulo=modulo)

@patrimonio_bp.route("/api/ativos/salvar", methods=["POST"])
@login_required
def salvar_ativo():
    from app.models.gestao.patrimonio import Patrimonio
    from flask import session
    e_id = session.get('empresa_id')
    data = request.json
    try:
        pid = data.get('id')
        categoria = data.get('categoria', 'OUTROS').upper()
        
        if pid and str(pid).isdigit():
            ativo = Patrimonio.query.get(pid)
        else:
            ativo = Patrimonio(empresa_id=e_id)
            
        ativo.categoria = categoria
        ativo.descricao = data.get('descricao', '').upper()
        
        ativo.tag_patrimonial = data.get('tag_patrimonial') or data.get('placa') or data.get('matricula') or f"PAT-{int(datetime.utcnow().timestamp())}"
        ativo.valor_aquisicao = float(data.get('valor_aquisicao') or 0)
        
        data_aq = data.get('data_aquisicao')
        if data_aq:
            try:
                ativo.data_aquisicao = datetime.strptime(data_aq, '%Y-%m-%d')
            except:
                pass
            
        ativo.status = data.get('status', 'ATIVO').upper()
        ativo.observacoes = data.get('observacoes', '').upper()
        
        # Salva o resto do payload flexível no JSON
        ativo.detalhes = json.dumps(data)
        
        db.session.add(ativo)
        db.session.commit()
        return jsonify({"success": True, "message": f"{categoria} salvo com sucesso!", "id": ativo.id})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500

@patrimonio_bp.route("/api/ativos/listar", methods=["GET"])
@login_required
def listar_ativos():
    from app.models.gestao.patrimonio import Patrimonio
    from flask import session
    e_id = session.get('empresa_id')
    categoria = request.args.get('categoria')
    
    query = Patrimonio.query.filter_by(empresa_id=e_id)
    if categoria:
        query = query.filter_by(categoria=categoria.upper())
        
    ativos = query.all()
    resultado = []
    for a in ativos:
        obj = {}
        if a.detalhes:
            try:
                obj = json.loads(a.detalhes)
            except:
                pass
        obj['id'] = a.id
        obj['descricao'] = a.descricao
        obj['valor_aquisicao'] = a.valor_aquisicao
        obj['status'] = a.status
        obj['valor_contabil_atual'] = a.valor_contabil_atual()
        resultado.append(obj)
        
    return jsonify(resultado)

@patrimonio_bp.route("/api/ativos/excluir/<int:id>", methods=["POST"])
@login_required
def excluir_ativo(id):
    from app.models.gestao.patrimonio import Patrimonio
    try:
        ativo = Patrimonio.query.get_or_404(id)
        db.session.delete(ativo)
        db.session.commit()
        return jsonify({"success": True, "message": "Excluído com sucesso!"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500

@patrimonio_bp.route("/api/ativos/alienar", methods=["POST"])
@login_required
def alienar_ativo():
    from app.models.gestao.patrimonio import Patrimonio
    from app.models.gestao.lancamento import Lancamento
    from flask import session
    
    e_id = session.get('empresa_id')
    u_id = session.get('user_id')
    data = request.json
    
    ativo_id = data.get('ativo_id')
    valor_venda = float(data.get('valor_venda') or 0)
    
    try:
        ativo = Patrimonio.query.get_or_404(ativo_id)
        
        novo_titulo = Lancamento(
            empresa_id=e_id,
            usuario_id=u_id,
            tipo='RECEITA',
            descricao=f"ALIENAÇÃO DE ATIVO: {ativo.descricao} ({ativo.tag_patrimonial})",
            valor=valor_venda,
            data_vencimento=datetime.utcnow(),
            data_competencia=datetime.utcnow(),
            data_lancamento=datetime.utcnow(),
            status='PENDENTE',
            observacoes=f"Venda do Ativo ID: {ativo.id}. Baixa Patrimonial."
        )
        db.session.add(novo_titulo)
        
        ativo.status = 'VENDIDO'
        ativo.observacoes = f"{ativo.observacoes or ''}\nAlienado por R$ {valor_venda:.2f} em {datetime.now().strftime('%d/%m/%Y')}."
        
        db.session.commit()
        return jsonify({"success": True, "message": "Alienação registrada! Título a receber gerado no Financeiro."})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500