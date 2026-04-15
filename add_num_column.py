
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from models.database import Database

db = Database()
db.db_path = os.path.join(os.path.dirname(__file__), 'backend', 'stock_system.db')

if db.connect():
    print("数据库连接成功！")
    
    cursor = db.connection.cursor()
    
    try:
        # 添加 num 字段
        cursor.execute("ALTER TABLE jiuyang_stock_action ADD COLUMN num TEXT")
        print("成功添加 num 字段！")
        db.connection.commit()
    except Exception as e:
        print(f"添加字段失败（可能已存在）: {e}")
    
    # 查看新的表结构
    print("\njiuyang_stock_action 表结构（更新后）：")
    cursor.execute("PRAGMA table_info(jiuyang_stock_action)")
    columns = cursor.fetchall()
    for c in columns:
        print(f"  {c[1]} ({c[2]})")
    
    cursor.close()
    db.close()

