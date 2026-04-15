
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from models.database import Database

db = Database()
db.connect()

print("=== 调试钴板块的数据 ===")
cursor = db.connection.cursor()

# 先看看钴有哪些concept_code
cursor.execute("""
    SELECT DISTINCT cd.concept_code, c.concept_name 
    FROM concept_daily cd 
    JOIN concept c ON cd.concept_code = c.concept_code 
    WHERE c.concept_name LIKE '%钴%'
""")
codes = cursor.fetchall()
print(f"钴相关的concept_code:")
for code, name in codes:
    print(f"  {code}: {name}")

# 检查第一个concept_code的数据
if codes:
    code_to_check = codes[0][0]
    print(f"\n检查 {code_to_check} 的数据:")
    cursor.execute("""
        SELECT cd.date, cd.change_pct, cd.volume 
        FROM concept_daily cd 
        WHERE cd.concept_code = ?
        ORDER BY cd.date DESC
    """, (code_to_check,))
    rows = cursor.fetchall()
    for row in rows:
        print(f"  {row[0]}: change={row[1]}, volume={row[2]}")

db.close()

