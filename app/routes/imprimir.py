# app/routes/imprimir.py
from flask import Blueprint, render_template
from flask_login import login_required

imprimir_bp = Blueprint("imprimir", __name__, url_prefix="/imprimir")

@imprimir_bp.route("/")
@login_required
def index():
    modules = [
        {"id": "cadastros", "label": "CADASTROS", "icon": "fa-folder-open", "color": "#BDBDBD", "route": "cadastros.gateway_modulos_cadastro"},
        {"id": "operacoes", "label": "OPERAÇÕES", "icon": "fa-tasks", "color": "#03A9F4", "route": "operacoes.gateway_modulos_operacoes"},
        {"id": "financeiro", "label": "FINANCEIRO", "icon": "fa-wallet", "color": "#00E676", "route": "financeiro.gateway_modulos_financeiro"},
        {"id": "gestao", "label": "GESTÃO", "icon": "fa-chart-line", "color": "#CE93D8", "route": "gestao.gateway_modulos_gestao"},
        {"id": "fiscal", "label": "FISCAL", "icon": "fa-gavel", "color": "#FFB74D", "route": "fiscal.gateway_modulos_fiscal"},
        {"id": "patrimonio", "label": "PATRIMÔNIO", "icon": "fa-landmark", "color": "#BCAAA4", "route": "patrimonio.gateway_modulos_patrimonio"},
        {"id": "digital", "label": "DIGITAL", "icon": "fa-network-wired", "color": "#42A5F5", "route": "digital.gateway_modulos_digital"},
        {"id": "sistema", "label": "SISTEMA", "icon": "fa-cogs", "color": "#90A4AE", "route": "sistema.gateway_modulos_sistema"},
    ]
    return render_template("imprimir/index.html", modules=modules)
