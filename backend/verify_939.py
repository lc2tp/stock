import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.database import Database

print("=" * 80)
print("验证完整数据（939个板块）")
print("=" * 80)

db = Database()
db.connect()

try:
    cursor = db.connection.cursor()
    
    # 1. 验证板块总数
    print("\n1. 板块总数:")
    cursor.execute("SELECT COUNT(*) FROM concept")
    count = cursor.fetchone()[0]
    print(f"   ✅ {count} 个板块")
    
    # 2. 验证板块类型分布
    print("\n2. 板块类型分布:")
    cursor.execute("SELECT concept_type, COUNT(*) as cnt FROM concept GROUP BY concept_type")
    for row in cursor.fetchall():
        print(f"   {row[0]}: {row[1]} 个")
    
    # 3. 查找稀土相关板块
    print("\n3. 稀土相关板块:")
    cursor.execute("SELECT concept_code, concept_name, concept_type FROM concept WHERE concept_name LIKE '%稀土%'")
    results = cursor.fetchall()
    if results:
        for row in results:
            print(f"   ✅ {row[0]}: {row[1]} ({row[2]})")
    else:
        print("   ❌ 未找到")
    
    # 4. 前50个行业指数
    print("\n4. 前50个行业指数:")
    cursor.execute("SELECT concept_code, concept_name FROM concept WHERE concept_type LIKE '%行业%' ORDER BY concept_name LIMIT 50")
    for idx, row in enumerate(cursor.fetchall()):
        print(f"   {idx+1:2d}. {row[0]}: {row[1]}")
    
    # 5. 验证2026-04-08的数据完整性
    print("\n5. 2026-04-08 数据条数:")
    cursor.execute("SELECT COUNT(*) FROM concept_daily WHERE date = '20260408'")
    count_20260408 = cursor.fetchone()[0]
    print(f"   ✅ {count_20260408} 条数据")
    
    # 6. 验证每个日期的数据条数
    print("\n6. 每个日期的数据条数:")
    cursor.execute("SELECT date, COUNT(*) as cnt FROM concept_daily GROUP BY date ORDER BY date")
    for row in cursor.fetchall():
        print(f"   {row[0]}: {row[1]} 条")
    
    cursor.close()
    
finally:
    db.close()

print("\n" + "=" * 80)
print("验证完成")
print("=" * 80)