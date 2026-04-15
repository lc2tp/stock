
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from models.database import Database

db = Database()
db.connect()

print("=== 检查为什么volume是None ===")
cursor = db.connection.cursor()

# 获取最近的一个日期
cursor.execute("SELECT DISTINCT date FROM concept_daily ORDER BY date DESC LIMIT 1")
latest_date = cursor.fetchone()[0]
print(f"最新日期: {latest_date}")

# 检查这个日期的数据
cursor.execute("""
    SELECT cd.concept_code, c.concept_name, cd.date, cd.change_pct, cd.volume 
    FROM concept_daily cd 
    JOIN concept c ON cd.concept_code = c.concept_code 
    WHERE cd.date = ?
    LIMIT 20
""", (latest_date,))
rows = cursor.fetchall()
print(f"\n{latest_date} 的数据:")
for row in rows:
    print(f"  {row[1]}: change_pct={row[3]}, volume={row[4]}")

print("\n=== 检查get_concept_daily返回 ===")
all_data = db.get_concept_daily(latest_date, latest_date)
print(f"get_concept_daily返回了 {len(all_data)} 条数据")
for i, item in enumerate(all_data[:20]):
    print(f"  {i+1}. {item['concept_name']}: volume={item.get('volume')}")

db.close()

