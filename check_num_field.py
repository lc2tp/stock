
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from models.database import Database

db = Database()
db.db_path = os.path.join(os.path.dirname(__file__), 'backend', 'stock_system.db')

if db.connect():
    print("数据库连接成功！")
    
    cursor = db.connection.cursor()
    
    # 查看表结构
    print("\njiuyang_stock_action 表结构：")
    cursor.execute("PRAGMA table_info(jiuyang_stock_action)")
    columns = cursor.fetchall()
    for c in columns:
        print(f"  {c[1]} ({c[2]})")
    
    # 查看最近数据，看看有没有 num 字段
    print("\n前10条数据：")
    cursor.execute("SELECT code, name FROM jiuyang_stock_action LIMIT 10")
    rows = cursor.fetchall()
    for r in rows:
        print(f"  {r[0]} - {r[1]}")
    
    cursor.close()
    db.close()

