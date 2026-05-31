from dotenv import load_dotenv
import os, sqlite3
load_dotenv()
from app import create_app
app = create_app()
uri = app.config.get("SQLALCHEMY_DATABASE_URI")
print("DB URI:", uri)
path = uri.replace("sqlite:///", "")
path = os.path.abspath(path)
print("DB path:", path)
conn = sqlite3.connect(path)
cur = conn.cursor()
cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='alembic_version'")
print("exists:", cur.fetchone())
cur.execute("SELECT * FROM alembic_version")
print("rows:", cur.fetchall())
conn.close()
