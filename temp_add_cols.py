from dotenv import load_dotenv
import os, sqlite3
load_dotenv()
from app import create_app
app = create_app()
uri = app.config.get("SQLALCHEMY_DATABASE_URI")
path = uri.replace("sqlite:///", "")
path = os.path.abspath(path)
conn = sqlite3.connect(path)
cur = conn.cursor()
try:
    cur.execute("ALTER TABLE campanhas ADD COLUMN valor_diario NUMERIC(16, 2) DEFAULT 0.0")
    print("Added valor_diario")
except Exception as e:
    print("valor_diario error:", e)
try:
    cur.execute("ALTER TABLE campanhas ADD COLUMN data_final DATE")
    print("Added data_final")
except Exception as e:
    print("data_final error:", e)
conn.commit()
conn.close()
