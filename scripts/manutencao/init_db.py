# init_db.py (RAIZ)
import os
from pathlib import Path
from app import create_app
from app.extensions import db
from app.models.cadastros.empresa import Empresa
from app.models.usuario import Usuario

BASE_DIR      = Path(__file__).resolve().parent
INSTANCE_PATH = BASE_DIR / 'instance'

if not INSTANCE_PATH.exists():
    os.makedirs(INSTANCE_PATH)
    print(f"Pasta 'instance/' criada em: {INSTANCE_PATH}")

app = create_app()

with app.app_context():
    print("Criando/atualizando tabelas no banco de dados...")
    db.create_all()
    print("✅ Banco atualizado com sucesso!")
    print("   Tabelas: empresa, usuarios")