
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from models.database import Database

db = Database()
db.connect()

print("="*80)
print("完整模拟API /api/concept/data 逻辑")
print("="*80)

days = 10

# ------------------
# 步骤 1: 获取concept_dates
# ------------------
concept_dates = db.get_concept_dates()
print(f"\n[步骤 1] concept_dates: {concept_dates[:10]}")

if len(concept_dates) &lt; 2:
    print("数据不足")
    exit()

# ------------------
# 步骤 2: 选择日期
# ------------------
actual_days = min(days, len(concept_dates))
selected_dates = concept_dates[:actual_days]
print(f"\n[步骤 2] selected_dates: {selected_dates}")

sorted_dates = sorted(selected_dates)
print(f"sorted_dates: {sorted_dates}")

start_date = sorted_dates[0]
end_date = sorted_dates[-1]
print(f"查询范围: {start_date} ~ {end_date}")

# ------------------
# 步骤 3: 查询数据
# ------------------
all_data = db.get_concept_daily(start_date, end_date)
print(f"\n[步骤 3] get_concept_daily 返回 {len(all_data)} 条数据")

# ------------------
# 步骤 4: 整理数据
# ------------------
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

print(f"\n[步骤 4] 整理了 {len(concept_data)} 个板块")

# ------------------
# 步骤 5: 检查884284
# ------------------
print(f"\n[步骤 5] 检查 884284:")
code_to_check = '884284'
if code_to_check in concept_data:
    data = concept_data[code_to_check]
    print(f"  concept_name: {data['concept_name']}")
    print(f"  concept_type: {data['concept_type']}")
    print(f"  daily_change keys: {sorted(data['daily_change'].keys(), reverse=True)[:5]}")
    print(f"  daily_volume keys: {sorted(data['daily_volume'].keys(), reverse=True)[:5]}")
    
    # 检查20260415
    d = '20260415'
    if d in data['daily_change']:
        print(f"  20260415 in daily_change: {data['daily_change'][d]}")
    if d in data['daily_volume']:
        print(f"  20260415 in daily_volume: {data['daily_volume'][d]}")
else:
    print("  884284 不在 concept_data 中！")

# ------------------
# 步骤 6: 计算结果
# ------------------
print(f"\n[步骤 6] 计算结果...")
result = []
for code, data in concept_data.items():
    concept_type = data.get('concept_type', '')
    if not ('概念' in concept_type or '行业' in concept_type):
        continue
    
    cumulative_change = 1.0
    valid_days = 0
    
    for d in sorted_dates:
        if d in data['daily_change']:
            change_pct = data['daily_change'][d]
            cumulative_change *= (1 + change_pct / 100)
            valid_days += 1
    
    if valid_days &gt;= 1:
        cumulative_change_pct = (cumulative_change - 1) * 100
        
        today_change = 0.0
        today_volume = 0.0
        found = False
        for d in concept_dates:
            has_change = d in data['daily_change']
            has_volume = d in data['daily_volume'] and data['daily_volume'][d] is not None
            
            if has_change:
                today_change = data['daily_change'][d]
            if has_volume:
                today_volume = data['daily_volume'][d]
            
            if has_change or has_volume:
                found = True
                break
        
        if today_volume is None:
            today_volume = 0.0
        
        if code == '884284':
            print(f"\n  找到 884284:")
            print(f"    today_change = {today_change}")
            print(f"    today_volume = {today_volume}")
        
        result.append({
            'concept_code': code,
            'concept_name': data['concept_name'],
            'concept_type': data.get('concept_type', ''),
            'cumulative_change': cumulative_change_pct,
            'today_change': today_change,
            'today_volume': today_volume
        })

result.sort(key=lambda x: x['cumulative_change'], reverse=True)

print(f"\n[步骤 7] 生成了 {len(result)} 条结果")

print(f"\n前3条结果:")
for i, r in enumerate(result[:3]):
    print(f"{i+1}. {r['concept_name']}: change={r['today_change']}, volume={r['today_volume']}")

db.close()

