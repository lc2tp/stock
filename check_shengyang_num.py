
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from models.database import Database

db = Database()
db.db_path = os.path.join(os.path.dirname(__file__), 'backend', 'stock_system.db')

if db.connect():
    print("数据库连接成功！")
    
    cursor = db.connection.cursor()
    
    print("\n查看数据库里有哪些日期：")
    cursor.execute("SELECT DISTINCT date FROM jiuyang_theme ORDER BY date DESC")
    dates = cursor.fetchall()
    for d in dates:
        print(f"  {d[0]}")
    
    print("\n查找圣阳股份：")
    cursor.execute("SELECT code, name, num, date, action_time FROM jiuyang_stock_action WHERE name LIKE ? ORDER BY date DESC", ('%圣阳%',))
    rows = cursor.fetchall()
    for r in rows:
        print(f"  date: {r[3]}, code: {r[0]}, name: {r[1]}, num: {r[2]}, action_time: {r[4]}")
    
    cursor.close()
    db.close()

