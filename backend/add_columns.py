import sqlite3

db_path = 'stock_system.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 添加amount和turnover字段
print("添加成交金额和换手率字段...")
try:
    # 添加amount字段（成交金额）
    cursor.execute("ALTER TABLE daily_change ADD COLUMN amount REAL DEFAULT 0")
    # 添加turnover字段（换手率）
    cursor.execute("ALTER TABLE daily_change ADD COLUMN turnover REAL DEFAULT 0")
    conn.commit()
    print("字段添加成功！")
except Exception as e:
    print(f"字段添加失败: {e}")

# 查看修改后的表结构
print("\n修改后的表结构：")
cursor.execute("PRAGMA table_info(daily_change)")
columns = cursor.fetchall()
for column in columns:
    print(f"{column[1]}: {column[2]}")

conn.close()