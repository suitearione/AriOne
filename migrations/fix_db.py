import sqlite3

conn = sqlite3.connect('instance/arione.db')
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '_alembic_tmp%'")
tabelas_temp = cursor.fetchall()
print("Tabelas temporarias encontradas:", tabelas_temp)

for t in tabelas_temp:
    cursor.execute("DROP TABLE IF EXISTS " + t[0])
    print("Removida:", t[0])

conn.commit()
conn.close()
print("OK")