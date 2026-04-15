
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from models.database import Database

db = Database()
if db.connect():
    cursor = db.connection.cursor()
    cursor.execute("SELECT DISTINCT code, name FROM jiuyang_stock_action LIMIT 20")
    stocks = cursor.fetchall()
    print("数据库里的前20只股票：")
    for s in stocks:
        print(f"  {s[0]} - {s[1]}")
    cursor.close()
    db.close()
else:
    print("连接失败")

