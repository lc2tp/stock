
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from models.database import Database

db = Database()
db.connect()

print("=== 找 today_change=9.9267 的板块 ===")
cursor = db.connection.cursor()

cursor.execute("""
    SELECT cd.concept_code, c.concept_name, c.concept_type, cd.date, cd.change_pct, cd.volume 
    FROM concept_daily cd 
    JOIN concept c ON cd.concept_code = c.concept_code 
    WHERE cd.change_pct = 9.9267
""")
rows = cursor.fetchall()
for row in rows:
    print(f"  code={row[0]}, name={row[1]}, type={row[2]}, date={row[3]}, change={row[4]}, volume={row[5]}")

db.close()

