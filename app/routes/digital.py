# app/routes/digital.py
from flask import Blueprint, render_template, request, flash, redirect, url_for, session, jsonify
from flask_login import login_required

digital_bp = Blueprint("digital", __name__, url_prefix="/digital")

@digital_bp.route("/")
@login_required
def abas():
    from app.models.digital.lead import Lead
    from app.models.digital.captura import Captura
    from app.models.digital.automacao import Automacao
    from app.models.digital.conversao import Conversao
    from app.models.digital.campanha import Campanha

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

    # Carregar dados se a aba ativa for LeadOne
    leads = None
    capturas = None
    automacoes = None
    conversoes = None
    campanhas = None

    if aba_ativa == "leadone":
        leads = Lead.query.order_by(Lead.nome.asc()).all()
        capturas = Captura.query.order_by(Captura.data_cadastro.desc()).all()
        automacoes = Automacao.query.order_by(Automacao.data_cadastro.desc()).all()
        conversoes = Conversao.query.order_by(Conversao.data_cadastro.desc()).all()
        campanhas = Campanha.query.order_by(Campanha.data_cadastro.desc()).all()

    return render_template(
        "digital/abas_digital.html",
        abas=abas,
        aba_ativa=aba_ativa,
        leads=leads,
        capturas=capturas,
        automacoes=automacoes,
        conversoes=conversoes,
        campanhas=campanhas
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

# ── LeadOne: Gestão de Leads ────────────────────────────────────────────────

@digital_bp.route("/leads", methods=['GET', 'POST'])
@login_required
def leads():
    from app.models.digital.lead import Lead
    from app.extensions import db

    if request.method == 'POST':
        lead_id = request.form.get('id')
        nome = request.form.get('nome', '').strip()
        email = request.form.get('email', '').strip()
        telefone = request.form.get('telefone', '').strip()
        etapa = request.form.get('etapa', 'Novo')
        origem = request.form.get('origem', '').strip()
        observacoes = request.form.get('observacoes', '').strip()

        if not nome:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'message': 'Nome do lead é obrigatório'}), 400
            flash('Nome do lead é obrigatório.', 'error')
            return redirect(url_for('digital.leads'))

        if lead_id:
            lead = Lead.query.get(lead_id)
            if lead:
                lead.nome = nome
                lead.email = email
                lead.telefone = telefone
                lead.etapa = etapa
                lead.origem = origem
                lead.observacoes = observacoes
                flash(f'Lead "{nome}" atualizado com sucesso!', 'success')
        else:
            lead = Lead(
                nome=nome,
                email=email,
                telefone=telefone,
                etapa=etapa,
                origem=origem,
                observacoes=observacoes
            )
            db.session.add(lead)
            flash(f'Lead "{nome}" cadastrado com sucesso!', 'success')

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'message': str(e)}), 500
            flash(f'Erro ao salvar: {str(e)}', 'danger')

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': True})
        return redirect(url_for('digital.leads'))

    leads = Lead.query.order_by(Lead.nome.asc()).all()
    return render_template('digital/cards/grid_leadone.html', leads=leads)

@digital_bp.route("/leads/<int:id>/delete", methods=['POST'])
@login_required
def delete_lead(id):
    from app.models.digital.lead import Lead
    from app.extensions import db
    lead = Lead.query.get_or_404(id)
    try:
        db.session.delete(lead)
        db.session.commit()
        flash(f'Lead "{lead.nome}" removido com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao remover: {str(e)}', 'danger')
    return redirect(url_for('digital.leads'))

@digital_bp.route("/leads/atualizar-etapa", methods=['POST'])
@login_required
def atualizar_etapa_lead():
    from app.models.digital.lead import Lead
    from app.extensions import db
    
    lead_id = request.json.get('lead_id')
    nova_etapa = request.json.get('etapa', 'Marcado')
    
    if not lead_id:
        return jsonify({'success': False, 'message': 'ID do lead não fornecido'}), 400
        
    lead = Lead.query.get(lead_id)
    if not lead:
        return jsonify({'success': False, 'message': 'Lead não encontrado'}), 404
        
    try:
        lead.etapa = nova_etapa
        db.session.commit()
        return jsonify({'success': True, 'message': 'Status atualizado com sucesso', 'lead_id': lead.id, 'etapa': lead.etapa})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@digital_bp.route("/leads/enviar-automacao", methods=['POST'])
@login_required
def enviar_automacao_leads():
    from app.models.digital.automacao import Automacao
    from app.extensions import db
    
    lead_ids = request.json.get('lead_ids', [])
    if not lead_ids:
        return jsonify({'success': False, 'message': 'Nenhum lead selecionado'}), 400
        
    try:
        automacao = Automacao(
            nome="FOLLOW-UP LEAD CAPTURADO",
            gatilho="Lead Contas Google e Cadastros",
            acao="Fazer Disparos WhatsApp",
            delay_horas=0
        )
        
        from app.models.digital.lead import Lead
        leads_selecionados = Lead.query.filter(Lead.id.in_(lead_ids)).all()
        for lead in leads_selecionados:
            automacao.leads.append(lead)
            
        db.session.add(automacao)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Automação criada com sucesso!'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@digital_bp.route("/automacoes/<int:id>/leads", methods=['GET'])
@login_required
def get_automacao_leads(id):
    from app.models.digital.automacao import Automacao
    automacao = Automacao.query.get_or_404(id)
    leads_data = []
    for lead in automacao.leads:
        leads_data.append({
            'id': lead.id,
            'nome': lead.nome,
            'telefone': lead.telefone or '-',
            'etapa': lead.etapa
        })
    return jsonify({'leads': leads_data})

@digital_bp.route("/leads/importar-csv", methods=['POST'])
@login_required
def importar_csv_leads():
    import csv
    import io
    from app.models.digital.lead import Lead
    from app.extensions import db

    arquivo = request.files.get('csv_file')
    if not arquivo or not arquivo.filename.endswith('.csv'):
        flash('Envie um arquivo CSV válido.', 'error')
        return redirect(url_for('digital.abas', aba='leadone'))

    try:
        conteudo = arquivo.stream.read().decode('utf-8-sig')
        leitor = csv.DictReader(io.StringIO(conteudo))

        importados = 0
        for row in leitor:
            # Google Contacts CSV: "First Name", "Last Name", "Phone 1 - Value", "E-mail 1 - Value"
            # Também suporta: "Nome", "Telefone", "Email" (formato simplificado)
            nome = ''
            telefone = ''
            email = ''

            # Formato Google Contacts
            first = row.get('First Name', row.get('Given Name', '')).strip()
            last = row.get('Last Name', row.get('Family Name', '')).strip()
            if first or last:
                nome = f'{first} {last}'.strip()

            # Formato simplificado (Nome direto)
            if not nome:
                nome = row.get('Nome', row.get('Name', row.get('name', ''))).strip()

            # Telefone - tenta múltiplas colunas
            telefone = (
                row.get('Phone 1 - Value', '') or
                row.get('Phone 1 - Value', '') or
                row.get('Mobile Phone', '') or
                row.get('Telefone', '') or
                row.get('phone', '') or
                row.get('Phone', '') or ''
            ).strip()

            # Email
            email = (
                row.get('E-mail 1 - Value', '') or
                row.get('Email', '') or
                row.get('email', '') or
                row.get('E-mail Address', '') or ''
            ).strip()

            # Só importa se tiver nome E telefone
            if nome and telefone:
                # Limpa telefone (remove espaços, parênteses, hifens)
                tel_limpo = ''.join(c for c in telefone if c.isdigit() or c == '+')
                if tel_limpo.startswith('+'):
                    tel_limpo = tel_limpo[1:]

                # Evita duplicidade: pula se telefone já existe
                existente = Lead.query.filter_by(telefone=tel_limpo).first()
                if existente:
                    continue

                lead = Lead(
                    nome=nome,
                    telefone=tel_limpo,
                    email=email,
                    etapa='Novo',
                    origem='CSV Google'
                )
                db.session.add(lead)
                importados += 1

        db.session.commit()

        # Registrar a importação como uma Captura no LeadOne
        if importados > 0:
            from app.models.digital.captura import Captura
            from datetime import datetime

            # Usa nome personalizado do form ou gera nome padrão
            nome_captura = request.form.get('nome_captura', '').strip()
            if not nome_captura:
                nome_captura = f'Importação CSV — {importados} contatos'

            # Evita captura duplicada para o mesmo arquivo
            ja_existe = Captura.query.filter_by(nome=nome_captura, integracao='CSV Import').first()
            if not ja_existe:
                captura = Captura(
                    nome=nome_captura,
                    campos=f'{importados} contatos importados do arquivo: {arquivo.filename}',
                    destino='Pipeline',
                    integracao='CSV Import'
                )
                captura.gerar_slug()
                db.session.add(captura)
                db.session.commit()

        flash(f'{importados} contatos importados com sucesso!', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao importar CSV: {str(e)}', 'danger')

    return redirect(url_for('digital.abas', aba='leadone'))

# ── LeadOne: Gestão de Capturas ────────────────────────────────────────────

@digital_bp.route("/capturas", methods=['GET', 'POST'])
@login_required
def capturas():
    from app.models.digital.captura import Captura
    from app.extensions import db

    if request.method == 'POST':
        captura_id = request.form.get('id')
        nome = request.form.get('nome', '').strip()
        campos = request.form.get('campos', '').strip()
        destino = request.form.get('destino', '').strip()
        integracao = request.form.get('integracao', '').strip()

        if not nome:
            flash('Nome da captura é obrigatório.', 'error')
            return redirect(url_for('digital.capturas'))

        if captura_id:
            captura = Captura.query.get(captura_id)
            if captura:
                captura.nome = nome
                captura.campos = campos
                captura.destino = destino
                captura.integracao = integracao
                captura.gerar_slug()
                flash(f'Captura "{nome}" atualizada com sucesso!', 'success')
        else:
            captura = Captura(
                nome=nome,
                campos=campos,
                destino=destino,
                integracao=integracao
            )
            captura.gerar_slug()
            db.session.add(captura)
            flash(f'Captura "{nome}" cadastrada com sucesso!', 'success')

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao salvar: {str(e)}', 'danger')

        return redirect(url_for('digital.capturas'))

    capturas = Captura.query.order_by(Captura.data_cadastro.desc()).all()
    return render_template('digital/cards/grid_leadone.html', capturas=capturas)

@digital_bp.route("/capturas/<int:id>/delete", methods=['POST'])
@login_required
def delete_captura(id):
    from app.models.digital.captura import Captura
    from app.extensions import db
    captura = Captura.query.get_or_404(id)
    try:
        db.session.delete(captura)
        db.session.commit()
        flash(f'Captura "{captura.nome}" removida com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao remover: {str(e)}', 'danger')
    return redirect(url_for('digital.capturas'))

# ── LeadOne: Gestão de Automações ──────────────────────────────────────────

@digital_bp.route("/automacoes", methods=['GET', 'POST'])
@login_required
def automacoes():
    from app.models.digital.automacao import Automacao
    from app.extensions import db

    if request.method == 'POST':
        automacao_id = request.form.get('id')
        nome = request.form.get('nome', '').strip()
        gatilho = request.form.get('gatilho', '').strip()
        acao = request.form.get('acao', '').strip()
        delay_horas = request.form.get('delay', 0)

        if not nome:
            flash('Nome da automação é obrigatório.', 'error')
            return redirect(url_for('digital.automacoes'))

        if automacao_id:
            automacao = Automacao.query.get(automacao_id)
            if automacao:
                automacao.nome = nome
                automacao.gatilho = gatilho
                automacao.acao = acao
                automacao.delay_horas = int(delay_horas) if delay_horas else 0
                flash(f'Automação "{nome}" atualizada com sucesso!', 'success')
        else:
            automacao = Automacao(
                nome=nome,
                gatilho=gatilho,
                acao=acao,
                delay_horas=int(delay_horas) if delay_horas else 0
            )
            db.session.add(automacao)
            flash(f'Automação "{nome}" cadastrada com sucesso!', 'success')

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao salvar: {str(e)}', 'danger')

        return redirect(url_for('digital.automacoes'))

    automacoes = Automacao.query.order_by(Automacao.data_cadastro.desc()).all()
    return render_template('digital/cards/grid_leadone.html', automacoes=automacoes)

@digital_bp.route("/automacoes/<int:id>/delete", methods=['POST'])
@login_required
def delete_automacao(id):
    from app.models.digital.automacao import Automacao
    from app.extensions import db
    automacao = Automacao.query.get_or_404(id)
    try:
        db.session.delete(automacao)
        db.session.commit()
        flash(f'Automação "{automacao.nome}" removida com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao remover: {str(e)}', 'danger')
    return redirect(url_for('digital.automacoes'))

# ── LeadOne: Gestão de Conversões ───────────────────────────────────────────

@digital_bp.route("/conversoes", methods=['GET', 'POST'])
@login_required
def conversoes():
    from app.models.digital.conversao import Conversao
    from app.extensions import db

    if request.method == 'POST':
        conversao_id = request.form.get('id')
        lead = request.form.get('lead', '').strip()
        data_conversao = request.form.get('data')
        valor = request.form.get('valor', 0)
        responsavel = request.form.get('resp', '').strip()

        if not lead:
            flash('Nome do lead é obrigatório.', 'error')
            return redirect(url_for('digital.conversoes'))

        if conversao_id:
            conversao = Conversao.query.get(conversao_id)
            if conversao:
                conversao.lead = lead
                conversao.data_conversao = datetime.strptime(data_conversao, '%Y-%m-%d').date() if data_conversao else None
                conversao.valor = float(valor) if valor else 0.0
                conversao.responsavel = responsavel
                flash(f'Conversão atualizada com sucesso!', 'success')
        else:
            conversao = Conversao(
                lead=lead,
                data_conversao=datetime.strptime(data_conversao, '%Y-%m-%d').date() if data_conversao else None,
                valor=float(valor) if valor else 0.0,
                responsavel=responsavel
            )
            db.session.add(conversao)
            flash(f'Conversão cadastrada com sucesso!', 'success')

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao salvar: {str(e)}', 'danger')

        return redirect(url_for('digital.conversoes'))

    conversoes = Conversao.query.order_by(Conversao.data_cadastro.desc()).all()
    return render_template('digital/cards/grid_leadone.html', conversoes=conversoes)

@digital_bp.route("/conversoes/<int:id>/delete", methods=['POST'])
@login_required
def delete_conversao(id):
    from app.models.digital.conversao import Conversao
    from app.extensions import db
    conversao = Conversao.query.get_or_404(id)
    try:
        db.session.delete(conversao)
        db.session.commit()
        flash(f'Conversão removida com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao remover: {str(e)}', 'danger')
    return redirect(url_for('digital.conversoes'))

# ══════════════════════════════════════════════════════════════════════════════
# ROTA PÚBLICA: Formulário de Captura (SEM LOGIN)
# Link compartilhável: /digital/f/<slug>
# ══════════════════════════════════════════════════════════════════════════════

@digital_bp.route("/f/<slug>", methods=['GET', 'POST'])
def form_publico_captura(slug):
    from app.models.digital.captura import Captura
    from app.models.digital.lead import Lead
    from app.extensions import db

    captura = Captura.query.filter_by(slug=slug, ativo=True).first_or_404()

    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        telefone = request.form.get('telefone', '').strip()
        email = request.form.get('email', '').strip()

        if nome and telefone:
            lead = Lead(
                nome=nome,
                telefone=telefone,
                email=email,
                etapa='Novo',
                origem=captura.nome
            )
            db.session.add(lead)
            try:
                db.session.commit()
            except Exception:
                db.session.rollback()

        return render_template('digital/publico/form_captura.html', captura=captura, sucesso=True)

    return render_template('digital/publico/form_captura.html', captura=captura, sucesso=False)

# ── LeadOne: Importar Clientes do Cadastro ──────────────────────────────────────

@digital_bp.route("/leads/clientes-disponiveis", methods=['GET'])
@login_required
def clientes_disponiveis():
    """Retorna lista de clientes do cadastro que ainda não estão no pipeline LeadOne"""
    from app.models.cadastros.cliente import Cliente
    from app.models.digital.lead import Lead
    from app.extensions import db

    # Busca todos os clientes ativos
    clientes = Cliente.query.filter_by(ativo=True).order_by(Cliente.nome).all()

    # Busca telefones já existentes no LeadOne
    leads_existentes = Lead.query.with_entities(Lead.telefone).all()
    telefones_leads = {l[0] for l in leads_existentes if l[0]}

    # Monta lista de clientes disponíveis (não duplicados por telefone)
    clientes_disponiveis = []
    for cliente in clientes:
        telefone = cliente.whatsapp or cliente.telefone
        if telefone and telefone not in telefones_leads:
            clientes_disponiveis.append({
                'id': cliente.id,
                'nome': cliente.nome,
                'email': cliente.email or '',
                'telefone': telefone,
                'origem': cliente.origem or 'Cadastro de Cliente'
            })

    return jsonify({'clientes': clientes_disponiveis})

@digital_bp.route("/leads/importar-clientes", methods=['POST'])
@login_required
def importar_clientes():
    """Importa clientes selecionados do cadastro para o pipeline LeadOne"""
    from app.models.cadastros.cliente import Cliente
    from app.models.digital.lead import Lead
    from app.extensions import db

    cliente_ids = request.json.get('cliente_ids', [])
    if not cliente_ids:
        return jsonify({'success': False, 'message': 'Nenhum cliente selecionado'}), 400

    importados = 0
    erros = []

    for cliente_id in cliente_ids:
        try:
            cliente = Cliente.query.get(cliente_id)
            if not cliente:
                erros.append(f'Cliente ID {cliente_id} não encontrado')
                continue

            telefone = cliente.whatsapp or cliente.telefone
            if not telefone:
                erros.append(f'Cliente {cliente.nome} não possui telefone')
                continue

            # Verifica duplicidade
            existente = Lead.query.filter_by(telefone=telefone).first()
            if existente:
                erros.append(f'Cliente {cliente.nome} já existe no pipeline')
                continue

            lead = Lead(
                nome=cliente.nome,
                email=cliente.email,
                telefone=telefone,
                etapa='Contato Feito',
                origem=cliente.origem or 'Cadastro de Cliente',
                observacoes=f'Cliente importado do Cadastro (ID: {cliente.id})'
            )
            db.session.add(lead)
            importados += 1

        except Exception as e:
            erros.append(f'Erro ao importar cliente {cliente_id}: {str(e)}')

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Erro ao salvar: {str(e)}'}), 500

    mensagem = f'{importados} cliente(s) importado(s) com sucesso!'
    if erros:
        mensagem += f' {len(erros)} erro(s): ' + '; '.join(erros[:3])

    return jsonify({'success': True, 'message': mensagem, 'importados': importados})


# ── LeadOne: Gestão de Campanhas ───────────────────────────────────────────

@digital_bp.route("/campanhas", methods=['GET', 'POST'])
@login_required
def campanhas():
    from app.models.digital.campanha import Campanha
    from app.models.comercial.models import Vendedor
    from app.extensions import db

    if request.method == 'POST':
        campanha_id = request.form.get('id')
        nome_campanha = request.form.get('nome_campanha', '').strip()
        identificador_webhook = request.form.get('identificador_webhook', '').strip()
        status = request.form.get('status', '1') == '1'
        vendedor_id = request.form.get('vendedor_id')
        investimento_estimado = request.form.get('investimento_estimado', 0)
        data_inicio = request.form.get('data_inicio')

        if not nome_campanha:
            flash('Nome da campanha é obrigatório.', 'error')
            return redirect(url_for('digital.campanhas'))
        if not identificador_webhook:
            flash('Identificador Webhook é obrigatório.', 'error')
            return redirect(url_for('digital.campanhas'))

        if campanha_id:
            camp = Campanha.query.get(campanha_id)
            if camp:
                camp.nome_campanha = nome_campanha
                camp.identificador_webhook = identificador_webhook
                camp.status = status
                camp.vendedor_id = vendedor_id if vendedor_id else None
                camp.investimento_estimado = float(investimento_estimado) if investimento_estimado else 0.0
                camp.data_inicio = datetime.strptime(data_inicio, '%Y-%m-%d').date() if data_inicio else None
                flash(f'Campanha "{nome_campanha}" atualizada com sucesso!', 'success')
        else:
            camp = Campanha(
                nome_campanha=nome_campanha,
                identificador_webhook=identificador_webhook,
                status=status,
                vendedor_id=vendedor_id if vendedor_id else None,
                investimento_estimado=float(investimento_estimado) if investimento_estimado else 0.0,
                data_inicio=datetime.strptime(data_inicio, '%Y-%m-%d').date() if data_inicio else None
            )
            db.session.add(camp)
            flash(f'Campanha "{nome_campanha}" cadastrada com sucesso!', 'success')

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao salvar: {str(e)}', 'danger')

        return redirect(url_for('digital.campanhas'))

    campanhas = Campanha.query.order_by(Campanha.data_cadastro.desc()).all()
    vendedores = Vendedor.query.filter_by(ativo=True).order_by(Vendedor.nome_exibivel.asc()).all()
    return render_template('digital/cards/form_campanha.html', campanhas=campanhas, vendedores=vendedores)

@digital_bp.route("/campanhas/<int:id>/delete", methods=['POST'])
@login_required
def delete_campanha(id):
    from app.models.digital.campanha import Campanha
    from app.extensions import db
    camp = Campanha.query.get_or_404(id)
    try:
        db.session.delete(camp)
        db.session.commit()
        flash(f'Campanha "{camp.nome_campanha}" removida com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao remover: {str(e)}', 'danger')
    return redirect(url_for('digital.campanhas'))

@digital_bp.route('/leadone/webhook/meta', methods=['POST'])
def webhook_meta_leadone():
    """
    Ponto de entrada de leads do Meta. 
    Lê o JSON, consulta a tabela de Campanhas e roteia o Lead.
    """
    from app.models.digital.campanha import Campanha
    try:
        dados_meta = request.json
        camp_webhook_id = dados_meta.get('campaign_id')

        config_campanha = Campanha.query.filter_by(
            identificador_webhook=camp_webhook_id, 
            status=True
        ).first()

        if not config_campanha:
            return jsonify({"msg": "Campanha não ativa ou não encontrada"}), 404

        novo_lead = {
            "nome": dados_meta.get('full_name'),
            "telefone": dados_meta.get('phone_number'),
            "vendedor_id": config_campanha.vendedor_id,
            "origem": config_campanha.nome_campanha,
            "etapa": "NOVO"
        }

        return jsonify({"msg": "Lead capturado com sucesso"}), 200

    except Exception as e:
        return jsonify({"erro": str(e)}), 500