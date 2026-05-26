# =============================================================================
# Caminho  : app/routes/sistema.py
# Arquivo  : sistema.py
# Função   : Rotas do módulo Sistema (Versões, Configurações, etc).
# Descrição: Gerenciamento de versões do sistema, changelog, releases e
#            controle de ambientes (DEV/PROD). Em ambiente de desenvolvimento
#            permite criar, editar e excluir versões. Em produção exibe
#            apenas versão atual e histórico (somente leitura).
# =============================================================================

import os
from datetime import datetime, date
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app, jsonify
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename
import shutil
from sqlalchemy.exc import IntegrityError
from app.models.sistema.versao import Versao
from app.models.sistema.status import StatusWorkflow
from app.models.cadastros.empresa import Empresa
from app import db



# ── CONSTANTES DE SISTEMA ────────────────────────────────────────────────────
ARIONE_MODULOS = [
    {"id": "cadastros", "nome": "Cadastros", "icone": "fas fa-database", "cor": "#1e293b", "desc": "Pessoas, Produtos e Configurações"},
    {"id": "operacoes", "nome": "Operações", "icone": "fas fa-sync-alt", "cor": "#3498db", "desc": "Vendas, Compras e Estoque"},
    {"id": "financeiro", "nome": "Financeiro", "icone": "fas fa-wallet", "cor": "#27ae60", "desc": "Caixas, Bancos e Contas"},
    {"id": "gestao", "nome": "Gestão", "icone": "fas fa-user-tie", "cor": "#8e44ad", "desc": "HCM, CRM e Marketing"},
    {"id": "fiscal", "nome": "Fiscal", "icone": "fas fa-file-invoice-dollar", "cor": "#c0392b", "desc": "Escrita e Tributação"},
    {"id": "patrimonio", "nome": "Patrimônio", "icone": "fas fa-building", "cor": "#d35400", "desc": "Imóveis, Veículos e Ativos"},
    {"id": "digital", "nome": "Digital", "icone": "fas fa-globe", "cor": "#2980b9", "desc": "E-commerce e Presença Digital"},
    {"id": "sistema", "nome": "Sistema", "icone": "fas fa-cogs", "cor": "#7f8c8d", "desc": "Admin, Segurança e Dev"},
    {"id": "imprimir", "nome": "Imprimir", "icone": "fas fa-print", "cor": "#2c3e50", "desc": "Relatórios e Documentos"}
]
from app.utils.progress import get_standardization_progress, is_ari_dev
from app.utils.backup_manager import BackupManager

sistema_bp = Blueprint('sistema', __name__, url_prefix='/sistema')

@sistema_bp.route('/status/form', methods=['GET', 'POST'])
@sistema_bp.route('/status/form/<int:id>', methods=['GET', 'POST'])
@login_required
def form_status(id=None):
    status = StatusWorkflow.query.get(id) if id else None
    
    if request.method == 'POST':
        if not status:
            status = StatusWorkflow()
        
        status.nome = request.form.get('nome', '').upper()
        status.tipo = request.form.get('tipo', 'VENDAS').upper()
        status.cor = request.form.get('cor', '#2980B9')
        status.icone = request.form.get('icone', 'fas fa-circle')
        status.ordem = int(request.form.get('ordem', 0))
        status.ativa = 'ativa' in request.form
        
        try:
            db.session.add(status)
            db.session.commit()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': True, 'message': 'Status salvo com sucesso!'})
            flash('Status salvo com sucesso!', 'success')
            return redirect(url_for('sistema.abas', aba='administracao'))
        except Exception as e:
            db.session.rollback()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'message': str(e)}), 500
            flash(f'Erro ao salvar: {str(e)}', 'danger')

    status_lista = StatusWorkflow.query.order_by(StatusWorkflow.tipo, StatusWorkflow.ordem).all()
    is_modal = request.args.get('modal') == '1'
    
    return render_template('sistema/cards/administracao/form_status.html', 
                           status=status, status_lista=status_lista, is_modal=is_modal)

@sistema_bp.before_app_request
def setup_versoes():
    """Auto-migração para a tabela de versões."""
    from sqlalchemy import text
    try:
        with db.engine.begin() as conn:
            result = conn.execute(text("PRAGMA table_info(versoes)"))
            cols_existentes = [row[1] for row in result]
            if 'data_previsao' not in cols_existentes:
                try: conn.execute(text('ALTER TABLE versoes ADD COLUMN data_previsao DATETIME'))
                except: pass
    except:
        pass


# ══════════════════════════════════════════════════════════════════════════════
# Detecção de Ambiente
# ══════════════════════════════════════════════════════════════════════════════

def is_development():
    """Detecta se está em ambiente de desenvolvimento"""
    # Método 1: Variável de ambiente
    if os.getenv('FLASK_ENV') == 'development':
        return True
    # Método 2: Modo debug do Flask
    from flask import current_app
    if current_app.debug:
        return True
    # Método 3: Host local
    if request.host.startswith('127.0.0.1') or request.host.startswith('localhost'):
        return True
    return False


# ══════════════════════════════════════════════════════════════════════════════
# Página Index do Sistema
# ══════════════════════════════════════════════════════════════════════════════

@sistema_bp.route('/')
@sistema_bp.route('')
def index():
    """Página principal do módulo Sistema - Dashboard Mestre"""
    return render_template('sistema/grids/grid_sistema_landing.html')

@sistema_bp.route('/teste-header')
@login_required
def teste_header():
    """Rota temporária para aprovação do novo Cabeçalho Padrão Ouro"""
    return render_template('sistema/teste_header.html')


# ══════════════════════════════════════════════════════════════════════════════
# Abas do Sistema (Pattern: Cadastros)
# ══════════════════════════════════════════════════════════════════════════════

@sistema_bp.route('/abas')
@login_required
def abas():
    """Endpoint Mestre de Navegação do Módulo Sistema (Padrão Cadastros)"""
    aba_ativa = request.args.get('aba', 'administracao')
    
    # Definição das Abas para a Macro
    ari_dev = is_ari_dev()
    
    lista_abas = [
        {'id': 'administracao',  'label': 'Administração',  'icon': 'fas fa-user-shield'},
        {'id': 'conexoes',       'label': 'Conexões',       'icon': 'fas fa-plug'},
        {'id': 'armazenamento',  'label': 'Armazenamento',  'icon': 'fas fa-database'}
    ]
    
    # Abas Exclusivas de Desenvolvimento
    if ari_dev:
        lista_abas.append({'id': 'developer',    'label': 'Developer',    'icon': 'fas fa-laptop-code'})
        lista_abas.append({'id': 'lab_dev',      'label': 'Lab DEV',      'icon': 'fas fa-flask'})
        lista_abas.append({'id': 'versoes',      'label': 'Versões',      'icon': 'fas fa-code-branch'})
        lista_abas.append({'id': 'sobre',      'label': 'Sobre AriOne', 'icon': 'fas fa-info-circle'})
        lista_abas.append({'id': 'seguranca',  'label': 'Segurança',     'icon': 'fas fa-shield-alt'})
    
    # Dados específicos para a aba Versões (se estiver nela)
    is_dev = is_development()
    versao_atual = None
    em_dev = []
    versoes = []
    matrix_dev_data = {}
    ari_progress = None
    
    if aba_ativa in ['developer', 'versoes']:
        try:
            versao_atual = Versao.query.filter_by(status='publicada')\
                                       .order_by(Versao.data_publicacao.desc())\
                                       .first()
            if is_dev:
                em_dev = Versao.query.filter_by(status='dev')\
                                     .order_by(Versao.data_inicio.desc())\
                                     .all()
            versoes = Versao.query.order_by(Versao.criado_em.desc()).all()
        except: pass
        
    if aba_ativa == 'matrix_dev':
        from app.utils.progress import get_matrix_progress, get_ari_progress_summary
        matrix_dev_data = get_matrix_progress()
        ari_progress = get_ari_progress_summary()

    return render_template(
        'sistema/abas_sistema.html',
        abas=lista_abas,
        aba_ativa=aba_ativa,
        is_dev=is_dev,
        versao_atual=versao_atual,
        em_dev=em_dev,
        versoes=versoes,
        matrix_data=matrix_dev_data,
        ari_progress=ari_progress,
        modulos=ARIONE_MODULOS
    )

@sistema_bp.route('/administracao')
def administracao():
    return redirect(url_for('sistema.abas', aba='administracao'))

@sistema_bp.route('/conexoes')
def conexoes():
    return redirect(url_for('sistema.abas', aba='conexoes'))

@sistema_bp.route('/armazenamento')
def armazenamento():
    return redirect(url_for('sistema.abas', aba='armazenamento'))

@sistema_bp.route('/auditoria')
@login_required
def auditoria():
    return redirect(url_for('sistema.abas', aba='auditoria'))

@sistema_bp.route('/versoes')
def versoes():
    return redirect(url_for('sistema.abas', aba='versoes'))

@sistema_bp.route('/seguranca')
def seguranca():
    return redirect(url_for('sistema.abas', aba='seguranca'))

@sistema_bp.route('/matrix-dev')
@login_required
def matrix_dev():
    return redirect(url_for('sistema.abas', aba='matrix_dev'))

@sistema_bp.route('/cards/developer/cores')
@login_required
def card_developer_cores():
    """Card de laboratório para testes de cores do Padrão Ouro"""
    return render_template('sistema/cards/Developer/form_developer_cores.html', modulos=ARIONE_MODULOS)

@sistema_bp.route('/cards/developer/vendas-premium')
@login_required
def card_developer_vendas_premium():
    is_modal = request.args.get('modal') == '1'
    return render_template('sistema/cards/Developer/form_developer_vendas_premium.html', is_modal=is_modal)

@sistema_bp.route('/cards/armazenamento/volume-dados')
@login_required
def card_volume_dados():
    """Painel de telemetria de volume de dados."""
    return render_template('sistema/cards/armazenamento/form_volume_dados.html')

@sistema_bp.route('/armazenamento/backup')
@login_required
def form_backup():
    """Formulário de criação de backup manual."""
    manager = BackupManager()
    snapshots = manager.list_snapshots()
    ultimo = snapshots[0] if snapshots else None
    return render_template('sistema/cards/armazenamento/form_backup.html', ultimo=ultimo)

@sistema_bp.route('/armazenamento/restauracao')
@login_required
def form_restauracao():
    """Painel de restauração e gestão de snapshots."""
    manager = BackupManager()
    snapshots = manager.list_snapshots()
    cloud_snapshots = manager.list_s3_snapshots()
    return render_template('sistema/cards/armazenamento/form_restauracao.html', 
                           snapshots=snapshots, 
                           cloud_snapshots=cloud_snapshots)

@sistema_bp.route('/armazenamento/agendamento')
@login_required
def form_agendamento():
    """Configuração de backups automáticos e retenção."""
    import json
    config_path = os.path.join(current_app.instance_path, 'backup_config.json')
    config = {}
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
        except: pass
    return render_template('sistema/cards/armazenamento/form_agendamento.html', config=config)

@sistema_bp.route('/armazenamento/executar-backup', methods=['POST'])
@login_required
def executar_backup():
    """Executa a lógica de backup seguro usando o BackupManager."""
    escopo = request.form.get('escopo', 'db')
    nota = request.form.get('nota', '')
    pastas = request.form.getlist('pastas[]')
    destino = request.form.get('destino', 'local')
    caminho_destino = request.form.get('caminho_destino', '')

    sync_aws = 'cloud_aws' in request.form
    sync_gdrive = 'cloud_google' in request.form

    manager = BackupManager()
    result = manager.create_snapshot(scope=escopo, note=nota, custom_paths=pastas, custom_dest=caminho_destino if destino == 'rede' else None)

    if result.get('success'):
        msg = f'Backup Seguro "{result["filename"]}" gerado localmente.'

        if destino == 'rede' and caminho_destino:
            msg += f' | 📁 Salvo em: {caminho_destino}'

        # Sincronização Cloud (AWS)
        if sync_aws:
            cloud_res = manager.sync_to_cloud(result['path'], provider_type='aws_s3')
            if cloud_res['success']:
                msg += f' | ✅ Sincronizado com AWS S3 ({cloud_res["provider"]}).'
            else:
                msg += f' | ❌ Falha no upload AWS: {cloud_res["error"]}'

        # Sincronização Cloud (Google Drive)
        if sync_gdrive:
            cloud_res = manager.sync_to_cloud(result['path'], provider_type='gdrive')
            if cloud_res['success']:
                msg += f' | ✅ Sincronizado com Google Drive ({cloud_res["provider"]}).'
            else:
                msg += f' | ❌ Falha no upload GDrive: {cloud_res["error"]}'
                
        flash(msg, 'success')
    else:
        flash(f'Erro ao gerar backup: {result.get("error")}', 'danger')
        
    return redirect(url_for('sistema.form_backup'))

@sistema_bp.route('/armazenamento/salvar-agendamento', methods=['POST'])
@login_required
def salvar_agendamento():
    """Salva as configurações de agendamento automático em JSON."""
    import json
    config_path = os.path.join(current_app.instance_path, 'backup_config.json')
    
    config = {
        'horario_db': request.form.get('horario_db', '03:00'),
        'frequencia_media': request.form.get('frequencia_media', 'daily'),
        'horario_media': request.form.get('horario_media', '04:00'),
        'limite_retencao': int(request.form.get('limite_retencao', 30)),
        'sync_aws': 'sync_aws' in request.form,
        'sync_google': 'sync_google' in request.form,
        'updated_at': datetime.now().isoformat()
    }
    
    try:
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=4)
        flash('Configurações de agendamento salvas com sucesso!', 'success')
    except Exception as e:
        flash(f'Erro ao salvar configurações: {str(e)}', 'danger')
        
    return redirect(url_for('sistema.form_agendamento'))

@sistema_bp.route('/armazenamento/status')
@login_required
def backup_status():
    """Retorna o status atual da automação e saúde dos backups."""
    import json
    config_path = os.path.join(current_app.instance_path, 'backup_config.json')
    config = {}
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f: config = json.load(f)
        except: pass
    
    manager = BackupManager()
    snapshots = manager.list_snapshots()
    ultimo = snapshots[0] if snapshots else None
    
    return jsonify({
        'config': config,
        'last_backup': ultimo,
        'total_backups': len(snapshots),
        'disk_usage': sum(s['size'] for s in snapshots) if snapshots else 0,
        'global_status': manager.get_global_status()
    })

@sistema_bp.route('/armazenamento/download-backup/<filename>')
@login_required
def download_backup(filename):
    """Permite o download de um snapshot de segurança."""
    from flask import send_from_directory
    backup_dir = os.path.join(current_app.instance_path, 'backups')
    return send_from_directory(backup_dir, filename, as_attachment=True)

@sistema_bp.route('/armazenamento/excluir-backup/<filename>', methods=['POST'])
@login_required
def excluir_backup(filename):
    """Remove um snapshot de segurança."""
    manager = BackupManager()
    if manager.delete_snapshot(filename):
        flash(f'Snapshot {filename} removido com sucesso.', 'success')
    else:
        flash(f'Erro ao remover snapshot {filename}.', 'danger')
    return redirect(url_for('sistema.form_restauracao'))

@sistema_bp.route('/conexoes/config')
@login_required
def form_api_config():
    """Formulário dinâmico de configuração de APIs (Hub de Integrações)."""
    import json
    config_path = os.path.join(current_app.instance_path, 'api_keys.json')
    connections = []
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f: connections = json.load(f)
        except: pass
    
    # Carrega Provedores Customizados
    custom_providers_path = os.path.join(current_app.instance_path, 'custom_providers.json')
    custom_providers = {}
    if os.path.exists(custom_providers_path):
        try:
            with open(custom_providers_path, 'r') as f: custom_providers = json.load(f)
        except: pass

    # Metadados das APIs suportadas (Nativos)
    providers = {
        'aws_s3': {
            'nome': 'Amazon S3',
            'icon': 'fab fa-aws',
            'cor': '#FF9900',
            'fields': [
                {'name': 'access_key', 'label': 'Access Key ID', 'type': 'text'},
                {'name': 'secret_key', 'label': 'Secret Access Key', 'type': 'password'},
                {'name': 'bucket', 'label': 'Nome do Bucket', 'type': 'text'},
                {'name': 'region', 'label': 'Região', 'type': 'select', 'options': ['us-east-1', 'sa-east-1']}
            ]
        },
        'gdrive': {
            'nome': 'Google Drive',
            'icon': 'fab fa-google-drive',
            'cor': '#1DA1F2',
            'fields': [
                {'name': 'json_token', 'label': 'Service Account JSON', 'type': 'textarea'}
            ]
        },
        'twilio': {
            'nome': 'Twilio (SMS/WhatsApp)',
            'icon': 'fas fa-sms',
            'cor': '#F22F46',
            'fields': [
                {'name': 'sid', 'label': 'Account SID', 'type': 'text'},
                {'name': 'token', 'label': 'Auth Token', 'type': 'password'},
                {'name': 'from_number', 'label': 'Número Remetente', 'type': 'text'}
            ]
        },
        'melhorenvio': {
            'nome': 'Melhor Envio',
            'icon': 'fas fa-shipping-fast',
            'cor': '#00B8D4',
            'fields': [
                {'name': 'token', 'label': 'API Token (Access Token)', 'type': 'textarea'},
                {'name': 'sandbox', 'label': 'Sandbox (Teste)', 'type': 'select', 'options': ['1', '0']},
                {'name': 'cep_origem', 'label': 'CEP de Origem Padrão', 'type': 'text'}
            ]
        },
        'correios': {
            'nome': 'Correios (Web Service)',
            'icon': 'fas fa-mail-bulk',
            'cor': '#FFCE00',
            'fields': [
                {'name': 'usuario', 'label': 'Usuário (Meu Correios)', 'type': 'text'},
                {'name': 'senha', 'label': 'Código de Acesso API', 'type': 'password'},
                {'name': 'cartao', 'label': 'Cartão de Postagem', 'type': 'text'},
                {'name': 'cep_origem', 'label': 'CEP de Origem Padrão', 'type': 'text'}
            ]
        }
    }
    
    # Merge Nativo + Custom
    providers.update(custom_providers)
    
    return render_template('sistema/cards/conexoes/form_api_config.html', connections=connections, providers=providers)

@sistema_bp.route('/conexoes/sync-logs')
@login_required
def card_sync_logs():
    """Retorna o formulário de histórico de eventos (Sync Logs)."""
    return render_template('sistema/cards/conexoes/form_sync_logs.html')

@sistema_bp.route('/conexoes/salvar-provedor', methods=['POST'])
@login_required
def salvar_provedor_custom():
    """Cria um novo molde de API (Provedor) no Hub."""
    import json
    path = os.path.join(current_app.instance_path, 'custom_providers.json')
    
    customs = {}
    if os.path.exists(path):
        try:
            with open(path, 'r') as f: customs = json.load(f)
        except: pass
        
    pid = request.form.get('nome').lower().replace(' ', '_')
    
    # Processa campos dinâmicos definidos na criação do provedor
    fields = []
    field_labels = request.form.getlist('f_label[]')
    field_types = request.form.getlist('f_type[]')
    
    for label, ftype in zip(field_labels, field_types):
        if label:
            fields.append({
                'name': label.lower().replace(' ', '_'),
                'label': label,
                'type': ftype
            })

    customs[pid] = {
        'nome': request.form.get('nome'),
        'icon': request.form.get('icon', 'fas fa-plug'),
        'cor': request.form.get('cor', '#34495e'),
        'fields': fields
    }
    
    try:
        with open(path, 'w') as f:
            json.dump(customs, f, indent=4)
        flash(f'Novo Provedor "{request.form.get("nome")}" criado no Hub!', 'success')
    except Exception as e:
        flash(f'Erro ao criar provedor: {str(e)}', 'danger')
        
    return redirect(url_for('sistema.form_api_config'))

@sistema_bp.route('/conexoes/salvar-api', methods=['POST'])
@login_required
def salvar_api_config():
    """Salva uma nova conexão ou atualiza existente no Hub."""
    import json
    config_path = os.path.join(current_app.instance_path, 'api_keys.json')
    
    # Carrega existentes
    connections = []
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f: connections = json.load(f)
        except: pass

    conn_id = request.form.get('id')
    provider_id = request.form.get('provider_id')
    
    if conn_id:
        # Modo Edição
        new_conn = next((c for c in connections if c['id'] == conn_id), None)
        if not new_conn:
            flash("Conexão não encontrada para edição.", "danger")
            return redirect(url_for('sistema.form_api_config'))
        new_conn['label'] = request.form.get('label', provider_id)
        new_conn['updated_at'] = datetime.now().isoformat()
        new_conn['data'] = {} # Reset data to repopulate
    else:
        # Modo Novo
        new_conn = {
            'id': provider_id + '_' + datetime.now().strftime('%H%M%S'),
            'provider': provider_id,
            'label': request.form.get('label', provider_id),
            'data': {},
            'updated_at': datetime.now().isoformat()
        }
        connections.append(new_conn)
    
    # Coleta campos dinâmicos
    for key, value in request.form.items():
        if key.startswith('field_'):
            new_conn['data'][key.replace('field_', '')] = value

    try:
        with open(config_path, 'w') as f:
            json.dump(connections, f, indent=4)
        flash(f'Integração {new_conn["label"]} salva com sucesso!', 'success')
    except Exception as e:
        flash(f'Erro ao salvar: {str(e)}', 'danger')
        
    return redirect(url_for('sistema.form_api_config'))

@sistema_bp.route('/conexoes/excluir-api/<id>', methods=['POST'])
@login_required
def excluir_api_config(id):
    """Remove uma conexão configurada no Hub."""
    import json
    config_path = os.path.join(current_app.instance_path, 'api_keys.json')
    
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f: connections = json.load(f)
            # Filtra removendo o ID
            novas_conexoes = [c for c in connections if c['id'] != id]
            
            with open(config_path, 'w') as f:
                json.dump(novas_conexoes, f, indent=4)
            flash("Conexão removida com sucesso.", "success")
        except Exception as e:
            flash(f"Erro ao excluir conexão: {str(e)}", "danger")
    
    return redirect(url_for('sistema.form_api_config'))

@sistema_bp.route('/api/listar-diretorios', methods=['GET'])
@login_required
def api_listar_diretorios():
    """Retorna lista de subdiretórios para o seletor de backup."""
    import os
    path_rel = request.args.get('path', '')
    base_uploads = os.path.join(current_app.static_folder, 'uploads')
    
    target_path = os.path.normpath(os.path.join(base_uploads, path_rel))
    
    # Segurança: Não permitir sair da pasta uploads
    if not target_path.startswith(os.path.normpath(base_uploads)):
        return jsonify({'error': 'Acesso negado'}), 403
        
    if not os.path.exists(target_path):
        return jsonify({'dirs': [], 'path': path_rel})
        
    dirs = []
    for item in os.listdir(target_path):
        full_item = os.path.join(target_path, item)
        if os.path.isdir(full_item):
            dirs.append(item)
            
    return jsonify({
        'dirs': sorted(dirs),
        'current_path': path_rel
    })

@sistema_bp.route('/api/estatisticas-sistema', methods=['GET'])
@login_required
def api_estatisticas_sistema():
    """Retorna estatísticas detalhadas de arquivos por categoria e nuvem."""
    root_dir = os.path.abspath(os.path.join(current_app.root_path, ".."))
    
    stats = {
        'total': {'files': 0, 'dirs': 0, 'size': 0},
        'categorias': {
            'models': {'count': 0, 'size': 0},
            'routes': {'count': 0, 'size': 0},
            'templates': {'count': 0, 'size': 0},
            'banco_fisico': {'count': 0, 'size': 0}
        },
        'cloud': {
            'aws': {'count': 0, 'size': 0, 'status': 'Desconectado'},
            'gdrive': {'count': 0, 'size': 0, 'status': 'Desconectado'}
        }
    }
    
    ignore_dirs = {'.venv', 'venv', '.git', '__pycache__', '.pytest_cache', '.idea', '.vscode', 'node_modules', '.gemini'}
    
    for root, dirs, files in os.walk(root_dir):
        dirs[:] = [d for d in dirs if d not in ignore_dirs]
        
        stats['total']['dirs'] += len(dirs)
        stats['total']['files'] += len(files)
        
        for f in files:
            fp = os.path.join(root, f)
            if os.path.islink(fp): continue
            
            try:
                fsize = os.path.getsize(fp)
                stats['total']['size'] += fsize
                
                ext = f.lower().split('.')[-1] if '.' in f else ''
                path_lower = root.lower()
                
                if ext == 'py':
                    if 'models' in path_lower:
                        stats['categorias']['models']['count'] += 1
                        stats['categorias']['models']['size'] += fsize
                    elif 'routes' in path_lower:
                        stats['categorias']['routes']['count'] += 1
                        stats['categorias']['routes']['size'] += fsize
                elif ext == 'html':
                    stats['categorias']['templates']['count'] += 1
                    stats['categorias']['templates']['size'] += fsize
                elif ext in ['db', 'sqlite', 'sqlite3']:
                    stats['categorias']['banco_fisico']['count'] += 1
                    stats['categorias']['banco_fisico']['size'] += fsize
            except: pass
            
    # Métricas de Nuvem (Cloud)
    try:
        manager = BackupManager()
        # AWS S3
        s3_snapshots = manager.list_s3_snapshots()
        if s3_snapshots:
            stats['cloud']['aws']['count'] = len(s3_snapshots)
            stats['cloud']['aws']['size'] = sum(s.get('size', 0) for s in s3_snapshots)
            stats['cloud']['aws']['status'] = 'Ativo'
        
        # Google Drive (Simulado ou via Config)
        config_path = os.path.join(current_app.instance_path, 'backup_config.json')
        if os.path.exists(config_path):
            import json
            with open(config_path, 'r') as f:
                cfg = json.load(f)
                if cfg.get('sync_google'):
                    stats['cloud']['gdrive']['status'] = 'Ativo (Sincronizando)'
    except: pass

    # Conversão para MB/GB amigável
    def to_mb(b): return round(b / (1024**2), 2)
    def to_gb(b): return round(b / (1024**3), 3)

    return jsonify({
        'pastas': stats['total']['dirs'],
        'arquivos': stats['total']['files'],
        'espaco_gb': to_gb(stats['total']['size']),
        'espaco_mb': to_mb(stats['total']['size']),
        'detalhes': {
            'models_mb': to_mb(stats['categorias']['models']['size']),
            'routes_mb': to_mb(stats['categorias']['routes']['size']),
            'html_mb': to_mb(stats['categorias']['templates']['size']),
            'db_fisico_mb': to_mb(stats['categorias']['banco_fisico']['size']),
            'models_count': stats['categorias']['models']['count'],
            'routes_count': stats['categorias']['routes']['count'],
            'html_count': stats['categorias']['templates']['count'],
            'db_fisico_count': stats['categorias']['banco_fisico']['count']
        },
        'cloud': {
            'aws_gb': to_gb(stats['cloud']['aws']['size']),
            'aws_count': stats['cloud']['aws']['count'],
            'aws_status': stats['cloud']['aws']['status'],
            'gdrive_status': stats['cloud']['gdrive']['status']
        },
        'root': root_dir
    })


# ══════════════════════════════════════════════════════════════════════════════
# Formulário de Versão (Criar/Editar)
# ══════════════════════════════════════════════════════════════════════════════

@sistema_bp.route('/versoes/fix-db')
def fix_versoes_db_web():
    """Rota temporária para corrigir o banco de dados via navegador"""
    import sqlite3
    try:
        db_path = 'instance/arione.db'
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Add sinopse
        try:
            cursor.execute("ALTER TABLE versoes ADD COLUMN sinopse TEXT")
        except: pass
        
        # Create activities table
        try:
            cursor.execute("""
                CREATE TABLE versoes_atividades (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    versao_id INTEGER NOT NULL,
                    data_hora DATETIME DEFAULT CURRENT_TIMESTAMP,
                    tipo TEXT DEFAULT 'info',
                    descricao TEXT NOT NULL,
                    FOREIGN KEY (versao_id) REFERENCES versoes (id)
                )
            """)
        except: pass
        
        conn.commit()
        conn.close()
        flash('Banco de Dados atualizado com sucesso! Pode usar a tela de Versões agora.', 'success')
    except Exception as e:
        flash(f'Erro ao atualizar: {str(e)}', 'danger')
    
    return redirect(url_for('sistema.versoes'))


@sistema_bp.route('/versoes/form', methods=['GET', 'POST'])
@sistema_bp.route('/versoes/form/<int:id>', methods=['GET', 'POST'])
def form_versao(id=None):
    """Formulário para criar ou editar uma versão"""
    # Bloqueia em produção
    if not is_development():
        flash('Operação não permitida em ambiente de produção.', 'danger')
        return redirect(url_for('sistema.versoes'))
    
    versao = Versao.query.get(id) if id else None
    
    # Busca a última versão publicada ou em dev para sugestão
    ultima_v = Versao.query.order_by(Versao.criado_em.desc()).first()
    ultima_numero = ultima_v.numero if ultima_v else "v0.0.0"
    
    if request.method == 'POST':
        # Lógica de Proteção contra Duplicidade (UNIQUE Constraint)
        numero_form = request.form.get('numero', '').strip()
        
        # Se estamos criando (id is None), mas o número já existe, capturamos o registro existente
        if id is None:
            existente = Versao.query.filter_by(numero=numero_form).first()
            if existente:
                versao = existente
                flash(f'A versão {numero_form} já existia. Entramos no modo de edição deste registro.', 'info')
            else:
                versao = Versao()
        
        # Atribuição de Campos
        versao.numero          = numero_form
        versao.titulo          = request.form.get('titulo', '').strip()
        versao.sinopse         = request.form.get('sinopse', '').strip()
        versao.status          = request.form.get('status', 'dev')
        versao.autor           = request.form.get('autor', '').strip()
        
        # Datas (Início e Publicação com Hora)
        data_inicio_str = request.form.get('data_inicio', '').strip()
        if data_inicio_str:
            try:
                # datetime-local envia formato ISO 'YYYY-MM-DDTHH:MM'
                versao.data_inicio = datetime.fromisoformat(data_inicio_str)
            except ValueError:
                versao.data_inicio = None
        
        data_pub_str = request.form.get('data_publicacao', '').strip()
        if data_pub_str:
            try:
                versao.data_publicacao = datetime.fromisoformat(data_pub_str)
            except ValueError:
                versao.data_publicacao = None
        
        data_previsao_str = request.form.get('data_previsao', '').strip()
        if data_previsao_str:
            try:
                versao.data_previsao = datetime.fromisoformat(data_previsao_str)
            except ValueError:
                versao.data_previsao = None
        
        # Se mudou para produção e não tem data de publicação, define agora
        if versao.status == 'publicada' and not versao.data_publicacao:
            versao.data_publicacao = datetime.now()
        
        # Conteúdo
        versao.changelog       = request.form.get('changelog', '').strip()
        versao.arquivos        = request.form.get('arquivos', '').strip()
        versao.observacoes     = request.form.get('observacoes', '').strip()
        
        try:
            db.session.add(versao)
            db.session.commit()
            flash(f'Versão {versao.numero} salva com sucesso!', 'success')
            return redirect(url_for('sistema.versoes'))
        
        except Exception as e:
            db.session.rollback()
            # Tratamento amigável para erro de integridade (caso o check acima falhe por concorrência)
            if "UNIQUE constraint failed" in str(e):
                flash(f'Erro: A versão {numero_form} já está cadastrada. Use a listagem para editá-la.', 'danger')
            else:
                flash(f'Erro ao salvar: {str(e)}', 'danger')
    
    return render_template(
        'sistema/cards/versoes/form_versao.html',
        versao=versao,
        ultima_numero=ultima_numero
    )


# ══════════════════════════════════════════════════════════════════════════════
# Excluir Versão
# ══════════════════════════════════════════════════════════════════════════════

@sistema_bp.route('/versoes/excluir/<int:id>', methods=['POST'])
def excluir_versao(id):
    """Exclui uma versão (apenas em DEV)"""
    if not is_development():
        flash('Operação não permitida em ambiente de produção.', 'danger')
        return redirect(url_for('sistema.versoes'))
    
    versao = Versao.query.get_or_404(id)
    
    # Não permite excluir versão em produção
    if versao.status == 'publicada':
        flash('Não é possível excluir uma versão em produção!', 'danger')
        return redirect(url_for('sistema.versoes'))
    
    try:
        numero = versao.numero
        db.session.delete(versao)
        db.session.commit()
        flash(f'Versão {numero} excluída com sucesso!', 'success')
    
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao excluir: {str(e)}', 'danger')
    
    return redirect(url_for('sistema.versoes'))


# ══════════════════════════════════════════════════════════════════════════════
# Publicar Versão (mover para produção)
# ══════════════════════════════════════════════════════════════════════════════

@sistema_bp.route('/versoes/<int:id>/atividade', methods=['POST'])
def registrar_atividade(id):
    """Registra uma nova atividade na timeline da versão via AJAX"""
    if not is_development():
        return jsonify({'success': False, 'message': 'Não permitido em produção'}), 403
    
    data = request.get_json()
    if not data or not data.get('descricao'):
        return jsonify({'success': False, 'message': 'Descrição é obrigatória'}), 400
    
    try:
        from app.models.sistema.versao import VersaoAtividade
        nova = VersaoAtividade(
            versao_id=id,
            tipo=data.get('tipo', 'info'),
            descricao=data.get('descricao')
        )
        db.session.add(nova)
        db.session.commit()
        return jsonify({'success': True, 'id': nova.id})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


@sistema_bp.route('/versoes/publicar/<int:id>', methods=['POST'])
def publicar_versao(id):
    """Publica uma versão (move para produção)"""
    import sys
    import subprocess
    if not is_development():
        flash('Operação não permitida em ambiente de produção.', 'danger')
        return redirect(url_for('sistema.versoes'))
    
    versao = Versao.query.get_or_404(id)
    
    try:
        versao.status = 'publicada'
        versao.data_publicacao = datetime.now()
        db.session.commit()
        
        # 🚀 DISPARO DO MOTOR DE SINCRONIZAÇÃO (DEPLOY INDUSTRIAL)
        try:
            # Localiza o script na raiz do projeto (um nível acima da pasta app)
            script_path = os.path.abspath(os.path.join(current_app.root_path, "..", "publicar.py"))
            
            if os.path.exists(script_path):
                # Dispara como processo independente (Desvinculado do Flask)
                subprocess.Popen([sys.executable, script_path], 
                                 stdout=subprocess.DEVNULL, 
                                 stderr=subprocess.DEVNULL, 
                                 start_new_session=True, # No Linux/Unix
                                 creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0) # No Windows
                
                flash(f'✅ Versão {versao.numero} Publicada! A sincronização física para C:\\AriOne está rodando agora em segundo plano.', 'success')
            else:
                flash(f'⚠️ Versão atualizada, mas o script de sincronização não foi encontrado em: {script_path}', 'warning')
        except Exception as e_sync:
            flash(f'⚠️ Versão atualizada, mas erro ao disparar cópia física: {str(e_sync)}', 'warning')
    
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao publicar: {str(e)}', 'danger')
    
    return redirect(url_for('sistema.versoes'))


@sistema_bp.route('/versoes/sincronizar-fisico', methods=['POST'])
def sincronizar_fisico():
    """Dispara apenas a sincronização física (Robocopy) sem alterar dados"""
    import sys
    import subprocess
    if not is_development():
        return jsonify({'success': False, 'message': 'Não permitido em produção.'}), 403
    
    try:
        # Reset do status antes de começar
        status_path = os.path.join(current_app.root_path, '..', 'instance', 'deploy_status.json')
        if os.path.exists(status_path): os.remove(status_path)
        
        script_path = os.path.abspath(os.path.join(current_app.root_path, "..", "publicar.py"))
        if os.path.exists(script_path):
            subprocess.Popen([sys.executable, script_path], 
                             stdout=subprocess.DEVNULL, 
                             stderr=subprocess.DEVNULL, 
                             start_new_session=True, 
                             creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
            return jsonify({'success': True, 'message': 'Sincronização física iniciada com sucesso!'})
        else:
            return jsonify({'success': False, 'message': 'Motor de sincronização não encontrado.'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


@sistema_bp.route('/versoes/status-sincronia', methods=['GET'])
def consultar_status_sincronia():
    """Retorna o progresso atual lido do arquivo JSON"""
    import json
    status_path = os.path.join(current_app.root_path, '..', 'instance', 'deploy_status.json')
    if not os.path.exists(status_path):
        return jsonify({'status': 'idle', 'percent': 0})
    
    try:
        with open(status_path, 'r') as f:
            return jsonify(json.load(f))
    except:
        return jsonify({'status': 'running', 'percent': 50, 'message': 'Lendo progresso...'})


@sistema_bp.route('/versoes/visualizar-log-sincronia')
@login_required
def visualizar_log_sincronia():
    """Lê e exibe o relatório da última sincronização física"""
    log_path = os.path.join(current_app.instance_path, 'sync_report.log')
    if not os.path.exists(log_path):
        return "Nenhum relatório de sincronização encontrado. Realize uma sincronização primeiro."
    
    try:
        with open(log_path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
        # Reutiliza o template de visualização formatando como bloco de código
        return render_template('sistema/visualizar_md.html', 
                               conteudo=f"```text\n{content}\n```", 
                               titulo="Relatório de Sincronização Física")
    except Exception as e:
        return f"Erro ao ler log: {str(e)}"


# ══════════════════════════════════════════════════════════════════════════════
# Rotas para Módulo de Administração de Acessos
# ══════════════════════════════════════════════════════════════════════════════

@sistema_bp.route('/usuarios/form', methods=['GET'])
@sistema_bp.route('/usuarios/form/<int:id>', methods=['GET'])
def form_usuarios(id=None):
    from app.models.usuario import Usuario
    from app.models.sistema.perfil import Perfil
    from app.models.cadastros.empresa import Empresa
    
    usuario = Usuario.query.get(id) if id else None
    usuarios_lista = Usuario.query.all()
    perfis_lista = Perfil.query.all()
    empresas_lista = Empresa.query.order_by(Empresa.razao_social).all()
    
    return render_template('sistema/cards/administracao/form_usuarios.html', 
                           usuario=usuario, 
                           usuarios_lista=usuarios_lista,
                           perfis_lista=perfis_lista,
                           empresas_lista=empresas_lista)


@sistema_bp.route('/usuarios/salvar', methods=['POST'])
def salvar_usuario():
    from app.models.usuario import Usuario
    from werkzeug.security import generate_password_hash
    from datetime import datetime
    
    # Limpeza de campos inteiros para evitar ValueError: invalid literal for int() with base 10: ''
    def safe_int(val):
        if val is None: return None
        s = str(val).strip()
        return int(s) if s.isdigit() else None

    usuario_id = safe_int(request.form.get('id'))
    nome = request.form.get('nome')
    apelido = request.form.get('apelido', '').strip() or None
    email = request.form.get('email')
    cpf = request.form.get('cpf')
    senha = request.form.get('senha')
    
    # Checkbox e Toggles
    ativo = 'status' in request.form
    habilitar_2fa = 'habilitar_2fa' in request.form
    perfil_id = safe_int(request.form.get('perfil'))
    empresas = request.form.getlist('empresas[]')
    
    if usuario_id:
        u = Usuario.query.get(usuario_id)
        msg = f"Usuário {nome} alterado com sucesso."
    else:
        u = Usuario(email=email)
        msg = f"Usuário {nome} criado com sucesso."
        db.session.add(u)
        
    u.nome = nome
    u.apelido = apelido
    u.cpf = cpf
    u.ativo = ativo
    u.habilitar_2fa = habilitar_2fa
    u.perfil_id = perfil_id # Atribui o int ou None com segurança
    
    # Adicionando empresa_id da sessão com segurança
    u.empresa_id = safe_int(session.get('empresa_id'))
        
    u.empresas_acesso = ",".join(empresas)
    
    # Se uma nova senha for digitada, hasheie
    if senha and len(senha.strip()) > 0:
        u.senha_hash = generate_password_hash(senha)
        
    exp = request.form.get('expiracao_senha')
    if exp:
        u.expiracao_senha = datetime.strptime(exp, '%Y-%m-%d').date()
    else:
        u.expiracao_senha = None

    # ── Upload de Foto ──
    foto = request.files.get('foto')
    if foto and foto.filename:
        from werkzeug.utils import secure_filename
        filename = secure_filename(foto.filename)
        
        # Pasta de uploads do usuário
        upload_path = os.path.join(current_app.static_folder, 'uploads', 'usuarios', str(u.id or 'novo'))
        os.makedirs(upload_path, exist_ok=True)
        
        filepath = os.path.join(upload_path, filename)
        foto.save(filepath)
        
        # Salva o caminho relativo no banco
        u.foto = f"uploads/usuarios/{u.id or 'novo'}/{filename}"

    try:
        db.session.add(u)
        db.session.flush() # Pega o ID caso seja novo
        
        # Se era 'novo' (novo cadastro com foto), movemos para a pasta final com o ID do banco
        if u.foto and 'uploads/usuarios/novo/' in u.foto:
             old_path = os.path.join(current_app.static_folder, 'uploads', 'usuarios', 'novo')
             new_path = os.path.join(current_app.static_folder, 'uploads', 'usuarios', str(u.id))
             
             if os.path.exists(old_path):
                 if os.path.exists(new_path):
                     shutil.rmtree(new_path)
                 os.rename(old_path, new_path)
                 u.foto = u.foto.replace('/novo/', f'/{u.id}/')

        db.session.commit()
        flash(msg, 'success')
        
    except IntegrityError as e:
        db.session.rollback()
        if 'usuarios.email' in str(e).lower():
            flash(f'O e-mail "{email}" já está cadastrado para outro usuário.', 'danger')
        else:
            flash(f'Erro de integridade de dados: {str(e)}', 'danger')
        return redirect(url_for('sistema.form_usuarios', id=u.id if u.id else ''))

    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao salvar usuário: {str(e)}', 'danger')
        return redirect(url_for('sistema.form_usuarios', id=u.id if u.id else ''))
        
    return redirect(url_for('sistema.form_usuarios'))


@sistema_bp.route('/usuarios/excluir/<int:id>', methods=['POST', 'GET'])
def excluir_usuario(id):
    from app.models.usuario import Usuario
    u = Usuario.query.get_or_404(id)
    try:
        nome = u.nome
        db.session.delete(u)
        db.session.commit()
        flash(f'Usuário {nome} excluído com sucesso.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao excluir usuário: {str(e)}', 'danger')
    return redirect(url_for('sistema.form_usuarios'))


@sistema_bp.route('/perfis/form', methods=['GET'])
@sistema_bp.route('/perfis/form/<int:id>', methods=['GET'])
def form_perfis(id=None):
    from app.models.sistema.perfil import Perfil
    perfil = Perfil.query.get(id) if id else None
    perfis_lista = Perfil.query.all()
    return render_template('sistema/cards/administracao/form_perfis.html',
                           perfil=perfil,
                           perfis_lista=perfis_lista)


@sistema_bp.route('/perfis/salvar', methods=['POST'])
def salvar_perfil():
    from app.models.sistema.perfil import Perfil
    import json
    
    perfil_id = request.form.get('id')
    nome = request.form.get('nome')
    descricao = request.form.get('descricao')
    
    permissoes_raw = request.form.get('permissoes_json', '{}')
    try:
        permissoes = json.loads(permissoes_raw)
    except:
        permissoes = {}
    
    if perfil_id:
        p = Perfil.query.get(perfil_id)
        msg_ok = f'Perfil {nome} alterado com sucesso.'
    else:
        p = Perfil()
        db.session.add(p)
        msg_ok = f'Perfil {nome} criado com sucesso.'
        
    p.nome = nome
    p.descricao = descricao
    p.permissoes = permissoes
    
    try:
        db.session.commit()
        flash(msg_ok, 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao salvar perfil: {str(e)}', 'danger')
        
    return redirect(url_for('sistema.form_perfis'))


@sistema_bp.route('/perfis/excluir/<int:id>', methods=['POST', 'GET'])
def excluir_perfil(id):
    from app.models.sistema.perfil import Perfil
    p = Perfil.query.get_or_404(id)
    try:
        db.session.delete(p)
        db.session.commit()
        flash(f'Perfil {p.nome} excluído com sucesso.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao excluir perfil: {str(e)}', 'danger')
    return redirect(url_for('sistema.form_perfis'))


@sistema_bp.route('/relatorios/admin', methods=['GET', 'POST'])
def form_relatorios_admin():
    """Mockup de Parametrização para Relatórios base de Administração"""
    return render_template('sistema/cards/administracao/form_relatorios.html')

# ── Seleção de Empresa (Multi-Tenant) ───────────────────────────────────────

@sistema_bp.route('/modal-trocar-empresa')
@login_required
def modal_trocar_empresa():
    """Retorna o conteúdo do modal de troca de empresa via AJAX"""
    # Lógica de Permissão Multi-Tenant AriOne
    # Se o usuário for Admin/Master, ele vê TODAS as empresas cadastradas
    is_admin = False
    if current_user.perfil_obj and current_user.perfil_obj.nome in ['Administrador', 'Master', 'Sistema']:
        is_admin = True

    if is_admin:
        empresas = Empresa.query.order_by(Empresa.razao_social).all()
    else:
        ids_acesso = []
        if current_user.empresas_acesso:
            ids_acesso = [int(i.strip()) for i in current_user.empresas_acesso.split(',') if i.strip()]
        
        # Se não houver IDs, mas o usuário estiver vinculado a uma empresa, permite trocar para ela
        if not ids_acesso and current_user.empresa_id:
            ids_acesso = [current_user.empresa_id]
            
        empresas = Empresa.query.filter(Empresa.id.in_(ids_acesso)).all() if ids_acesso else []
    
    return render_template('sistema/modal_trocar_empresa.html', empresas=empresas)

@sistema_bp.route('/trocar-empresa/<int:id>')
@login_required
def trocar_empresa(id):
    """Efetiva a troca de empresa na sessão"""
    ids_acesso = []
    if current_user.empresas_acesso:
        ids_acesso = [int(i.strip()) for i in current_user.empresas_acesso.split(',') if i.strip()]
    
    if id not in ids_acesso and id != current_user.empresa_id:
        flash('Você não tem acesso a esta empresa.', 'danger')
        return redirect(request.referrer or url_for('cadastros.abas'))

    empresa = Empresa.query.get(id)
    if empresa:
        session['empresa_id'] = empresa.id
        session['nome_empresa'] = empresa.razao_social
        flash(f'Empresa alterada para {empresa.razao_social}', 'success')
    
    # Redireciona para a mesma página anterior ou home
    return redirect(request.referrer or url_for('cadastros.abas'))



@sistema_bp.route('/visualizar-protocolo/<nome>')
@login_required
def visualizar_protocolo(nome):
    """Renderiza um arquivo Markdown em uma página com estilo AriOne."""
    import os
    # Tenta localizar em static ou em Doc_DEV
    paths = [
        os.path.join(current_app.static_folder, f"{nome}.md"),
        os.path.join(current_app.root_path, "..", "Doc_DEV", "Integridade", f"{nome}.md")
    ]
    
    conteudo = "Documento não encontrado."
    for p in paths:
        if os.path.exists(p):
            with open(p, 'r', encoding='utf-8') as f:
                conteudo = f.read()
            break
            
    return render_template('sistema/visualizar_md.html', conteudo=conteudo, titulo=nome.upper())

@sistema_bp.route('/progresso-dev')
@login_required
def progresso_dev():
    return redirect(url_for('sistema.abas', aba='matrix_dev'))

import json as _json

PROGRESSO_DEV_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'data', 'progresso_dev.json')

def _ler_progresso():
    try:
        os.makedirs(os.path.dirname(PROGRESSO_DEV_FILE), exist_ok=True)
        if os.path.exists(PROGRESSO_DEV_FILE):
            with open(PROGRESSO_DEV_FILE, 'r', encoding='utf-8') as f:
                return _json.load(f)
    except Exception:
        pass
    return {}

def _salvar_progresso(data):
    os.makedirs(os.path.dirname(PROGRESSO_DEV_FILE), exist_ok=True)
    with open(PROGRESSO_DEV_FILE, 'w', encoding='utf-8') as f:
        _json.dump(data, f, ensure_ascii=False)

@sistema_bp.route('/api/progresso-dev/toggle', methods=['POST'])
@login_required
def api_progresso_dev_toggle():
    """Salva o estado pronto/não-pronto de um card no servidor."""
    dados = request.get_json()
    card_id = dados.get('id', '').strip()
    pronto = dados.get('pronto', False)
    if not card_id:
        return jsonify({'erro': 'ID inválido'}), 400
    progresso = _ler_progresso()
    progresso[card_id] = pronto
    _salvar_progresso(progresso)
    return jsonify({'ok': True, 'id': card_id, 'pronto': pronto})

@sistema_bp.route('/api/progresso-dev/status', methods=['GET'])
@login_required
def api_progresso_dev_status():
    """Retorna o estado de todos os cards marcados como prontos."""
    return jsonify(_ler_progresso())

@sistema_bp.route('/migrar-setores-db')
def migrar_setores_db():
    """Rota temporária para migrar as colunas da tabela setores"""
    import sqlite3
    try:
        db_path = os.path.join(current_app.instance_path, 'arione.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        relatorio = []
        
        # Colunas a adicionar
        colunas = [
            ("codigo", "VARCHAR(20)"),
            ("sigla", "VARCHAR(10)"),
            ("parent_id", "INTEGER REFERENCES setores(id)")
        ]
        
        for col, tipo in colunas:
            try:
                cursor.execute(f"ALTER TABLE setores ADD COLUMN {col} {tipo}")
                relatorio.append(f"Coluna {col} adicionada.")
            except Exception:
                relatorio.append(f"Coluna {col} já existe ou erro ignorado.")
        
        conn.commit()
        conn.close()
        return f"<h1>Migração Concluída</h1><ul><li>" + "</li><li>".join(relatorio) + "</li></ul><p><a href='/'>Voltar</a></p>"
    except Exception as e:
        return f"<h1>Erro na Migração</h1><p>{str(e)}</p>"


@sistema_bp.route('/limpar-base-debug')
@login_required
def limpar_base_debug():
    """Rota temporária para limpar empresas excedentes (Mantém apenas a primeira)"""
    # Verifica se é admin/master por segurança
    if not (current_user.perfil_obj and current_user.perfil_obj.nome in ['Administrador', 'Master', 'Sistema']):
        return "Acesso negado.", 403
        
    try:
        from app.models.cadastros.empresa import Empresa
        
        # Mantemos a empresa com o menor ID
        primeira = Empresa.query.order_by(Empresa.id).first()
        
        if not primeira:
            return "Nenhuma empresa encontrada."
            
        # Deleta as outras (SQLAlchemy tratará os cascades definidos no model)
        outras = Empresa.query.filter(Empresa.id != primeira.id).all()
        qtd = len(outras)
        
        for e in outras:
            db.session.delete(e)
            
        db.session.commit()
        return f"<h1>Limpeza Concluída</h1><p>Mantida: {primeira.razao_social} (ID {primeira.id})</p><p>Removidas: {qtd} registros.</p><p><a href='/'>Voltar ao Sistema</a></p>"
        
    except Exception as e:
        db.session.rollback()
        return f"<h1>Erro na Limpeza</h1><p>{str(e)}</p>"

@sistema_bp.route('/card/institucional')
@login_required
def card_institucional():
    """Retorna o card institucional com Missão, Visão e Valores."""
    return render_template('sistema/cards/SobreAriOne/form_institucional.html')

@sistema_bp.route('/card/creditos')
@login_required
def card_creditos():
    """Retorna o card de créditos com a Equipe AriOne."""
    return render_template('sistema/cards/SobreAriOne/form_creditos.html')

@sistema_bp.route('/card/roadmap')
@login_required
def card_roadmap():
    """Retorna o card de roadmap com as futuras entregas."""
    return render_template('sistema/cards/SobreAriOne/form_roadmap.html')

@sistema_bp.route('/card/central-parceiros')
@login_required
def card_central_parceiros():
    """Retorna a central de gestão de parceiros (Hub Central)."""
    from app.models.sistema.licenca import Licenca
    licencas = Licenca.query.order_by(Licenca.criado_em.desc()).all()
    return render_template('sistema/cards/SobreAriOne/form_central_Hub.html', licencas=licencas)

@sistema_bp.route('/card/hub-licenc', methods=['GET', 'POST'])
@login_required
def hub_licenc():
    """Retorna o formulário de registro de novo parceiro (Hub de Licenciamento)."""
    from app.models.sistema.licenca import Licenca
    from app.utils.progress import get_matrix_progress
    
    
    if request.method == 'POST':
        try:
            # Captura dados básicos
            nome = request.form.get('nome')
            cnpj = request.form.get('cnpj')
            contato = request.form.get('contato_master')
            email = request.form.get('email')
            whatsapp = request.form.get('whatsapp')
            cidade = request.form.get('cidade')
            uf = request.form.get('uf')
            pais = request.form.get('pais', 'Brasil')
            status = request.form.get('status', 'ATIVO')
            tipo_cobranca = request.form.get('tipo_cobranca')
            inicio_str = request.form.get('inicio_cobranca')
            assinatura = request.form.get('assinatura_url')
            
            # Converte data
            inicio_date = None
            if inicio_str:
                inicio_date = datetime.strptime(inicio_str, '%Y-%m-%d').date()
            
            # Captura Matriz de Licenciamento (todas as permissões marcadas)
            matriz_permissoes = {}
            for key, value in request.form.items():
                if key.startswith('permissao_'):
                    matriz_permissoes[key] = True
            
            # Cria/Atualiza Registro
            nova_licenca = Licenca(
                nome_parceiro=nome,
                cnpj_cpf=cnpj,
                contato_master=contato,
                email_gestao=email,
                whatsapp_gestor=whatsapp,
                cidade=cidade,
                uf=uf,
                pais=pais,
                status=status,
                tipo_cobranca=tipo_cobranca,
                inicio_cobranca=inicio_date,
                assinatura_url=assinatura,
                matriz_licenciamento=matriz_permissoes
            )
            
            db.session.add(nova_licenca)
            db.session.commit()
            
            return jsonify({'success': True, 'message': f'Licença para {nome} ativada com sucesso!'})
        
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': f'Erro ao processar licenciamento: {str(e)}'}), 500

    matriz_mestre = get_matrix_progress()
    # Carrega licenças para a listagem interna do form
    licencas = Licenca.query.order_by(Licenca.criado_em.desc()).all()
    return render_template('sistema/cards/SobreAriOne/form_Hub_Licenc.html', 
                           modulos=ARIONE_MODULOS,
                           matriz_mestre=matriz_mestre,
                           licencas=licencas)


# ── CENTRAL DE RELATÓRIOS E GATEWAY SISTEMA ─────────────────────────────────

@sistema_bp.route('/gateway-modulos')
@login_required
def gateway_modulos_sistema():
    """Retorna o menu mestre de relatórios e sub-módulos do sistema."""
    return render_template('sistema/cards/form_gateway_modulos_sistema.html')

@sistema_bp.route('/card/relatorios')
@login_required
def card_sistema_relatorios():
    """Retorna o formulário de relatórios/filtros para o módulo solicitado."""
    modulo = request.args.get('modulo', 'administracao')
    
    # Mapeamento de Configurações Visuais por Módulo
    config = {
        'administracao': {'titulo': 'Relatórios de Acessos & Perfis', 'cor': '#34495E'},
        'conexoes':      {'titulo': 'Telemetria de Conexões & Sync', 'cor': '#2980B9'},
        'armazenamento': {'titulo': 'Gestão de Infra & Backups',      'cor': '#1ABC9C'},
        'auditoria':     {'titulo': 'Rastro de Auditoria Master',    'cor': '#7A255F'},
        'versoes':       {'titulo': 'Histórico de Releases',         'cor': '#E67E22'},
        'seguranca':     {'titulo': 'Compliance & Segurança',        'cor': '#C0392B'},
        'developer':     {'titulo': 'Central de Engenharia (Dev)',   'cor': '#7A255F'},
        'documentacao':  {'titulo': 'Central de Documentação',       'cor': '#34495E'}
    }
    
    params = config.get(modulo, config['administracao'])
    
    return render_template('sistema/cards/form_sistema_relatorios.html', 
                           modulo=modulo,
                           titulo=params['titulo'],
                           cor=params['cor'])


