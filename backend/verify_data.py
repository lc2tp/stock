import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.database import Database

print("=" * 80)
print("验证数据库数据")
print("=" * 80)

db = Database()
db.connect()

try:
    cursor = db.connection.cursor()
    
    # 查询板块数量
    cursor.execute("SELECT COUNT(*) FROM concept")
    concept_count = cursor.fetchone()[0]
    print(f"\n板块数量: {concept_count}")
    
    # 查询数据条数
    cursor.execute("SELECT COUNT(*) FROM concept_daily")
    data_count = cursor.fetchone()[0]
    print(f"数据条数: {data_count}")
    
    # 查询板块类型分布
    cursor.execute("SELECT concept_type, COUNT(*) as cnt FROM concept GROUP BY concept_type")
    type_dist = cursor.fetchall()
    print(f"\n板块类型分布:")
    for row in type_dist:
        print(f"  {row[0]}: {row[1]} 个")
    
    # 查询前20个板块
    print(f"\n前20个板块:")
    cursor.execute("SELECT concept_code, concept_name, concept_type FROM concept LIMIT 20")
    for row in cursor.fetchall():
        print(f"  {row[0]} - {row[1]} ({row[2]})")
    
    # 查询20260408的数据条数
    cursor.execute("SELECT COUNT(*) FROM concept_daily WHERE date = '20260408'")
    count_20260408 = cursor.fetchone()[0]
    print(f"\n2026-04-08 数据条数: {count_20260408}")
    
    # 查询20260410的数据条数
    cursor.execute("SELECT COUNT(*) FROM concept_daily WHERE date = '20260410'")
    count_20260410 = cursor.fetchone()[0]
    print(f"2026-04-10 数据条数: {count_20260410}")
    
    # 查询每个日期的数据条数
    print(f"\n每个日期的数据条数:")
    cursor.execute("SELECT date, COUNT(*) as cnt FROM concept_daily GROUP BY date ORDER BY date")
    for row in cursor.fetchall():
        print(f"  {row[0]}: {row[1]} 条")
    
    cursor.close()
    
finally:
    db.close()

print("\n" + "=" * 80)
print("验证完成")
print("=" * 80)