
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from models.database import Database

# 测试数据库连接
db = Database()
db.db_path = os.path.join(os.path.dirname(__file__), 'backend', 'stock_system.db')

if db.connect():
    print("数据库连接成功！")
    
    cursor = db.connection.cursor()
    
    # 查看所有表
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print("\n所有表：")
    for t in tables:
        print(f"  - {t[0]}")
    
    # 查看jiuyang_stock_action表的结构
    print("\njiuyang_stock_action 表结构：")
    cursor.execute("PRAGMA table_info(jiuyang_stock_action)")
    columns = cursor.fetchall()
    for c in columns:
        print(f"  {c[1]} ({c[2]})")
    
    # 查看前10条数据
    print("\n前10条数据：")
    cursor.execute("SELECT code, name, action_time FROM jiuyang_stock_action LIMIT 10")
    rows = cursor.fetchall()
    for r in rows:
        print(f"  code={r[0]}, name={r[1]}, action_time={r[2]}")
    
    cursor.close()
    db.close()
else:
    print("数据库连接失败！")

