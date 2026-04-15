
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from models.database import Database

db = Database()
db.db_path = os.path.join(os.path.dirname(__file__), 'backend', 'stock_system.db')

if db.connect():
    print("数据库连接成功！")
    
    cursor = db.connection.cursor()
    
    print("\n查询所有有股票数据的日期（带数量）：")
    cursor.execute("""
        SELECT t.date, COUNT(s.id) as stock_count
        FROM jiuyang_theme t
        INNER JOIN jiuyang_stock_action s ON t.id = s.theme_id
        GROUP BY t.date
        ORDER BY t.date DESC
    """)
    dates = cursor.fetchall()
    
    print(f"  共 {len(dates)} 个日期有数据：")
    for d in dates:
        print(f"    {d[0]}: {d[1]} 只股票")
    
    cursor.close()
    db.close()

