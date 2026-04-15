
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from models.database import Database

db = Database()
db.db_path = os.path.join(os.path.dirname(__file__), 'backend', 'stock_system.db')

if db.connect():
    print("数据库连接成功！")
    
    cursor = db.connection.cursor()
    
    # 搜索圣阳股份
    cursor.execute("SELECT code, name, num, date FROM jiuyang_stock_action WHERE name LIKE ? LIMIT 10", ('%圣阳%',))
    rows = cursor.fetchall()
    
    print("\n搜索结果：")
    for r in rows:
        print(f"  code: {r[0]}, name: {r[1]}, num: {r[2]}, date: {r[3]}")
    
    # 查看最近的数据，看看 num 字段有没有值
    print("\n最近10条数据：")
    cursor.execute("SELECT code, name, num FROM jiuyang_stock_action ORDER BY id DESC LIMIT 10")
    rows = cursor.fetchall()
    for r in rows:
        print(f"  code: {r[0]}, name: {r[1]}, num: {r[2]}")
    
    cursor.close()
    db.close()

