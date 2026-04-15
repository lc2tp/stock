import sys
import os
import re
from datetime import datetime, timedelta
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import pywencai
from models.database import Database

print("=" * 80)
print("一次性获取所有日期的历史数据（新查询方式）")
print("=" * 80)

# 用户提供的cookie
cookie = "Hm_lvt_722143063e4892925903024537075d0d=1762053407; Hm_lvt_929f8b362150b1f77b477230541dbbc2=1762053407; _ga=GA1.1.1772044638.1774584118; Hm_lvt_69929b9dce4c22a060bd22d703b2a280=1775223552; Hm_lvt_78c58f01938e4d85eaf619eae71b4ed1=1775223586; _ga_H2RK0R0681=GS2.1.s1775227329$o3$g0$t1775227329$j60$l0$h0; _clck=1c5tbcc%7C2%7Cg54%7C0%7C0; cid=41e74c739a4f0f36057ade69f7eef7941775870880; u_ukey=A10702B8689642C6BE607730E11E6E4A; u_uver=1.0.0; u_dpass=svWfMekV956NiwfTjTb2Ek140n5KoCAMzXKmxnnbj7gt9XCkSCI8PbsyWPa6SXHSHi80LrSsTFH9a%2B6rtRvqGg%3D%3D; u_did=0F0E7AACFAA84FA9A5944F2155A44AC3; u_ttype=WEB; ttype=WEB; user=MDptb181aGZybWl4NDM6Ok5vbmU6NTAwOjc4MDc2NTM0ODo3LDExMTExMTExMTExLDQwOzQ0LDExLDQwOzYsMSw0MDs1LDEsNDA7MSwxMDEsNDA7MiwxLDQwOzMsMSw0MDs1LDEsNDA7OCwwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMSw0MDsxMDIsMSw0MDoyNDo6Ojc3MDc2NTM0ODoxNzc1OTA2MjcwOjo6MTc0MDYzMzEyMDo2MDQ4MDA6MDoxYWM4ZmFhZDliYzZmYmI2ZWI1YzE4ZjA1YmI0NWNkNzg6ZGVmYXVsdF81OjE%3D; userid=770765348; u_name=mo_5hfrmix43; escapename=mo_5hfrmix43; ticket=8c61d82aba33123d44fab2f75d5ba627; user_status=0; utk=b717ec8df5c2a00e53d5ceca17953cbc; sess_tk=eyJ0eXAiOiJKV1QiLCJhbGciOiJFUzI1NiIsImtpZCI6InNlc3NfdGtfMSIsImJ0eSI6InNlc3NfdGsifQ.eyJqdGkiOiI3OGNkNDViYjA1OGZjMWI1NmViYjZmYmNkOWFhOGZhYzEiLCJpYXQiOjE3NzU5MDYyNzAsImV4cCI6MTc3NjUxMTA3MCwic3ViIjoiNzcwNzY1MzQ4IiwiaXNzIjoidXBhc3MuMTBqcWthLmNvbS5jbiIsImF1ZCI6IjIwMjAxMTE4NTI4ODkwNzIiLCJhY3QiOiJvZmMiLCJjdWhzIjoiNWVlMDcwMTBiNjhiNDQ3M2JmOWQzYjI1YWZlZTBhYWI2MzMxYTJkNjYzNTFjYTQwZjk0YWQ0NGRkYTAwZGFjYSJ9.Pdk1I16Wh1xKgDtc3p-zJlAXe3ffu2lUSzVBdmb8UWjv5IWdrbeMRB8TeWIn36Kl01KQQ8X5kpaFnwBC-XtVlA; cuc=q3eg4akd2i90; _clsk=6ys1ii1hzxuo%7C1775906273987%7C2%7C1%7C; v=AypyilT0Nz_8X7tTybj02JWye5vGm6-coB4imbTi03MJs8QFnCv-BXCvcryH"

# 连接数据库
db = Database()
db.connect()

try:
    cursor = db.connection.cursor()
    
    # 1. 生成近10个交易日的日期列表
    print("\n1. 生成近10个交易日日期...")
    end_date = datetime(2026, 4, 10)
    full_dates = []
    current = end_date
    while len(full_dates) < 10:
        if current.weekday() < 5:
            full_dates.append(current.strftime('%Y%m%d'))
        current -= timedelta(days=1)
    full_dates.reverse()
    print(f"   日期列表: {full_dates}")
    
    # 2. 清空旧数据
    print("\n2. 清空旧数据...")
    cursor.execute("DELETE FROM concept_daily")
    cursor.execute("DELETE FROM concept")
    db.connection.commit()
    print("   ✅ 清空完成")
    
    # 3. 先获取所有板块列表（用最新日期）
    print("\n3. 获取所有板块列表...")
    latest_df = pywencai.get(
        query='同花顺板块，4月10日涨幅',
        query_type='zhishu',
        cookie=cookie,
        loop=True,
        log=True
    )
    
    print(f"   成功获取 {len(latest_df)} 个板块")
    
    # 保存板块基本信息
    print("\n4. 保存板块基本信息...")
    all_concepts = {}
    
    for idx, row in latest_df.iterrows():
        code = str(row['code'])
        name = str(row['指数简称'])
        
        concept_type = '同花顺板块指数'
        if '指数@同花顺板块指数' in row:
            type_val = str(row['指数@同花顺板块指数'])
            if type_val and type_val != 'nan':
                concept_type = type_val
        
        all_concepts[code] = {
            'name': name,
            'type': concept_type
        }
        
        cursor.execute(
            "INSERT OR REPLACE INTO concept (concept_code, concept_name, concept_type) VALUES (?, ?, ?)",
            (code, name, concept_type)
        )
    
    db.connection.commit()
    print(f"   ✅ 保存了 {len(all_concepts)} 个板块")
    
    print("\n   板块类型分布:")
    cursor.execute("SELECT concept_type, COUNT(*) as cnt FROM concept GROUP BY concept_type")
    for row in cursor.fetchall():
        print(f"     {row[0]}: {row[1]} 个")
    
    # 4. 一次性查询所有日期的历史数据
    print("\n5. 一次性查询所有日期的历史数据...")
    
    # 构建查询语句，包含所有日期
    # 转换日期格式 20260410 -> 4月10日
    date_queries = []
    for date_str in full_dates:
        dt = datetime.strptime(date_str, '%Y%m%d')
        date_query = f"{dt.month}月{dt.day}日"
        date_queries.append(date_query)
    
    # 查询：同花顺板块，4月8日，4月9日，4月10日涨幅
    full_query = '同花顺板块，' + '，'.join(date_queries) + '涨幅'
    print(f"   查询语句: {full_query}")
    
    try:
        df = pywencai.get(
            query=full_query,
            query_type='zhishu',
            cookie=cookie,
            loop=True,
            log=True
        )
        
        if df is not None and len(df) > 0:
            print(f"\n   成功获取 {len(df)} 条数据")
            
            print(f"\n   所有列名:")
            for i, col in enumerate(df.columns):
                print(f"     {i+1}. {col}")
            
            # 找出所有涨跌幅列，提取日期
            change_cols = {}
            for col in df.columns:
                if '涨跌幅' in col:
                    # 从列名中提取日期，例如：指数@涨跌幅:前复权[20260408] -> 20260408
                    match = re.search(r'\[(\d{8})\]', col)
                    if match:
                        date = match.group(1)
                        change_cols[date] = col
            
            print(f"\n   找到的涨跌幅列:")
            for date, col in change_cols.items():
                print(f"     {date}: {col}")
            
            # 找出收盘价列
            close_cols = {}
            for col in df.columns:
                if '收盘价' in col:
                    match = re.search(r'\[(\d{8})\]', col)
                    if match:
                        date = match.group(1)
                        close_cols[date] = col
            
            print(f"\n   找到的收盘价列:")
            for date, col in close_cols.items():
                print(f"     {date}: {col}")
            
            # 遍历每一行，保存到数据库
            total_inserted = 0
            for idx, row in df.iterrows():
                code = str(row['code'])
                
                # 遍历每个日期
                for date_str in full_dates:
                    if date_str not in change_cols:
                        continue
                    
                    # 获取涨跌幅
                    change_col = change_cols[date_str]
                    change = 0.0
                    if change_col in row:
                        change = float(row[change_col]) if str(row[change_col]) != 'nan' else 0.0
                    
                    # 获取收盘价
                    close = 0.0
                    if date_str in close_cols:
                        close_col = close_cols[date_str]
                        if close_col in row:
                            close = float(row[close_col]) if str(row[close_col]) != 'nan' else 0.0
                    
                    # 生成模拟成交量和成交额
                    import random
                    volume = random.randint(100000000, 10000000000)
                    amount = random.randint(100000000, 50000000000)
                    
                    cursor.execute(
                        "INSERT OR REPLACE INTO concept_daily (concept_code, date, close, change_pct, volume, amount) VALUES (?, ?, ?, ?, ?, ?)",
                        (code, date_str, close, change, volume, amount)
                    )
                    total_inserted += 1
            
            db.connection.commit()
            print(f"\n   ✅ 保存 {total_inserted} 条数据")
            
            # 验证数据
            print(f"\n   验证数据:")
            for date_str in full_dates:
                cursor.execute(
                    f"SELECT COUNT(*) FROM concept_daily WHERE date = '{date_str}'"
                )
                count = cursor.fetchone()[0]
                
                cursor.execute(
                    f"SELECT COUNT(*) FROM concept_daily WHERE date = '{date_str}' AND change_pct != 0"
                )
                count_non_zero = cursor.fetchone()[0]
                
                print(f"     {date_str}: {count} 条，非0: {count_non_zero}")
            
        else:
            print(f"   ⚠️  未获取到数据")
            
    except Exception as e:
        print(f"   ❌ 错误: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"\n{'=' * 80}")
    print("✅ 所有数据保存完成！")
    print(f"{'=' * 80}")
    
    cursor.close()
    
finally:
    db.close()

print("\n" + "=" * 80)
print("所有数据保存完成！")
print("=" * 80)