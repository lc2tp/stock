
import sqlite3
import os

# 获取当前脚本所在目录的绝对路径
script_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(script_dir, 'stock_system.db')

print(f"数据库路径: {db_path}")

# 连接数据库
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 删除2025年之前的旧数据
print("删除2025年之前的旧数据...")
cursor.execute('''
    DELETE FROM daily_change
    WHERE date < '20250101'
''')

deleted_count = cursor.rowcount
print(f"删除了 {deleted_count} 条旧数据")

# 提交更改
conn.commit()

# 查询剩余的数据
print("\n查询剩余的数据...")
cursor.execute('''
    SELECT COUNT(*) FROM daily_change
''')
remaining_count = cursor.fetchone()[0]
print(f"剩余 {remaining_count} 条数据")

# 查看数据的日期范围
cursor.execute('''
    SELECT MIN(date), MAX(date) FROM daily_change
''')
date_range = cursor.fetchone()
print(f"日期范围: {date_range[0]} 到 {date_range[1]}")

# 关闭连接
conn.close()

print("\n清理完成！")
