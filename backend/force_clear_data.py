import sqlite3

# 直接连接SQLite数据库
conn = sqlite3.connect('stock_system.db')
cursor = conn.cursor()

try:
    # 按照外键约束顺序删除数据
    cursor.execute("DELETE FROM limit_up")
    cursor.execute("DELETE FROM stock")
    cursor.execute("DELETE FROM theme")
    conn.commit()
    print("SQLite数据清空成功")
    
    # 验证清空结果
    cursor.execute("SELECT COUNT(*) FROM theme")
    theme_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM stock")
    stock_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM limit_up")
    limit_up_count = cursor.fetchone()[0]
    
    print(f"验证结果: 题材={theme_count}, 股票={stock_count}, 涨停记录={limit_up_count}")
    
except Exception as e:
    print(f"清空数据失败: {e}")
    conn.rollback()
finally:
    cursor.close()
    conn.close()