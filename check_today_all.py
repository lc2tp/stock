
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from models.database import Database

db = Database()
db.db_path = os.path.join(os.path.dirname(__file__), 'backend', 'stock_system.db')

if db.connect():
    print("数据库连接成功！")
    
    cursor = db.connection.cursor()
    
    date = '2026-04-14'
    print(f"\n查看 {date} 的题材数据：")
    
    cursor.execute("SELECT * FROM jiuyang_theme WHERE date = ?", (date,))
    themes = cursor.fetchall()
    print(f"  共 {len(themes)} 个题材！")
    
    if len(themes) > 0:
        print(f"\n查看 {date} 的股票数据：")
        cursor.execute("SELECT * FROM jiuyang_stock_action WHERE date = ?", (date,))
        stocks = cursor.fetchall()
        print(f"  共 {len(stocks)} 条股票记录！")
    
    cursor.close()
    db.close()

