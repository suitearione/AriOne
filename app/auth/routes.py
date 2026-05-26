# =============================================================================
# Caminho  : app/auth/routes.py
# Arquivo  : routes.py
# Função   : Rotas de autenticação do sistema.
# Descrição: Gerencia login em duas etapas (credenciais + seleção de empresa),
#            logout e validação via JSON. Após login bem-sucedido redireciona
#            para o dashboard (gestao.abas). Usa Flask-Login + sessão Flask.
# =============================================================================

from flask import Blueprint, render_template, redirect, url_for, flash, request, session, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app.extensions import db

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    from app.models import Usuario, Empresa

    if current_user.is_authenticated:
        return redirect(url_for('gestao.abas'))

    # ✅ Sem filter_by(ativo=True) e sem order_by(cod_empresa) — campos removidos
    empresas = Empresa.query.order_by(Empresa.razao_social).all()

    if request.method == 'POST':
        # ── Verificação Humana (Segurança Anti-Bot) ──
        h_val1 = request.form.get('h_val1')
        h_val2 = request.form.get('h_val2')
        h_resp = request.form.get('h_resp')
        
        try:
            if not h_resp or int(h_resp) != int(h_val1 or 0) + int(h_val2 or 0):
                flash('Verificação de segurança falhou. Tente novamente.', 'warning')
                return render_template('login/login.html', empresas=empresas)
        except:
            flash('Erro na verificação de segurança.', 'danger')
            return render_template('login/login.html', empresas=empresas)

        email      = request.form.get('email', '').strip().lower()
        senha      = request.form.get('senha', '').strip()
        empresa_id = request.form.get('empresa_id', '').strip()

        from sqlalchemy import func
        user = Usuario.query.filter(func.lower(Usuario.email) == email).first()

        if not user or not user.check_senha(senha):
            flash('E-mail ou senha incorretos.', 'danger')
            return render_template('login/login.html', empresas=empresas)

        if not empresa_id:
            flash('Selecione uma empresa para continuar.', 'warning')
            return render_template('login/login.html', empresas=empresas)

        # ✅ Busca por id (Integer) — sem cod_empresa
        empresa = Empresa.query.get(int(empresa_id))
        if not empresa:
            flash('Empresa inválida.', 'danger')
            return render_template('login/login.html', empresas=empresas)

        login_user(user)
        session['empresa_id']   = empresa.id
        session['nome_empresa'] = empresa.razao_social

        # ✅ Redireciona para o dashboard principal
        return redirect(url_for('gestao.abas'))

    return render_template('login/login.html', empresas=empresas)


@auth_bp.route('/validar-credenciais', methods=['POST'])
def validar_credenciais():
    from app.models import Usuario
    from sqlalchemy import func

    dados = request.get_json()
    email = dados.get('email', '').strip().lower()
    senha = dados.get('senha', '').strip()
    user  = Usuario.query.filter(func.lower(Usuario.email) == email).first()

    if user and user.check_senha(senha):
        return jsonify({'ok': True})
    return jsonify({'ok': False}), 401


@auth_bp.route('/logout')
@login_required
def logout():
    session.pop('empresa_id',   None)
    session.pop('nome_empresa', None)
    logout_user()
    flash('Você saiu do sistema com sucesso.', 'success')
    return redirect(url_for('auth.login'))