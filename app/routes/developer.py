# =============================================================================
# Caminho  : app/routes/developer.py
# Arquivo  : developer.py
# Função   : Módulo DEVELOPER — Ambiente exclusivo para desenvolvedores.
# Descrição: Centraliza ferramentas de deploy, laboratório DEV e grid
#            de desenvolvimento, separado dos módulos normais do sistema.
# =============================================================================

from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from flask_login import login_required
import json as _json
import os
import requests

# ── Constantes do Módulo ──────────────────────────────────────────────────
developer_bp = Blueprint('developer', __name__, url_prefix='/developer')

# Arquivo de progresso DEV
PROGRESSO_DEV_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'data', 'progresso_dev.json')

# Arquivo de configuração do Render
RENDER_CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'data', 'render_config.json')

def _ler_render_config():
    try:
        os.makedirs(os.path.dirname(RENDER_CONFIG_FILE), exist_ok=True)
        if os.path.exists(RENDER_CONFIG_FILE):
            with open(RENDER_CONFIG_FILE, 'r', encoding='utf-8') as f:
                return _json.load(f)
    except Exception:
        pass
    return {'webhook_url': ''}

def _salvar_render_config(config):
    os.makedirs(os.path.dirname(RENDER_CONFIG_FILE), exist_ok=True)
    with open(RENDER_CONFIG_FILE, 'w', encoding='utf-8') as f:
        _json.dump(config, f, ensure_ascii=False)

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


# =============================================================================
# 🔹 ABA MESTRE (Navegação por Abas)
# =============================================================================
@developer_bp.route('/abas')
@login_required
def abas():
    """Módulo DEVELOPER — Deploy, Lab DEV e Developer Grid"""
    aba_ativa = request.args.get('aba', 'deploy')

    lista_abas = [
        {'id': 'deploy',    'label': 'Deploy',    'icon': 'fas fa-rocket'},
        {'id': 'developer', 'label': 'Developer', 'icon': 'fas fa-laptop-code'},
        {'id': 'lab_dev',   'label': 'Lab DEV',   'icon': 'fas fa-flask'},
    ]

    # Dados para a aba Deploy
    deploy_data = {
        'servicos': [
            {
                'nome': 'suitearione',
                'branch': 'main',
                'url': 'https://suitearione.onrender.com',
                'status': 'ativo',
                'banco': 'arione-db',
                'descricao': 'Ambiente de Produção'
            }
        ],
        'repos': [
            {'nome': 'main',    'desc': 'Ambiente de produção (PROD)'}
        ]
    }

    return render_template(
        'developer/abas_developer.html',
        abas=lista_abas,
        aba_ativa=aba_ativa,
        deploy_data=deploy_data
    )


@developer_bp.route('/deploy')
@login_required
def deploy():
    return redirect(url_for('developer.abas', aba='deploy'))


@developer_bp.route('/developer')
@login_required
def developer():
    return redirect(url_for('developer.abas', aba='developer'))


@developer_bp.route('/lab-dev')
@login_required
def lab_dev():
    return redirect(url_for('developer.abas', aba='lab_dev'))


# =============================================================================
# 🔹 CARDS (Formulários Dinâmicos via AJAX)
# =============================================================================
@developer_bp.route('/cards/deploy/servidor')
@login_required
def card_deploy_servidor():
    """Card: Deploy Servidor — Status dos serviços no Render"""
    servicos = [
        {
            'nome': 'suitearione-dev',
            'branch': 'develop',
            'url': 'https://suitearione-dev.onrender.com',
            'status': 'ativo',
            'banco': 'arione-dev-db',
            'tipo': 'Desenvolvimento'
        },
        {
            'nome': 'suitearione',
            'branch': 'main',
            'url': 'https://suitearione.onrender.com',
            'status': 'ativo',
            'banco': 'arione-db',
            'tipo': 'Produção'
        }
    ]
    return render_template('developer/cards/deploy/card_deploy_servidor.html', servicos=servicos)


@developer_bp.route('/cards/deploy/branches')
@login_required
def card_deploy_branches():
    """Card: Branches — develop vs main"""
    branches = [
        {
            'nome': 'develop',
            'desc': 'Desenvolvimento — testes online antes de ir para PROD',
            'url': 'https://suitearione-dev.onrender.com',
            'acao': 'git push origin develop'
        },
        {
            'nome': 'main',
            'desc': 'Principal — Produção real dos usuários',
            'url': 'https://suitearione.onrender.com',
            'acao': 'git checkout main && git merge develop && git push origin main'
        }
    ]
    return render_template('developer/cards/deploy/card_deploy_branches.html', branches=branches)


@developer_bp.route('/cards/developer/cores')
@login_required
def card_developer_cores():
    """Card: Laboratório de Cores do Padrão Ouro"""
    from app.utils.sistema_matriz import ARIONE_MODULOS
    is_modal = request.args.get('modal') == '1'
    return render_template('developer/cards/form_developer_cores.html', modulos=ARIONE_MODULOS, is_modal=is_modal)


@developer_bp.route('/cards/developer/vendas-premium')
@login_required
def card_developer_vendas_premium():
    """Card: Protótipo Vendas Premium"""
    is_modal = request.args.get('modal') == '1'
    return render_template('developer/cards/form_developer_vendas_premium.html', is_modal=is_modal)


@developer_bp.route('/cards/documentacao')
@login_required
def card_documentacao():
    """Card: Central de Documentação"""
    return render_template('developer/cards/form_documentacao.html')


@developer_bp.route('/api/progresso-dev/toggle', methods=['POST'])
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


@developer_bp.route('/api/progresso-dev/status', methods=['GET'])
@login_required
def api_progresso_dev_status():
    """Retorna o estado de todos os cards marcados como prontos."""
    return jsonify(_ler_progresso())


@developer_bp.route('/api/trigger-deploy', methods=['POST'])
@login_required
def api_trigger_deploy():
    """Trigger deploy automático no Render via Webhook (mais seguro)"""
    # Prioridade: variável de ambiente > arquivo de configuração
    render_webhook_url = os.environ.get('RENDER_WEBHOOK_URL') or _ler_render_config().get('webhook_url')
    
    if not render_webhook_url:
        return jsonify({
            'erro': 'Webhook do Render não configurado',
            'detalhes': 'Configure o webhook na aba Deploy'
        }), 400
    
    try:
        response = requests.post(render_webhook_url, timeout=10)
        
        if response.status_code in [200, 201, 202]:
            return jsonify({
                'ok': True,
                'mensagem': 'Deploy iniciado com sucesso via webhook'
            })
        else:
            return jsonify({
                'erro': 'Erro ao iniciar deploy',
                'status': response.status_code,
                'detalhes': response.text
            }), response.status_code
            
    except Exception as e:
        return jsonify({
            'erro': 'Erro ao conectar com webhook do Render',
            'detalhes': str(e)
        }), 500


@developer_bp.route('/api/render-config', methods=['GET'])
@login_required
def api_get_render_config():
    """Retorna a configuração atual do Render"""
    config = _ler_render_config()
    # Não retornar a URL completa por segurança, apenas se está configurada
    return jsonify({
        'configurado': bool(config.get('webhook_url')),
        'url_preview': config.get('webhook_url', '')[:30] + '...' if config.get('webhook_url') else ''
    })


@developer_bp.route('/api/render-config', methods=['POST'])
@login_required
def api_save_render_config():
    """Salva a configuração do webhook do Render"""
    dados = request.get_json()
    webhook_url = dados.get('webhook_url', '').strip()
    
    if not webhook_url:
        return jsonify({'erro': 'URL do webhook é obrigatória'}), 400
    
    # Validação básica da URL
    if not webhook_url.startswith('https://'):
        return jsonify({'erro': 'URL deve começar com https://'}), 400
    
    _salvar_render_config({'webhook_url': webhook_url})
    
    return jsonify({
        'ok': True,
        'mensagem': 'Configuração salva com sucesso'
    })
