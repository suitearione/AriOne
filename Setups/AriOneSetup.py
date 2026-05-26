#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
Arquivo  : AriOneSetup.py
Função   : Script de configuração inicial do sistema AriOne.
Descrição: Cria usuário admin padrão e empresa exemplo para primeiro acesso.
           Execute: python AriOneSetup.py
=============================================================================
"""

import sys
import os

# Adiciona o diretório do projeto ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from datetime import datetime, date


def print_header():
    """Exibe cabeçalho do setup."""
    print("\n" + "="*70)
    print("🚀 AriOne ERP - Setup Inicial do Sistema")
    print("="*70 + "\n")


def print_footer():
    """Exibe rodapé com informações de acesso."""
    print("\n" + "="*70)
    print("✅ SETUP CONCLUÍDO COM SUCESSO!")
    print("="*70)
    print("\n📌 DADOS DE ACESSO:")
    print("   URL     : http://127.0.0.1:8081")
    print("   Email   : admin@arione.com.br")
    print("   Senha   : admin123")
    print("\n⚠️  IMPORTANTE: Altere a senha após o primeiro acesso!")
    print("="*70 + "\n")


def importar_todos_modelos():
    """Importa todos os modelos para garantir que as tabelas sejam criadas."""
    print("📚 Importando modelos do sistema...")
    try:
        # Importar TODOS os modelos aqui
        from app.models.usuario import Usuario
        from app.models.cadastros.empresa import Empresa
        from app.models.sistema.versao import Versao
        
        # Adicione outros modelos conforme necessário
        # from app.models.cliente import Cliente
        # from app.models.fornecedor import Fornecedor
        # etc...
        
        print("✅ Modelos importados com sucesso!\n")
        return Usuario, Empresa
        
    except Exception as e:
        print(f"❌ Erro ao importar modelos: {e}\n")
        return None, None


def criar_tabelas(app):
    """Cria todas as tabelas do banco de dados."""
    print("📦 Criando estrutura do banco de dados...")
    try:
        with app.app_context():
            # CRÍTICO: Importar modelos ANTES de create_all
            Usuario, Empresa = importar_todos_modelos()
            
            if not Usuario or not Empresa:
                print("❌ Falha ao importar modelos necessários.\n")
                return False
            
            # Criar todas as tabelas
            db.create_all()
            
            # Verificar se a tabela empresas foi criada
            inspector = db.inspect(db.engine)
            tabelas = inspector.get_table_names()
            
            print(f"📋 Tabelas criadas: {', '.join(tabelas)}")
            
            if 'empresas' not in tabelas:
                print("❌ ERRO: Tabela 'empresas' não foi criada!\n")
                return False
            
            if 'usuarios' not in tabelas:
                print("❌ ERRO: Tabela 'usuarios' não foi criada!\n")
                return False
            
            print("✅ Todas as tabelas criadas com sucesso!\n")
            return True
            
    except Exception as e:
        print(f"❌ Erro ao criar tabelas: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def criar_empresa_padrao(app):
    """Cria empresa padrão se não existir."""
    from app.models.cadastros.empresa import Empresa
    
    with app.app_context():
        # Verificar se já existe empresa
        empresa_exists = Empresa.query.first()
        
        if empresa_exists:
            print("⚠️  Já existe uma empresa cadastrada:")
            print(f"   Razão Social: {empresa_exists.razao_social}")
            resposta = input("   Deseja recriar? (s/N): ").strip().lower()
            
            if resposta != 's':
                print("   ✓ Mantendo empresa existente.\n")
                return empresa_exists
            else:
                db.session.delete(empresa_exists)
                db.session.commit()
        
        # Criar nova empresa
        print("🏢 Criando empresa padrão...")
        try:
            empresa = Empresa(
                razao_social='ARIONE SISTEMAS LTDA',
                nome_fantasia='AriOne ERP',
                area_atuacao_resumo='Desenvolvimento de Software',
                setor_atividade='Tecnologia',
                
                # Documentos
                cnpj='00.000.000/0000-00',
                ie='ISENTO',
                
                # Contato
                whatsapp='(85) 99999-9999',
                email_contato='contato@arione.com.br',
                contato_nome='Administrador',
                contato_tipo='Proprietário',
                
                # Digital
                slug='arione-erp',
                website='https://arione.com.br',
                instagram='@arione.erp',
                
                # Endereço de Faturamento
                end_fat_cep='60000-000',
                end_fat_logradouro='Rua Exemplo',
                end_fat_numero='100',
                end_fat_complemento='Sala 01',
                end_fat_bairro='Centro',
                end_fat_cidade='Fortaleza',
                end_fat_uf='CE',
                
                # Ciclo de Vida
                data_abertura=date.today(),
                ativa=True,
                
                # Fiscal
                nfe_serie='1',
                nfe_ultimo_numero=0,
                nfe_ambiente='2',
                danfe_formato='1'
            )
            
            db.session.add(empresa)
            db.session.commit()
            
            print("✅ Empresa criada com sucesso!")
            print(f"   ID: {empresa.id}")
            print(f"   Razão Social: {empresa.razao_social}")
            print(f"   CNPJ: {empresa.cnpj}\n")
            
            return empresa
            
        except Exception as e:
            print(f"❌ Erro ao criar empresa: {e}\n")
            import traceback
            traceback.print_exc()
            db.session.rollback()
            return None


def criar_usuario_admin(app, empresa):
    """Cria usuário administrador padrão."""
    from app.models.usuario import Usuario
    
    with app.app_context():
        # Verificar se já existe usuário admin
        admin_exists = Usuario.query.filter_by(email='admin@arione.com.br').first()
        
        if admin_exists:
            print("⚠️  Usuário administrador já existe:")
            print(f"   Nome: {admin_exists.nome}")
            print(f"   Email: {admin_exists.email}")
            resposta = input("   Deseja recriar? (s/N): ").strip().lower()
            
            if resposta != 's':
                print("   ✓ Mantendo usuário existente.\n")
                return True
            else:
                db.session.delete(admin_exists)
                db.session.commit()
        
        # Criar novo usuário admin
        print("👤 Criando usuário administrador...")
        try:
            admin = Usuario(
                nome='Administrador do Sistema',
                apelido='Admin',
                email='admin@arione.com.br',
                perfil='admin',
                empresa_id=empresa.id if empresa else None,
                foto='usuarios/avatar.png'
            )
            
            admin.set_password('admin123')
            
            db.session.add(admin)
            db.session.commit()
            
            print("✅ Usuário administrador criado!")
            print(f"   ID: {admin.id}")
            print(f"   Nome: {admin.nome}")
            print(f"   Email: {admin.email}")
            print(f"   Senha: admin123")
            print(f"   Perfil: {admin.perfil}")
            print(f"   Empresa ID: {admin.empresa_id}\n")
            
            return True
            
        except Exception as e:
            print(f"❌ Erro ao criar usuário: {e}\n")
            import traceback
            traceback.print_exc()
            db.session.rollback()
            return False


def verificar_instalacao(app):
    """Verifica se já existem dados no sistema."""
    from app.models.usuario import Usuario
    from app.models.cadastros.empresa import Empresa
    
    with app.app_context():
        try:
            total_usuarios = Usuario.query.count()
            total_empresas = Empresa.query.count()
            
            if total_usuarios > 0 or total_empresas > 0:
                print("⚠️  ATENÇÃO: O sistema já possui dados cadastrados!")
                print(f"   Empresas: {total_empresas}")
                print(f"   Usuários: {total_usuarios}\n")
                
                resposta = input("   Deseja continuar mesmo assim? (s/N): ").strip().lower()
                
                if resposta != 's':
                    print("\n❌ Setup cancelado pelo usuário.\n")
                    return False
        except:
            # Se der erro é porque as tabelas não existem ainda
            pass
        
        return True


def main():
    """Função principal do setup."""
    print_header()
    
    # Criar aplicação Flask
    app = create_app()
    
    # Verificar instalação existente
    if not verificar_instalacao(app):
        sys.exit(0)
    
    # 1. Criar estrutura do banco
    if not criar_tabelas(app):
        print("\n❌ FALHA: Não foi possível criar as tabelas do banco.")
        print("   Verifique se todos os modelos estão sendo importados corretamente.\n")
        sys.exit(1)
    
    # 2. Criar empresa padrão
    empresa = criar_empresa_padrao(app)
    if not empresa:
        print("❌ Não foi possível criar a empresa. Abortando setup.\n")
        sys.exit(1)
    
    # 3. Criar usuário admin
    if not criar_usuario_admin(app, empresa):
        print("❌ Não foi possível criar o usuário. Abortando setup.\n")
        sys.exit(1)
    
    # 4. Sucesso!
    print_footer()
    
    # 5. Perguntar se deseja iniciar o sistema
    iniciar = input("Deseja iniciar o sistema agora? (S/n): ").strip().lower()
    
    if iniciar != 'n':
        print("\n🚀 Iniciando servidor Flask...\n")
        os.system('python main.py')


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Setup interrompido pelo usuário.\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)