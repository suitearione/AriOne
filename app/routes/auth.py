
# /app/routes/auth.py
# Modulo de Segurança — autenticação e sessão de usuário

from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from app.extensions import db
from app.models import Usuario

auth_bp = Blueprint('auth', __name__)

# ----------------- BLOCO: VIEW DE LOGIN -----------------
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('gestao.abas'))  # ✅ Corrigido para Gestão Dash

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        senha = request.form.get('senha', '')

        from sqlalchemy import func
        user = Usuario.query.filter(func.lower(Usuario.email) == email).first()

        if user and user.check_senha(senha):
            login_user(user)
            # Define contexto inicial da empresa
            if user.empresa:
                session['empresa_id'] = user.empresa.id
                session['nome_empresa'] = user.empresa.razao_social
                if user.empresa.logo:
                    session['logo_empresa'] = f"img/logo/{user.empresa.logo}"
            elif user.empresas_acesso:
                # Se não tem uma fixa, pega a primeira da lista de acesso
                from app.models.cadastros.empresa import Empresa
                try:
                    primeiro_id = int(user.empresas_acesso.split(',')[0].strip())
                    emp = Empresa.query.get(primeiro_id)
                    if emp:
                        session['empresa_id'] = emp.id
                        session['nome_empresa'] = emp.razao_social
                        if emp.logo:
                            session['logo_empresa'] = f"img/logo/{emp.logo}"
                except: pass

            return redirect(url_for('gestao.abas'))
        else:
            flash('E-mail ou senha incorretos.', 'danger')

    return render_template('login/login.html')

# ----------------- BLOCO: VIEW DE SAÍDA -----------------
@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Você saiu do sistema com sucesso.', 'success')
    return redirect(url_for('auth.login'))