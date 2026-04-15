import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.database import Database

print("=" * 80)
print("详细诊断板块数据")
print("=" * 80)

db = Database()
db.connect()
db.create_tables()

try:
    # 1. 检查concept_daily表的所有数据
    print("\n1. 检查 concept_daily 表的前10条数据:")
    cursor = db.connection.cursor()
    cursor.execute("SELECT * FROM concept_daily LIMIT 10")
    rows = cursor.fetchall()
    for i, row in enumerate(rows):
        print(f"   {i+1}. {dict(row)}")
    
    # 2. 获取concept_dates
    print("\n2. get_concept_dates():")
    dates = db.get_concept_dates()
    print(f"   返回: {dates}")
    if dates:
        print(f"   类型: {type(dates[0])}")
    
    # 3. 测试get_concept_daily
    if len(dates) >= 2:
        start = dates[0]
        end = dates[-1]
        print(f"\n3. get_concept_daily('{start}', '{end}'):")
        data = db.get_concept_daily(start, end)
        print(f"   返回数据条数: {len(data)}")
        if len(data) > 0:
            print(f"   前3条:")
            for i, item in enumerate(data[:3]):
                print(f"     {i+1}. {item}")
    
    # 4. 按板块分组
    if len(dates) >= 2 and len(data) > 0:
        print(f"\n4. 按板块分组:")
        concept_data = {}
        for item in data:
            code = item['concept_code']
            if code not in concept_data:
                concept_data[code] = {
                    'concept_code': code,
                    'concept_name': item['concept_name'],
                    'daily_data': {}
                }
            concept_data[code]['daily_data'][item['date']] = item['change_pct']
        
        print(f"   板块数量: {len(concept_data)}")
        for code, info in concept_data.items():
            print(f"     {code} ({info['concept_name']}): {len(info['daily_data'])}天数据")
            
            # 计算累计涨幅
            cumulative_change = 1.0
            valid_days = 0
            selected_dates = dates[:min(8, len(dates))]
            for d in selected_dates:
                if d in info['daily_data']:
                    change_pct = info['daily_data'][d]
                    cumulative_change *= (1 + change_pct / 100)
                    valid_days += 1
            print(f"       valid_days={valid_days}, cumulative_change={(cumulative_change-1)*100:.2f}%")
    
    cursor.close()
    
finally:
    db.close()

print("\n" + "=" * 80)
print("诊断完成")
print("=" * 80)