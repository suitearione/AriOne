# criar_tabelas.py
# Script para criar todas as tabelas do banco de dados

from app import create_app, db

# Criar aplicação
app = create_app()

# Criar contexto e tabelas
with app.app_context():
    print("🔧 Criando tabelas no banco de dados...")
    
    # Importar todos os models
    from app.models.sistema.versao import Versao
    from app.models.cadastros.empresa import Empresa
    
    # Criar todas as tabelas
    db.create_all()
    
    print("✅ Tabelas criadas com sucesso!")
    print("\nTabelas disponíveis:")
    print("  - versoes")
    print("  - empresas")
    print("\n🚀 Agora você pode iniciar o Flask:")
    print("  flask run")