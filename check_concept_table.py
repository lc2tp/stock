
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from models.database import Database

db = Database()
db.connect()

print("=== concept 表结构 ===")
cursor = db.connection.cursor()
cursor.execute("PRAGMA table_info(concept)")
columns = cursor.fetchall()
for c in columns:
    print(f"  {c[1]} ({c[2]})")

print("\n=== concept_daily 表结构 ===")
cursor.execute("PRAGMA table_info(concept_daily)")
columns = cursor.fetchall()
for c in columns:
    print(f"  {c[1]} ({c[2]})")

db.close()

