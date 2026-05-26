import os
import sys

# Adiciona o diretório raiz ao path para encontrar a app
sys.path.append(os.getcwd())

from app import create_app
from app.extensions import db
from app.models.cadastros.configuracao import ParametroSistema

app = create_app()
with app.app_context():
    print("\n=== DIAGNÓSTICO DE PARÂMETROS ARIONE ===")
    params = ParametroSistema.query.all()
    if not params:
        print("⚠️ NENHUM PARÂMETRO ENCONTRADO NO BANCO!")
    else:
        for p in params:
            print(f"Grupo: {p.grupo:10} | Chave: {p.chave:30} | Valor: {p.valor}")
    print("========================================\n")
