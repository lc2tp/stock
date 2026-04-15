
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from models.database import Database

db = Database()
db.connect()

print("=== 检查concept_daily表数据 ===")
cursor = db.connection.cursor()

cursor.execute("SELECT cd.concept_code, c.concept_name, cd.date, cd.change_pct, cd.volume FROM concept_daily cd JOIN concept c ON cd.concept_code = c.concept_code ORDER BY cd.date DESC LIMIT 10")
rows = cursor.fetchall()
print("最近10条数据:")
for row in rows:
    print(f"  日期: {row[2]}, 板块: {row[1]}, 涨跌幅: {row[3]}, 成交额: {row[4]}")

db.close()

