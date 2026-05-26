from app import create_app, db
from sqlalchemy import text

app = create_app()
with app.app_context():
    print("Iniciando correção de colunas das tabelas comerciais...")
    
    correcoes = {
        'comercial_revendedores': [
            ('whatsapp', 'VARCHAR(20)'),
            ('foto', 'VARCHAR(255)'),
            ('categoria', 'VARCHAR(50)'),
            ('tipo_revenda', 'VARCHAR(50)'),
            ('comissao', 'FLOAT DEFAULT 0.0')
        ],
        'comercial_influenciadores': [
            ('handle', 'VARCHAR(50)'),
            ('nicho', 'VARCHAR(50)'),
            ('alcance', 'INTEGER'),
            ('seguidores', 'VARCHAR(20)'),
            ('whatsapp', 'VARCHAR(20)'),
            ('email', 'VARCHAR(100)'),
            ('instagram', 'VARCHAR(100)'),
            ('plataforma', 'VARCHAR(50)'),
            ('foto', 'VARCHAR(255)'),
            ('status_contrato', 'VARCHAR(20) DEFAULT "ATIVO"')
        ],
        'comercial_estilistas': [
            ('especialidade', 'VARCHAR(100)'),
            ('portfólio_url', 'VARCHAR(255)'),
            ('whatsapp', 'VARCHAR(20)'),
            ('email', 'VARCHAR(100)'),
            ('foto', 'VARCHAR(255)'),
            ('disponibilidade', 'VARCHAR(50)')
        ]
    }

    for tabela, colunas in correcoes.items():
        for col, tipo in colunas:
            try:
                db.session.execute(text(f"ALTER TABLE {tabela} ADD COLUMN {col} {tipo}"))
                db.session.commit()
                print(f"[✅] {tabela}: Coluna '{col}' adicionada.")
            except Exception as e:
                db.session.rollback()
                # Provavelmente a coluna já existe
                pass

    print("\n[✨] Correção concluída!")
