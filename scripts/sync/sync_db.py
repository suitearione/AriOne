from app import create_app, db
from app.models.cadastros.empresa import EmpresaContato

app = create_app()
with app.app_context():
    db.create_all()
    print("Tabelas sicronizadas com sucesso!")
