from app import create_app, db
from app.models.cadastros.empresa import Empresa

app = create_app()
with app.app_context():
    empresas = Empresa.query.all()
    print('EMPRESAS CADASTRADAS:')
    print('=' * 60)
    for e in empresas:
        print(f'ID: {e.id} | Razão Social: {e.razao_social} | Nome Fantasia: {e.nome_fantasia}')
