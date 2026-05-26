from app import create_app, db
from app.models.catalogos import CorCatalogo

app = create_app()
with app.app_context():
    try:
        num = CorCatalogo.query.delete()
        db.session.commit()
        print(f"Sucesso: {num} cores removidas do catálogo.")
    except Exception as e:
        db.session.rollback()
        print(f"Erro ao deletar: {str(e)}")
