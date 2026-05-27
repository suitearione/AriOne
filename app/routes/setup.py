# =============================================================================
# Caminho  : app/routes/setup.py
# Arquivo  : setup.py
# Função   : Rota de configuração inicial do sistema.
# Descrição: Executada apenas uma vez na primeira execução. Cria o registro
#            da Empresa e o usuário administrador no banco. Redireciona para
#            login se o setup já foi concluído anteriormente.
# =============================================================================

from flask import Blueprint, render_template, redirect, url_for, flash, request
from app.extensions import db

setup_bp = Blueprint('setup', __name__)


@setup_bp.route('/setup')
def index():
    from app.models import Empresa
    if Empresa.query.first():
        return redirect(url_for('auth.login'))
    return render_template('setup/setup.html', erro_admin=False, concluido=False)


@setup_bp.route('/setup/salvar', methods=['POST'])
def salvar():
    from app.models import Empresa, Usuario

    if Empresa.query.first():
        return redirect(url_for('auth.login'))

    razao_social        = request.form.get('razao_social', '').strip()
    nome_fantasia       = request.form.get('nome_fantasia', '').strip()
    cnpj                = request.form.get('cnpj', '').strip()
    ie                  = request.form.get('ie', '').strip()
    telefone            = request.form.get('telefone', '').strip()
    email_empresa       = request.form.get('email_empresa', '').strip()
    endereco            = request.form.get('endereco', '').strip()
    admin_nome          = request.form.get('admin_nome', '').strip()
    admin_email         = request.form.get('admin_email', '').strip()
    admin_senha         = request.form.get('admin_senha', '').strip()
    admin_senha_confirm = request.form.get('admin_senha_confirm', '').strip()

    # ── Validações ──
    if not razao_social or not cnpj:
        flash('Razão Social e CNPJ são obrigatórios.', 'danger')
        return render_template('setup/setup.html', erro_admin=False, concluido=False)

    if not admin_nome or not admin_email or not admin_senha:
        flash('Preencha todos os dados do administrador.', 'danger')
        return render_template('setup/setup.html', erro_admin=True, concluido=False)

    if admin_senha != admin_senha_confirm:
        flash('As senhas não coincidem.', 'danger')
        return render_template('setup/setup.html', erro_admin=True, concluido=False)

    if len(admin_senha) < 6:
        flash('A senha deve ter no mínimo 6 caracteres.', 'danger')
        return render_template('setup/setup.html', erro_admin=True, concluido=False)

    # ── Cria Empresa ──
    try:
        empresa = Empresa(
            razao_social       = razao_social,
            nome_fantasia      = nome_fantasia,
            cnpj               = cnpj,
            ie                 = ie,
            whatsapp           = telefone,        # campo telefone → whatsapp
            email_contato      = email_empresa,   # campo email_empresa → email_contato
            end_fat_logradouro = endereco,        # campo endereco → end_fat_logradouro
        )
        db.session.add(empresa)
        db.session.flush()  # garante empresa.id antes de criar o admin

        # ── Cria Usuário Admin ──
        admin = Usuario(
            nome       = admin_nome,
            email      = admin_email,
            empresa_id = empresa.id,  # ✅ FK correta
            perfil     = 'admin',
        )
        admin.set_password(admin_senha)
        db.session.add(admin)
        db.session.commit()

        return redirect(url_for('setup.concluido'))
    except Exception as e:
        db.session.rollback()
        import traceback
        tb = traceback.format_exc()
        print(f"SETUP ERROR: {tb}")
        return f"<pre>Erro no setup:\n{tb}</pre>", 500


@setup_bp.route('/setup/concluido')
def concluido():
    from app.models import Empresa
    if not Empresa.query.first():
        return redirect(url_for('setup.index'))
    return render_template('setup/setup.html', erro_admin=False, concluido=True)