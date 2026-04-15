
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from models.database import Database

db = Database()
db.connect()

print("=== 调试代码为884284的板块 ===")

code = '884284'

# 获取这个板块的所有数据
cursor = db.connection.cursor()
cursor.execute("""
    SELECT cd.date, cd.change_pct, cd.volume, c.concept_name, c.concept_type
    FROM concept_daily cd 
    JOIN concept c ON cd.concept_code = c.concept_code 
    WHERE cd.concept_code = ?
    ORDER BY cd.date DESC
""", (code,))
rows = cursor.fetchall()

print(f"板块名称: {rows[0][3] if rows else 'N/A'}")
print(f"板块类型: {rows[0][4] if rows else 'N/A'}")
print(f"\n所有日期数据:")
for row in rows:
    print(f"  {row[0]}: change={row[1]}, volume={row[2]}")

# 构建 concept_data 结构
concept_dates = db.get_concept_dates()
data = {
    'concept_code': code,
    'concept_name': rows[0][3],
    'concept_type': rows[0][4],
    'daily_change': {},
    'daily_volume': {}
}
for row in rows:
    data['daily_change'][row[0]] = row[1]
    data['daily_volume'][row[0]] = row[2]

print(f"\ndaily_change keys: {sorted(data['daily_change'].keys(), reverse=True)[:5]}")
print(f"daily_volume keys: {sorted(data['daily_volume'].keys(), reverse=True)[:5]}")

# 模拟API逻辑
print(f"\n=== 模拟API逻辑 ===")
today_change = 0.0
today_volume = 0.0
found = False
for d in concept_dates:
    print(f"检查日期: {d}")
    has_change = d in data['daily_change']
    has_volume = d in data['daily_volume'] and data['daily_volume'][d] is not None
    print(f"  has_change={has_change}, has_volume={has_volume}")
    
    if has_change:
        today_change = data['daily_change'][d]
        print(f"  设置 today_change = {today_change}")
    if has_volume:
        today_volume = data['daily_volume'][d]
        print(f"  设置 today_volume = {today_volume}")
    
    if has_change or has_volume:
        found = True
        print(f"  找到，break")
        break

print(f"\n最终结果:")
print(f"  today_change={today_change}")
print(f"  today_volume={today_volume}")

db.close()

