
import sys
import os
import pandas as pd
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

date = '2026-04-13'

from datetime import datetime
dt = datetime.strptime(date, '%Y-%m-%d')
display_date = f"{dt.year}{dt.month:02d}{dt.day:02d}"

import pywencai

queries = [
    f"{display_date}同花顺板块",
    f"同花顺板块{display_date}涨幅排名"
]

for i, query in enumerate(queries, 1):
    print(f"\n{'='*60}")
    print(f"测试 {i}: {query}")
    print('='*60)
    
    df = pywencai.get(
        query=query,
        query_type='zhishu',
        loop=True,
        log=False
    )
    
    if df is not None:
        print(f"✅ 获取到 {len(df)} 条数据！")
        print("\n列名：")
        for col in df.columns:
            print(f"  - {col}")
    else:
        print("❌ 未获取到数据")
