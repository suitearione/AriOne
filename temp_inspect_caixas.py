import sqlite3, os
path = os.path.join('instance', 'arione.db')
conn = sqlite3.connect(path)
cur = conn.cursor()
rows = cur.execute('SELECT id, nome, formas_pagamento_ids, formas_pagamento_detalhes FROM financeiro_caixas ORDER BY id').fetchall()
for row in rows:
    print(row)
conn.close()
