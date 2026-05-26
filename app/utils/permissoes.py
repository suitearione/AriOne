# app/utils/permissoes.py
from functools import wraps
from flask import redirect, url_for, flash, request, abort
from flask_login import current_user
import json

"""
MOTOR DE SEGURANÇA ARIONE (PERMISSION ENFORCEMENT)
Gerencia o acesso granular: Visualizar (v), Criar (c), Editar (e), Excluir (x), Exportar (p)
"""

def tem_permissao(modulo, produto, card, acao='v'):
    """
    Verifica se o usuário logado tem uma permissão específica.
    acao: 'v' (visualizar), 'c' (criar), 'e' (editar), 'x' (excluir), 'p' (exportar)
    """
    if not current_user.is_authenticated:
        return False
    
    # Usuário MASTER (ID 1) sempre tem acesso total
    if hasattr(current_user, 'id') and current_user.id == 1:
        return True

    # Se não tiver perfil vinculado, nega por segurança
    if not hasattr(current_user, 'perfil') or not current_user.perfil:
        return False

    permissoes = current_user.perfil.permissoes
    if not permissoes:
        return False

    # Se as permissões forem string, converte para dict
    if isinstance(permissoes, str):
        try:
            permissoes = json.loads(permissoes)
        except:
            return False

    # Chave da matriz: "MÓDULO — Produto"
    chave_matriz = f"{modulo} — {produto}"
    
    if chave_matriz in permissoes:
        config_card = permissoes[chave_matriz].get(card)
        if config_card:
            # Retorna o valor booleano da ação solicitada
            return config_card.get(acao, False)

    return False

def login_required_granular(modulo, produto, card, acao='v'):
    """
    Decorator para proteger rotas (Blueprints).
    Uso: @login_required_granular('CADASTROS', 'Catálogos', 'Produtos', 'v')
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not tem_permissao(modulo, produto, card, acao):
                flash(f"⚠️ Acesso Negado: Você não tem permissão para {acao_nome(acao)} em {card}.", "danger")
                return redirect(url_for('gestao.abas')) # Redireciona para o Dashboard
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def acao_nome(sigla):
    mapa = {'v': 'Visualizar', 'c': 'Criar', 'e': 'Editar', 'x': 'Excluir', 'p': 'Exportar'}
    return mapa.get(sigla, 'Acessar')
