
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from models.database import Database

db = Database()
db.db_path = os.path.join(os.path.dirname(__file__), 'backend', 'stock_system.db')

if db.connect():
    print("数据库连接成功！")
    
    cursor = db.connection.cursor()
    
    print("\n检查最近几天的数据：")
    cursor.execute("SELECT DISTINCT date FROM jiuyang_theme ORDER BY date DESC LIMIT 5")
    dates = cursor.fetchall()
    
    for d in dates:
        date = d[0]
        # 查询股票数量
        cursor.execute("SELECT COUNT(*) FROM jiuyang_stock_action WHERE date = ?", (date,))
        stock_count = cursor.fetchone()[0]
        
        # 查询有 num 的股票数量
        cursor.execute("SELECT COUNT(*) FROM jiuyang_stock_action WHERE date = ? AND num IS NOT NULL AND num != ''", (date,))
        num_count = cursor.fetchone()[0]
        
        print(f"  {date}: {stock_count} 只股票 | {num_count} 只有 num")
        
        # 打印几只有 num 的股票
        if num_count > 0:
            cursor.execute("SELECT code, name, num FROM jiuyang_stock_action WHERE date = ? AND num IS NOT NULL AND num != '' LIMIT 5", (date,))
            for r in cursor.fetchall():
                print(f"    - {r[0]} {r[1]}: {r[2]}")
    
    cursor.close()
    db.close()

