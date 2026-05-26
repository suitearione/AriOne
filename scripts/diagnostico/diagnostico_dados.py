from app import create_app, db
from app.models.comercial.models import TabelaPreco
from app.models.cadastros.funcionario import Funcionario

app = create_app()
with app.app_context():
    tabelas = TabelaPreco.query.all()
    vendedores = Funcionario.query.all()
    
    print(f"Total de Tabelas de Precos: {len(tabelas)}")
    for t in tabelas:
        print(f" - ID: {t.id} | Nome: {t.nome}")
        
    print(f"\nTotal de Funcionarios (Vendedores): {len(vendedores)}")
    for v in vendedores:
        print(f" - ID: {v.id} | Nome: {v.nome} | Cargo: {v.cargo.nome if v.cargo else 'Sem cargo'}")
