
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
    print(f"\n查看 {date} 的数据：")
    
    cursor.execute("SELECT code, name, num, action_time FROM jiuyang_stock_action WHERE date = ? ORDER BY id", (date,))
    rows = cursor.fetchall()
    
    print(f"\n共 {len(rows)} 条股票数据：")
    
    count_with_num = 0
    for r in rows:
        num = r[2]
        if num:
            count_with_num += 1
            print(f"  ✅ {r[0]} - {r[1]} | num: {num}")
    
    print(f"\n共有 {count_with_num} 条数据有 num 字段！")
    
    cursor.close()
    db.close()

