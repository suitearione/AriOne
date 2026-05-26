# app/routes/relatorios.py
from flask import Blueprint, render_template, request

relatorios_bp = Blueprint("relatorios", __name__, url_prefix="/relatorios")

@relatorios_bp.route("/")
def abas():
    abas = [
        {"id": "gerencial",      "label": "Gerencial",      "icon": "insights"},
        {"id": "operacional",    "label": "Operacional",    "icon": "factory"},
        {"id": "administrativo", "label": "Administrativo", "icon": "admin_panel_settings"},
    ]
    aba_ativa = request.args.get("aba", "gerencial")
    if aba_ativa not in [a["id"] for a in abas]:
        aba_ativa = "gerencial"

    return render_template(
        "relatorios/abas_relatorios.html",
        abas=abas,
        aba_ativa=aba_ativa
    )