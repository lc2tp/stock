
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

date = '2026-04-13'

from datetime import datetime
dt = datetime.strptime(date, '%Y-%m-%d')
display_date = f"{dt.year}{dt.month:02d}{dt.day:02d}"
print(f"日期格式: {display_date}")

import pywencai

query = f"{display_date}同花顺板块成交额"
print(f"查询参数: {query}")

print("\n正在请求...")
df = pywencai.get(
    query=query,
    query_type='zhishu',
    loop=True,
    log=False
)

if df is not None:
    print(f"\n✅ 获取到 {len(df)} 条数据！")
    print("\n列名：")
    for col in df.columns[:10]:  # 只显示前10列
        print(f"  - {col}")
    if len(df.columns) > 10:
        print(f"  ... 还有 {len(df.columns) - 10} 列")
    
    print("\n前3条数据预览：")
    print(df[['code', '指数简称']].head(3))
else:
    print("\n❌ 未获取到数据")

