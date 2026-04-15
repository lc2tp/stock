
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from models.database import Database

db = Database()
db.connect()

print("=== 检查数据库里是否有volume数据 ===")
cursor = db.connection.cursor()

# 获取一个日期的数据
cursor.execute("SELECT * FROM concept_daily LIMIT 5")
rows = cursor.fetchall()
print(f"concept_daily 表前5行数据:")
for row in rows:
    print(f"  {row}")

print("\n=== 获取最近10天的概念数据 ===")
concept_dates = db.get_concept_dates()
print(f"有数据的日期: {concept_dates[:10]}")

if len(concept_dates) &gt;= 2:
    selected_dates = concept_dates[:2]
    selected_dates.sort()
    start_date = selected_dates[0]
    end_date = selected_dates[-1]
    
    print(f"\n查询范围: {start_date} - {end_date}")
    
    all_data = db.get_concept_daily(start_date, end_date)
    print(f"\nget_concept_daily 返回了 {len(all_data)} 条数据")
    
    if len(all_data) &gt; 0:
        print(f"\n第一条数据: {all_data[0]}")
        
        print(f"\n检查volume字段:")
        for i, item in enumerate(all_data[:5]):
            print(f"  {i+1}. {item['concept_name']}: volume={item.get('volume', 'N/A')}")

db.close()

