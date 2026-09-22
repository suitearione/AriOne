# =============================================================================
# Caminho  : app/auth/routes.py
# Arquivo  : routes.py
# Função   : Rotas de autenticação do sistema.
# Descrição: Gerencia login em duas etapas (credenciais + seleção de empresa),
#            logout e validação via JSON. Após login bem-sucedido redireciona
#            para o dashboard (gestao.abas). Usa Flask-Login + sessão Flask.
# =============================================================================

from flask import Blueprint, render_template, redirect, url_for, flash, request, session, jsonify, current_app
from flask_login import login_user, logout_user, login_required, current_user
from app.extensions import db
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from email.message import EmailMessage
import smtplib
import os

auth_bp = Blueprint('auth', __name__)


def _reset_serializer():
    return URLSafeTimedSerializer(
        current_app.config['SECRET_KEY'],
        salt='arione-password-reset'
    )


def _send_reset_email(user, reset_url):
    server = current_app.config.get('MAIL_SERVER') or os.getenv('MAIL_SERVER') or current_app.config.get('SMTP_SERVER') or os.getenv('SMTP_SERVER')
    username = current_app.config.get('MAIL_USERNAME') or os.getenv('MAIL_USERNAME') or current_app.config.get('SMTP_USERNAME') or os.getenv('SMTP_USERNAME')
    password = current_app.config.get('MAIL_PASSWORD') or os.getenv('MAIL_PASSWORD') or current_app.config.get('SMTP_PASSWORD') or os.getenv('SMTP_PASSWORD')
    port = int(current_app.config.get('MAIL_PORT') or os.getenv('MAIL_PORT') or current_app.config.get('SMTP_PORT') or os.getenv('SMTP_PORT') or 587)
    use_tls = str(current_app.config.get('MAIL_USE_TLS') or os.getenv('MAIL_USE_TLS', '1')).lower() in ('1', 'true', 'yes')

    if not server or not username or not password:
        current_app.logger.warning('Recuperação de senha solicitada sem SMTP configurado.')
        return False

    message = EmailMessage()
    message['Subject'] = 'Redefinição de senha AriOne'
    message['From'] = username
    message['To'] = user.email
    message.set_content(
        'Olá,\n\n'
        'Recebemos uma solicitação para redefinir sua senha no AriOne.\n\n'
        f'Use este link em até 30 minutos:\n{reset_url}\n\n'
        'Se você não fez esta solicitação, ignore esta mensagem.\n'
    )

    try:
        with smtplib.SMTP(server, port, timeout=15) as smtp:
            smtp.ehlo()
            if use_tls:
                smtp.starttls()
                smtp.ehlo()
            smtp.login(username, password)
            smtp.send_message(message)
        return True
    except Exception:
        current_app.logger.exception('Falha ao enviar e-mail de recuperação de senha.')
        return False


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


@auth_bp.route('/esqueci-senha', methods=['GET', 'POST'])
def esqueci_senha():
    if request.method == 'POST':
        from app.models import Usuario

        email = request.form.get('email', '').strip().lower()
        user = Usuario.query.filter_by(email=email, ativo=True).first()
        if user:
            token = _reset_serializer().dumps({
                'user_id': user.id,
                'senha_hash': user.senha_hash,
            })
            reset_url = url_for('auth.redefinir_senha', token=token, _external=True)
            if _send_reset_email(user, reset_url):
                flash('Se o e-mail estiver cadastrado, enviaremos as instruções de recuperação.', 'info')
            else:
                flash('Não foi possível enviar o e-mail de recuperação. Verifique a configuração SMTP.', 'danger')
                current_app.logger.error('Falha no envio de recuperação para o usuário %s.', user.id)
                return redirect(url_for('auth.esqueci_senha'))
        else:
            flash('Se o e-mail estiver cadastrado, enviaremos as instruções de recuperação.', 'info')

        return redirect(url_for('auth.esqueci_senha'))

    return render_template('login/esqueci_senha.html')


@auth_bp.route('/redefinir-senha/<token>', methods=['GET', 'POST'])
def redefinir_senha(token):
    try:
        payload = _reset_serializer().loads(token, max_age=1800)
    except SignatureExpired:
        flash('O link de recuperação expirou. Solicite um novo link.', 'warning')
        return redirect(url_for('auth.esqueci_senha'))
    except BadSignature:
        flash('O link de recuperação é inválido.', 'danger')
        return redirect(url_for('auth.esqueci_senha'))

    from app.models import Usuario
    user = Usuario.query.filter_by(id=payload.get('user_id'), ativo=True).first()
    if not user or user.senha_hash != payload.get('senha_hash'):
        flash('O link de recuperação não é mais válido. Solicite um novo link.', 'warning')
        return redirect(url_for('auth.esqueci_senha'))

    if request.method == 'POST':
        senha = request.form.get('senha', '')
        confirmacao = request.form.get('confirmacao', '')
        if len(senha) < 8:
            flash('A nova senha deve ter pelo menos 8 caracteres.', 'danger')
        elif senha != confirmacao:
            flash('As senhas não coincidem.', 'danger')
        else:
            user.set_password(senha)
            db.session.commit()
            flash('Senha redefinida com sucesso. Faça login novamente.', 'success')
            return redirect(url_for('auth.login'))

    return render_template('login/redefinir_senha.html', token=token)


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