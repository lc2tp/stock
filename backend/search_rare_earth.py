import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.database import Database

print("=" * 80)
print("搜索所有可能的稀土相关板块")
print("=" * 80)

db = Database()
db.connect()

try:
    cursor = db.connection.cursor()
    
    # 搜索各种可能的关键词
    keywords = ['稀土', '稀', '土', '磁', '永磁']
    
    print("\n搜索各种关键词:")
    for keyword in keywords:
        cursor.execute(
            "SELECT concept_code, concept_name, concept_type FROM concept WHERE concept_name LIKE ?",
            (f'%{keyword}%',)
        )
        results = cursor.fetchall()
        if results:
            print(f"\n  '{keyword}':")
            for row in results:
                print(f"    - {row[0]}: {row[1]} ({row[2]})")
    
    # 列出所有类型
    print("\n" + "=" * 80)
    print("所有板块类型统计:")
    cursor.execute("SELECT concept_type, COUNT(*) as cnt FROM concept GROUP BY concept_type")
    for row in cursor.fetchall():
        print(f"  {row[0]}: {row[1]} 个")
    
    cursor.close()
    
finally:
    db.close()

print("\n" + "=" * 80)
print("搜索完成")
print("=" * 80)