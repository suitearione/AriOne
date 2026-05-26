# =============================================================================
# Caminho  : app/utils/avisos.py
# Arquivo  : avisos.py
# Função   : Sistema de Notificações e Alertas (Bandeja do Usuário).
# =============================================================================

from app.extensions import db
from datetime import datetime

# Nota: Assumindo que a tabela Notificacao existe ou será criada.
# Se não existir, vou definir o modelo aqui para fins de demonstração ou criar o arquivo de modelo.

class Notificacao(db.Model):
    __tablename__ = 'sys_notificacoes'
    id = db.Column(db.Integer, primary_key=True)
    empresa_id = db.Column(db.Integer, db.ForeignKey('empresas.id'))
    
    setor_destino = db.Column(db.String(50)) # Financeiro, Compras, Producao, Sistema
    titulo = db.Column(db.String(100))
    mensagem = db.Column(db.Text)
    
    lida = db.Column(db.Boolean, default=False)
    data_criacao = db.Column(db.DateTime, default=datetime.now)
    
    link_acao = db.Column(db.String(255)) # URL para clicar e ir ao registro

def enviar_aviso(empresa_id, setor, titulo, mensagem, link=None):
    """Envia uma notificação para a bandeja do setor correspondente."""
    try:
        nova_notif = Notificacao(
            empresa_id=empresa_id,
            setor_destino=setor,
            titulo=titulo,
            mensagem=mensagem,
            link_acao=link
        )
        db.session.add(nova_notif)
        db.session.commit()
        return True
    except Exception as e:
        print(f"Erro ao enviar aviso: {e}")
        db.session.rollback()
        return False
