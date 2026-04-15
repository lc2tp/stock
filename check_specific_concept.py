
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from models.database import Database

db = Database()
db.connect()

print("=== 检查钴和印制电路板板块的数据 ===")
cursor = db.connection.cursor()

# 搜索这两个板块
concept_names = ['钴', '印制电路板']

for name in concept_names:
    print(f"\n--- {name} ---")
    cursor.execute("""
        SELECT cd.concept_code, c.concept_name, cd.date, cd.change_pct, cd.volume 
        FROM concept_daily cd 
        JOIN concept c ON cd.concept_code = c.concept_code 
        WHERE c.concept_name LIKE ?
        ORDER BY cd.date DESC
        LIMIT 10
    """, (f'%{name}%',))
    rows = cursor.fetchall()
    if rows:
        for row in rows:
            print(f"  {row[2]}: change_pct={row[3]}, volume={row[4]}")
    else:
        print("  未找到数据")

db.close()

