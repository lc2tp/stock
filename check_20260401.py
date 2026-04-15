
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from models.database import Database

db = Database()
db.db_path = os.path.join(os.path.dirname(__file__), 'backend', 'stock_system.db')

if db.connect():
    print("数据库连接成功！")
    
    cursor = db.connection.cursor()
    
    date = '2026-04-01'
    
    print(f"\n检查 {date} 的数据：")
    
    # 检查题材
    cursor.execute("SELECT * FROM jiuyang_theme WHERE date = ?", (date,))
    themes = cursor.fetchall()
    print(f"  题材数量: {len(themes)}")
    
    # 检查股票
    cursor.execute("SELECT * FROM jiuyang_stock_action WHERE date = ?", (date,))
    stocks = cursor.fetchall()
    print(f"  股票数量: {len(stocks)}")
    
    # 检查当前所有日期（有股票数据的）
    print(f"\n所有有股票数据的日期：")
    cursor.execute("""
        SELECT DISTINCT t.date 
        FROM jiuyang_theme t
        INNER JOIN jiuyang_stock_action s ON t.id = s.theme_id
        ORDER BY t.date DESC
    """)
    dates = cursor.fetchall()
    for d in dates:
        print(f"  {d[0]}")
    
    cursor.close()
    db.close()

