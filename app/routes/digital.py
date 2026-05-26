# app/routes/digital.py
from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from flask_login import login_required

digital_bp = Blueprint("digital", __name__, url_prefix="/digital")

@digital_bp.route("/")
@login_required
def abas():
    abas = [
        {"id": "linkone",    "label": "LinkOne",    "icon": "fas fa-link"},
        {"id": "leadone",    "label": "LeadOne",    "icon": "fas fa-filter"},
        {"id": "siteone",    "label": "SiteOne",    "icon": "fas fa-globe"},
        {"id": "chatone",    "label": "ChatOne",    "icon": "fas fa-comments"},
        {"id": "shopone",    "label": "ShopOne",    "icon": "fas fa-shopping-cart"},
        {"id": "metricsone", "label": "MetricsOne", "icon": "fas fa-chart-pie"},
    ]
    aba_ativa = request.args.get("aba", "linkone")
    if aba_ativa not in [a["id"] for a in abas]:
        aba_ativa = "linkone"

    return render_template(
        "digital/abas_digital.html",
        abas=abas,
        aba_ativa=aba_ativa
    )

@digital_bp.route("/card/gateway/modulos")
@login_required
def gateway_modulos_digital():
    return render_template('digital/cards/form_gateway_modulos_digital.html')

@digital_bp.route("/cards/digital/relatorios")
@login_required
def card_digital_relatorios():
    modulo = request.args.get('modulo', 'metricsone')
    return render_template('digital/cards/form_digital_relatorios.html', 
                           titulo='Analytics Digital', 
                           cor='#2980B9', 
                           modulo=modulo)

@digital_bp.route("/cards/chatone/canais", methods=['GET', 'POST'])
@login_required
def card_chatone_canais():
    from app.models.comercial.models import CanalVenda
    from app.extensions import db
    emp_id = session.get('empresa_id', 1)

    if request.method == 'POST':
        nome = request.form.get('nome_canal', '').strip().upper()
        tipo = request.form.get('tipo_canal', 'WhatsApp API')
        status = request.form.get('status', 'ATIVO')
        departamento = request.form.get('departamento', 'Suporte N1')
        identificador = request.form.get('identificador', '').strip()
        api_token = request.form.get('api_token', '').strip()
        webhook_url = request.form.get('webhook_url', '').strip()
        ativar_ia = request.form.get('ativar_ia', 'SIM')
        sla_minutos = int(request.form.get('sla_minutos', 15) or 15)
        mensagem_ausencia = request.form.get('mensagem_ausencia', '').strip()

        if not nome:
            flash('O Nome do Canal é obrigatório.', 'error')
            return redirect(url_for('digital.card_chatone_canais'))

        canal = CanalVenda.query.filter_by(nome=nome, empresa_id=emp_id).first()
        if canal:
            canal.tipo = tipo
            canal.status = status
            canal.departamento = departamento
            canal.identificador = identificador
            canal.api_token = api_token
            canal.webhook_url = webhook_url
            canal.ativar_ia = ativar_ia
            canal.sla_minutos = sla_minutos
            canal.mensagem_ausencia = mensagem_ausencia
            flash(f'Canal "{nome}" atualizado com sucesso no Padrão Ouro AriOne!', 'success')
        else:
            canal = CanalVenda(
                empresa_id=emp_id,
                nome=nome,
                tipo=tipo,
                status=status,
                departamento=departamento,
                identificador=identificador,
                api_token=api_token,
                webhook_url=webhook_url,
                ativar_ia=ativar_ia,
                sla_minutos=sla_minutos,
                mensagem_ausencia=mensagem_ausencia
            )
            db.session.add(canal)
            flash(f'Canal "{nome}" cadastrado com sucesso no Padrão Ouro AriOne!', 'success')
        
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao salvar: {str(e)}', 'danger')
            
        return redirect(url_for('digital.card_chatone_canais'))

    canais = CanalVenda.query.filter_by(empresa_id=emp_id).order_by(CanalVenda.nome).all()
    return render_template('digital/cards/form_chatone_canais.html', canais=canais)

@digital_bp.route("/cards/chatone/canais/delete/<nome>", methods=['POST'])
@login_required
def delete_chatone_canal(nome):
    from app.models.comercial.models import CanalVenda
    from app.extensions import db
    emp_id = session.get('empresa_id', 1)
    canal = CanalVenda.query.filter_by(nome=nome, empresa_id=emp_id).first()
    if canal:
        try:
            db.session.delete(canal)
            db.session.commit()
            flash(f'Canal "{nome}" removido com sucesso!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao remover: {str(e)}', 'danger')
    return redirect(url_for('digital.card_chatone_canais'))