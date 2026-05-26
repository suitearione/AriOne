# app/routes/fiscal.py
from flask import Blueprint, render_template, request
from flask_login import login_required

fiscal_bp = Blueprint("fiscal", __name__, url_prefix="/fiscal")

@fiscal_bp.route("/")
@login_required
def abas():
    abas = [
        {"id": "contabilidade", "label": "Contabilidade", "icon": "fas fa-calculator"},
        {"id": "fiscal",        "label": "Fiscal",        "icon": "fas fa-gavel"},
        {"id": "tributacao",    "label": "Tributação",    "icon": "fas fa-percent"},
    ]
    aba_ativa = request.args.get("aba", "contabilidade")
    if aba_ativa not in [a["id"] for a in abas]:
        aba_ativa = "contabilidade"

    return render_template(
        "fiscal/abas_fiscal.html",
        abas=abas,
        aba_ativa=aba_ativa
    )

@fiscal_bp.route("/card/gateway/modulos")
@login_required
def gateway_modulos_fiscal():
    return render_template('fiscal/cards/form_gateway_modulos_fiscal.html')

@fiscal_bp.route("/cards/relatorios")
@login_required
def card_fiscal_gateway_relatorios():
    modulo = request.args.get('modulo', 'contabilidade')
    titulos = {
        'contabilidade': 'Relatórios Contábeis',
        'fiscal': 'Escrituração Fiscal',
        'tributacao': 'Planejamento Tributário'
    }
    cores = {
        'contabilidade': '#2C3E50',
        'fiscal': '#C0392B',
        'tributacao': '#F39C12'
    }
    return render_template('fiscal/cards/form_fiscal_relatorios.html', 
                            titulo=titulos.get(modulo, 'Relatórios Fiscais'), 
                            cor=cores.get(modulo, '#2C3E50'), 
                            modulo=modulo)