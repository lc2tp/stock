
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from models.database import Database

db = Database()
db.connect()

print("正在添加缺失的列...")
cursor = db.connection.cursor()

try:
    # 1. 添加 concept_type 到 concept 表
    try:
        cursor.execute("ALTER TABLE concept ADD COLUMN concept_type TEXT")
        print("✅ 已添加 concept_type 列到 concept 表")
    except Exception as e:
        print(f"ℹ️ concept_type 列已存在: {e}")
    
    # 2. 添加 volume 到 concept_daily 表
    try:
        cursor.execute("ALTER TABLE concept_daily ADD COLUMN volume REAL")
        print("✅ 已添加 volume 列到 concept_daily 表")
    except Exception as e:
        print(f"ℹ️ volume 列已存在: {e}")
    
    # 3. 添加 amount 到 concept_daily 表（如果需要）
    try:
        cursor.execute("ALTER TABLE concept_daily ADD COLUMN amount REAL")
        print("✅ 已添加 amount 列到 concept_daily 表")
    except Exception as e:
        print(f"ℹ️ amount 列已存在: {e}")
    
    db.connection.commit()
    print("\n✅ 所有列添加完成！")
    
except Exception as e:
    print(f"❌ 添加列失败: {e}")
    db.connection.rollback()

print("\n=== concept 表结构 ===")
cursor.execute("PRAGMA table_info(concept)")
columns = cursor.fetchall()
for c in columns:
    print(f"  {c[1]} ({c[2]})")

print("\n=== concept_daily 表结构 ===")
cursor.execute("PRAGMA table_info(concept_daily)")
columns = cursor.fetchall()
for c in columns:
    print(f"  {c[1]} ({c[2]})")

db.close()

