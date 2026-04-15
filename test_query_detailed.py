
import sys
import os
import pandas as pd
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

date = '2026-04-13'

from datetime import datetime
dt = datetime.strptime(date, '%Y-%m-%d')
display_date = f"{dt.year}{dt.month:02d}{dt.day:02d}"
print(f"查询日期: {date}")
print(f"格式化为: {display_date}")

import pywencai

query = f"{display_date}同花顺板块成交额"
print(f"\n查询参数: {query}")

print("\n正在请求...")
df = pywencai.get(
    query=query,
    query_type='zhishu',
    loop=True,
    log=False
)

if df is not None:
    print(f"\n✅ 获取到 {len(df)} 条数据！")
    print("\n=== 所有列名 ===")
    for col in df.columns:
        print(f"  - {col}")
    
    print("\n=== 前2条完整数据 ===")
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    print(df.head(2))
else:
    print("\n❌ 未获取到数据")

