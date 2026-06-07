#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para importar fornecedores de arquivo Excel para banco de dados
"""

import pandas as pd
import os
import sys
from pathlib import Path

# Adiciona o diretório raiz ao PATH
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app import create_app
from app.models.cadastros.fornecedor import Fornecedor
from app.extensions import db

def importar_fornecedores(xls_path):
    """Importa fornecedores do arquivo Excel"""
    
    if not os.path.exists(xls_path):
        print(f"❌ Arquivo não encontrado: {xls_path}")
        return False
    
    try:
        print(f"📖 Lendo arquivo: {xls_path}")
        df = pd.read_excel(xls_path)
        
        print(f"📊 Estrutura: {len(df)} linhas, {len(df.columns)} colunas")
        print(f"📋 Colunas: {list(df.columns)}")
        
        if len(df) == 0:
            print("❌ Arquivo vazio")
            return False
        
        print(f"\n📝 Primeiras 3 linhas:")
        print(df.head(3).to_string())
        
        # Criar app e contexto
        app = create_app()
        
        with app.app_context():
            fornecedores_adicionados = 0
            fornecedores_atualizados = 0
            erros = []
            
            for idx, row in df.iterrows():
                try:
                    # Mapeamento de colunas (ajuste conforme necessário)
                    nome_fantasia = str(row.get('Nome Fantasia', row.get('nome_fantasia', ''))).strip()
                    razao_social = str(row.get('Razão Social', row.get('razao_social', nome_fantasia))).strip()
                    cnpj_cpf = str(row.get('CNPJ/CPF', row.get('cnpj_cpf', ''))).strip()
                    email = str(row.get('E-mail', row.get('email', ''))).strip()
                    telefone = str(row.get('Telefone', row.get('telefone', ''))).strip()
                    whatsapp = str(row.get('WhatsApp', row.get('whatsapp', ''))).strip()
                    contato = str(row.get('Contato', row.get('contato_nome', ''))).strip()
                    categoria = str(row.get('Categoria', row.get('categoria', ''))).strip()
                    
                    # Validação mínima
                    if not razao_social or razao_social == 'nan':
                        erros.append(f"Linha {idx+2}: Razão Social vazia")
                        continue
                    
                    # Buscar fornecedor existente ou criar novo
                    fornecedor = None
                    if cnpj_cpf and cnpj_cpf != 'nan':
                        fornecedor = Fornecedor.query.filter_by(cnpj_cpf=cnpj_cpf).first()
                    
                    if fornecedor:
                        # Atualizar
                        fornecedor.razao_social = razao_social or fornecedor.razao_social
                        fornecedor.nome_fantasia = nome_fantasia or fornecedor.nome_fantasia
                        fornecedor.email = email or fornecedor.email
                        fornecedor.telefone = telefone or fornecedor.telefone
                        fornecedor.whatsapp = whatsapp or fornecedor.whatsapp
                        fornecedor.contato_nome = contato or fornecedor.contato_nome
                        fornecedor.categoria = categoria or fornecedor.categoria
                        fornecedores_atualizados += 1
                        print(f"  ✏️  Atualizado: {razao_social}")
                    else:
                        # Criar novo
                        fornecedor = Fornecedor()
                        fornecedor.razao_social = razao_social
                        fornecedor.nome_fantasia = nome_fantasia or razao_social
                        fornecedor.cnpj_cpf = cnpj_cpf if cnpj_cpf != 'nan' else None
                        fornecedor.email = email if email != 'nan' else None
                        fornecedor.telefone = telefone if telefone != 'nan' else None
                        fornecedor.whatsapp = whatsapp if whatsapp != 'nan' else None
                        fornecedor.contato_nome = contato if contato != 'nan' else None
                        fornecedor.categoria = categoria if categoria != 'nan' else None
                        fornecedor.ativo = True
                        db.session.add(fornecedor)
                        fornecedores_adicionados += 1
                        print(f"  ✅ Adicionado: {razao_social}")
                
                except Exception as e:
                    erros.append(f"Linha {idx+2}: {str(e)}")
                    print(f"  ❌ Erro: {str(e)}")
            
            # Confirmar mudanças
            try:
                db.session.commit()
                print(f"\n✅ Importação concluída:")
                print(f"  ✅ Adicionados: {fornecedores_adicionados}")
                print(f"  ✏️  Atualizados: {fornecedores_atualizados}")
                if erros:
                    print(f"  ⚠️  Erros: {len(erros)}")
                    for erro in erros[:5]:
                        print(f"     - {erro}")
                    if len(erros) > 5:
                        print(f"     ... e mais {len(erros) - 5} erros")
                return True
            except Exception as e:
                db.session.rollback()
                print(f"❌ Erro ao confirmar: {str(e)}")
                return False
    
    except Exception as e:
        print(f"❌ Erro ao processar arquivo: {str(e)}")
        return False

if __name__ == '__main__':
    xls_path = r'c:\Users\Arisvan\Downloads\ListaFornecedores.xls'
    sucesso = importar_fornecedores(xls_path)
    sys.exit(0 if sucesso else 1)
