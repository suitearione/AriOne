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
cur.execute("DELETE FROM alembic_version")
cur.execute("INSERT INTO alembic_version (version_num) VALUES (?)", ("006_merge_heads",))
conn.commit()
print("Stamped DB with 006_merge_heads")
conn.close()
