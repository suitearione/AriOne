from dotenv import load_dotenv
import os, sqlite3
load_dotenv()
from app import create_app
app = create_app()
uri = app.config.get("SQLALCHEMY_DATABASE_URI")
path = uri.replace("sqlite:///", "")
path = os.path.abspath(path)
print("DB path:", path)
conn = sqlite3.connect(path)
cur = conn.cursor()
cur.execute("PRAGMA table_info(campanhas)")
for row in cur.fetchall():
    print(row)
conn.close()
