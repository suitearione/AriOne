from app import create_app
import sqlite3, os

app = create_app()
uri = app.config.get('SQLALCHEMY_DATABASE_URI')
print('DB URI:', uri)
if uri.startswith('sqlite:///'):
    path = uri.replace('sqlite:///', '')
    if not os.path.isabs(path):
        path = os.path.abspath(path)
    print('DB path:', path)
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    cur.execute("PRAGMA table_info('op_compras_pedidos')")
    cols = cur.fetchall()
    print('Columns count:', len(cols))
    for c in cols:
        if c[1] in ('condicao_pagamento', 'condicoes_pagamento'):
            print(c)
    conn.close()
