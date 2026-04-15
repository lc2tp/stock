import sqlite3

# 连接数据库
conn = sqlite3.connect('stock_system.db')
cursor = conn.cursor()

# 清空daily_top30表
cursor.execute('DELETE FROM daily_top30')
conn.commit()

# 查看清空后的结果
cursor.execute('SELECT COUNT(*) FROM daily_top30')
count = cursor.fetchone()[0]
print(f"daily_top30表已清空，当前记录数: {count}")

# 关闭连接
conn.close()
