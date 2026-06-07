"""
Importador de fornecedores a partir de um arquivo Excel (XLS/XLSX).
Uso: python scripts/import_fornecedores.py "C:/Users/Arisvan/Downloads/ListaFornecedores.xls"

O script tenta usar pandas para ler o arquivo; se não disponível, pede instalação.
Aplica mapeamento heurístico de colunas e insere na tabela `fornecedores` do SQLite em instance/arione.db.
Faz checagem de duplicidade por `cnpj_cpf`.
"""
import sys
import os
import unicodedata
import sqlite3
import uuid
import json

FILE = sys.argv[1] if len(sys.argv) > 1 else r"C:\Users\Arisvan\Downloads\ListaFornecedores.xls"
DB = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'instance', 'arione.db') if os.path.exists(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'instance', 'arione.db')) else os.path.join(os.getcwd(), 'instance', 'arione.db')

if not os.path.exists(FILE):
    print(json.dumps({'error': 'file_not_found', 'path': FILE}))
    sys.exit(1)

try:
    import pandas as pd
except Exception as e:
    print(json.dumps({'error': 'pandas_missing', 'message': str(e), 'install': 'pip install pandas openpyxl xlrd'}))
    sys.exit(2)

try:
    df = pd.read_excel(FILE)
except Exception as e:
    print(json.dumps({'error': 'read_failed', 'message': str(e)}))
    sys.exit(3)

# normalize column names
cols = [c.strip() for c in df.columns.astype(str)]
print(json.dumps({'ok': True, 'columns': cols}, ensure_ascii=False))

# heurística de mapeamento (mapa: model_field -> df column)
lower_cols = {c.lower(): c for c in cols}

def _normalize(s):
    if not s:
        return ''
    s = str(s)
    s = unicodedata.normalize('NFKD', s)
    s = ''.join(ch for ch in s if not unicodedata.combining(ch))
    return s.lower().strip()

# mapa: normalized_lower_col -> original column name
norm_cols = {_normalize(c): c for c in cols}

def find_candidate(names):
    """Procura por candidate nos nomes - compara sem acento e por substring"""
    # busca exata por normalização
    for n in names:
        key = _normalize(n)
        if key in norm_cols:
            return norm_cols[key]

    # busca por substring em ambos sentidos
    for n in names:
        n_key = _normalize(n)
        for col_key in norm_cols:
            if n_key in col_key or col_key in n_key:
                return norm_cols[col_key]

    return None

mapping = {
    'cnpj_cpf': find_candidate(['cnpj_cpf','cnpj','cpf','cnpj/cpf','cnpj_cpf ','c n p j']),
    'razao_social': find_candidate(['razao_social','razao social','razao','empresa','nome_razao','nome','nome/razao social','nome/razao','nome/razao social','nome/razão social','nome/razão']),
    'nome_fantasia': find_candidate(['nome_fantasia','fantasia','nome fantasia','nome_fantasia ','apelido','apelido/nome fantasia','apelido nome fantasia','apelido/nome fantasia','apelido/nome','apelido/nome fantasia']),
    'contato_nome': find_candidate(['contato','contato_nome','contato nome','responsavel','contato nome ','responsável','responsavel']),
    'whatsapp': find_candidate(['whatsapp','telefone_whatsapp','celular','celular1','telefone celular','mobile']),
    'telefone': find_candidate(['telefone','phone','tel','fone']),
    'email': find_candidate(['email','e-mail','e mail','e_mail']),
    'end_cep': find_candidate(['cep']),
    'end_logradouro': find_candidate(['logradouro','endereco','end_logradouro','endereço','endereco rua','rua','address']),
    'end_numero': find_candidate(['numero','número','end_numero','num']),
    'end_bairro': find_candidate(['bairro']),
    'end_cidade': find_candidate(['cidade','city']),
    'end_uf': find_candidate(['uf','estado','estado sigla']),
    'observacoes': find_candidate(['observacoes','observação','obs','descricao','descricao dos fornecedores']),
}

print(json.dumps({'mapping_suggested': mapping}, ensure_ascii=False))

# prepare inserts
conn = sqlite3.connect(DB)
cur = conn.cursor()

insert_cols = [
    'tipo_pessoa','razao_social','nome_fantasia','cnpj_cpf','ie_rg','data_abertura',
    'contato_nome','contato_cargo','whatsapp','telefone','email','website',
    'categoria','avaliacao','prazo_entrega',
    'end_cep','end_logradouro','end_numero','end_complemento','end_bairro','end_cidade','end_uf',
    'prazo_pagamento','forma_pagamento','moeda',
    'banco_nome','banco_codigo','banco_agencia','banco_conta','banco_tipo','pix_tipo','pix_chave',
    'observacoes','is_fp','ativo'
]

added = 0
skipped = 0
errors = []

for idx, row in df.iterrows():
    def val(key):
        col = mapping.get(key)
        if col and col in df.columns:
            v = row[col]
            if pd.isna(v): return None
            return str(v).strip()
        return None

    def val_cnpj_any():
        # tenta coluna mapeada primeiro
        v = val('cnpj_cpf')
        if v:
            return v
        # tenta qualquer coluna que contenha 'cpf' ou 'cnpj'
        for nkey, orig in norm_cols.items():
            if 'cpf' in nkey or 'cnpj' in nkey:
                v2 = row[orig]
                if not pd.isna(v2) and str(v2).strip():
                    return str(v2).strip()
        return None

    cnpj = val_cnpj_any() or ''
    cnpj = ''.join(ch for ch in cnpj if ch.isdigit())
    if not cnpj:
        # gerar identificador único para registros sem documento
        cnpj = f'NOID_{idx}_{uuid.uuid4().hex[:8]}'

    # preparar um dicionário de valores para colunas
    row_values = {}
    for c in insert_cols:
        if c == 'razao_social':
            row_values[c] = val('razao_social') or val('nome_fantasia') or None
        elif c == 'nome_fantasia':
            row_values[c] = val('nome_fantasia') or None
        elif c == 'contato_nome':
            row_values[c] = val('contato_nome') or None
        elif c == 'whatsapp':
            row_values[c] = val('whatsapp') or None
        elif c == 'telefone':
            row_values[c] = val('telefone') or None
        elif c == 'email':
            row_values[c] = val('email') or None
        elif c == 'end_cep':
            row_values[c] = val('end_cep') or None
        elif c == 'end_logradouro':
            row_values[c] = val('end_logradouro') or None
        elif c == 'end_numero':
            row_values[c] = val('end_numero') or None
        elif c == 'end_bairro':
            row_values[c] = val('end_bairro') or None
        elif c == 'end_cidade':
            row_values[c] = val('end_cidade') or None
        elif c == 'end_uf':
            row_values[c] = val('end_uf') or None
        elif c == 'observacoes':
            row_values[c] = val('observacoes') or None
        elif c == 'cnpj_cpf':
            row_values[c] = cnpj
        else:
            row_values[c] = None

    try:
        # verificar existência
        cur.execute('SELECT id FROM fornecedores WHERE cnpj_cpf = ?', (cnpj,))
        existing = cur.fetchone()
        if existing:
            # atualizar somente campos não nulos (para não sobrescrever dados existentes)
            set_parts = []
            set_values = []
            for k, v in row_values.items():
                if k == 'cnpj_cpf':
                    continue
                if v is not None and v != '':
                    set_parts.append(f"{k} = ?")
                    set_values.append(v)
            if set_parts:
                set_values.append(existing[0])
                cur.execute('UPDATE fornecedores SET ' + ','.join(set_parts) + ' WHERE id = ?', set_values)
                added += 1
            else:
                skipped += 1
        else:
            # insert - manter None para campos ausentes (inserirá NULL no SQLite)
            insert_vals = [row_values.get(c) for c in insert_cols]
            placeholders = ','.join(['?'] * len(insert_cols))
            cur.execute('INSERT INTO fornecedores (' + ','.join(insert_cols) + ') VALUES (' + placeholders + ')', insert_vals)
            added += 1
    except Exception as e:
        errors.append({'idx': int(idx), 'error': str(e)})

conn.commit()
conn.close()

print(json.dumps({'result':'done','added':added,'skipped':skipped,'errors':errors}, ensure_ascii=False))
