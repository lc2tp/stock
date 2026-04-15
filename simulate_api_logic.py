
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from models.database import Database

db = Database()
db.connect()

print("=== 模拟API逻辑 ===")

concept_dates = db.get_concept_dates()
print(f"有数据的日期: {concept_dates[:10]}")

actual_days = min(10, len(concept_dates))
selected_dates = concept_dates[:actual_days]
sorted_dates = sorted(selected_dates)

start_date = sorted_dates[0]
end_date = sorted_dates[-1]

all_data = db.get_concept_daily(start_date, end_date)
print(f"\nget_concept_daily返回 {len(all_data)} 条数据")

concept_data = {}
for item in all_data:
    code = item['concept_code']
    if code not in concept_data:
        concept_data[code] = {
            'concept_code': code,
            'concept_name': item['concept_name'],
            'concept_type': item.get('concept_type', ''),
            'daily_change': {},
            'daily_volume': {}
        }
    concept_data[code]['daily_change'][item['date']] = item['change_pct']
    concept_data[code]['daily_volume'][item['date']] = item.get('volume', 0.0)

print(f"\n整理了 {len(concept_data)} 个板块")

# 找钴板块
for code, data in concept_data.items():
    if '钴' in data['concept_name']:
        print(f"\n--- 找到钴板块: {code} ---")
        print(f"  concept_name: {data['concept_name']}")
        print(f"  daily_change keys: {list(data['daily_change'].keys())[:5]}")
        print(f"  daily_volume keys: {list(data['daily_volume'].keys())[:5]}")
        
        # 查看20260415的数据
        if '20260415' in data['daily_change']:
            print(f"  20260415 change: {data['daily_change']['20260415']}")
        if '20260415' in data['daily_volume']:
            print(f"  20260415 volume: {data['daily_volume']['20260415']}")
        
        # 模拟API逻辑
        today_change = 0.0
        today_volume = 0.0
        found = False
        for d in concept_dates:
            has_change = d in data['daily_change']
            has_volume = d in data['daily_volume'] and data['daily_volume'][d] is not None
            
            print(f"    检查日期 {d}: has_change={has_change}, has_volume={has_volume}")
            
            if has_change:
                today_change = data['daily_change'][d]
                print(f"      设置 today_change = {today_change}")
            if has_volume:
                today_volume = data['daily_volume'][d]
                print(f"      设置 today_volume = {today_volume}")
            
            if has_change or has_volume:
                found = True
                print(f"      找到数据，break!")
                break
        
        print(f"  最终结果: today_change={today_change}, today_volume={today_volume}")

db.close()

