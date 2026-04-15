
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from models.database import Database

db = Database()
db.connect()

print("=== 检查selected_dates和查询范围 ===")

concept_dates = db.get_concept_dates()
print(f"concept_dates: {concept_dates[:10]}")

actual_days = min(10, len(concept_dates))
selected_dates = concept_dates[:actual_days]
print(f"selected_dates: {selected_dates}")

sorted_dates = sorted(selected_dates)
print(f"sorted_dates: {sorted_dates}")

start_date = sorted_dates[0]
end_date = sorted_dates[-1]
print(f"查询范围: {start_date} ~ {end_date}")

print(f"\n查询 884284 在这个范围内的数据:")
cursor = db.connection.cursor()
cursor.execute("""
    SELECT cd.date, cd.change_pct, cd.volume 
    FROM concept_daily cd 
    WHERE cd.concept_code = '884284' AND cd.date BETWEEN ? AND ?
    ORDER BY cd.date DESC
""", (start_date, end_date))
rows = cursor.fetchall()
for row in rows:
    print(f"  {row[0]}: change={row[1]}, volume={row[2]}")

db.close()

