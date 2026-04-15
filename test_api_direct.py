
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from models.database import Database

db = Database()
db.connect()

print("=== 模拟API接口逻辑 ===")
concept_dates = db.get_concept_dates()
print(f"有数据的日期: {concept_dates[:10]}")

actual_days = min(10, len(concept_dates))
selected_dates = concept_dates[:actual_days]
selected_dates.sort()

start_date = selected_dates[0]
end_date = selected_dates[-1]

all_data = db.get_concept_daily(start_date, end_date)
print(f"\nget_concept_daily 返回了 {len(all_data)} 条数据")

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

result = []
for code, data in concept_data.items():
    concept_type = data.get('concept_type', '')
    if not ('概念' in concept_type or '行业' in concept_type):
        continue
    
    cumulative_change = 1.0
    valid_days = 0
    
    for d in selected_dates:
        if d in data['daily_change']:
            change_pct = data['daily_change'][d]
            cumulative_change *= (1 + change_pct / 100)
            valid_days += 1
    
    if valid_days &gt;= 1:
        cumulative_change_pct = (cumulative_change - 1) * 100
        
        today_change = 0.0
        today_volume = 0.0
        if selected_dates:
            latest_date = selected_dates[-1]
            if latest_date in data['daily_change']:
                today_change = data['daily_change'][latest_date]
            if latest_date in data['daily_volume']:
                today_volume = data['daily_volume'][latest_date]
        
        result.append({
            'concept_code': code,
            'concept_name': data['concept_name'],
            'concept_type': data.get('concept_type', ''),
            'cumulative_change': cumulative_change_pct,
            'today_change': today_change,
            'today_volume': today_volume
        })

print(f"\n生成了 {len(result)} 条结果")

print("\n=== 前5条结果 ===")
for i, r in enumerate(result[:5]):
    print(f"{i+1}. {r['concept_name']}: today_volume={r['today_volume']}")

db.close()

