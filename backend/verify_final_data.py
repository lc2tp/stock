import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.database import Database

print("=" * 80)
print("验证数据完整性和累计涨幅")
print("=" * 80)

db = Database()
db.connect()

try:
    cursor = db.connection.cursor()
    
    # 1. 查看板块总数
    cursor.execute("SELECT COUNT(*) FROM concept")
    concept_count = cursor.fetchone()[0]
    
    # 2. 查看数据总数
    cursor.execute("SELECT COUNT(*) FROM concept_daily")
    data_count = cursor.fetchone()[0]
    
    print(f"\n1. 基本信息:")
    print(f"   板块数量: {concept_count}")
    print(f"   数据条数: {data_count}")
    
    # 3. 查看每个日期的数据
    print(f"\n2. 每个日期的数据:")
    cursor.execute("SELECT date, COUNT(*) as cnt FROM concept_daily GROUP BY date ORDER BY date")
    for row in cursor.fetchall():
        cursor.execute(
            f"SELECT COUNT(*) FROM concept_daily WHERE date = '{row[0]}' AND change_pct != 0"
        )
        count_non_zero = cursor.fetchone()[0]
        print(f"   {row[0]}: {row[1]} 条，非0: {count_non_zero}")
    
    # 4. 拿稀土永磁测试不同周期的累计涨幅
    print(f"\n3. 测试稀土永磁(885343)的累计涨幅:")
    code = '885343'
    cursor.execute(
        "SELECT date, change_pct FROM concept_daily WHERE concept_code = ? ORDER BY date",
        (code,)
    )
    data = cursor.fetchall()
    
    print(f"\n   日期-涨跌幅:")
    for row in data:
        print(f"     {row[0]}: {row[1]}%")
    
    # 测试不同周期
    print(f"\n   计算不同周期的累计涨幅:")
    for days in [2, 3, 4, 5, 10]:
        if len(data) >= days:
            selected = data[-days:]
            cumulative_change = 1.0
            for row in selected:
                cumulative_change *= (1 + row[1] / 100)
            cumulative_pct = (cumulative_change - 1) * 100
            print(f"     {days}日: {cumulative_pct:.2f}%")
    
    cursor.close()
    
finally:
    db.close()

print("\n" + "=" * 80)
print("验证完成")
print("=" * 80)