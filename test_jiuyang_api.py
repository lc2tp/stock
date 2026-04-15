
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from services.jiuyang_service import fetch_jiuyang_data
from datetime import datetime, timedelta

# 获取最近一个交易日
today = datetime.now()
date_str = today.strftime('%Y-%m-%d')
print(f"正在获取 {date_str} 的数据...")

data = fetch_jiuyang_data(date_str)

if data:
    print(f"\n获取到 {len(data)} 个题材！")
    
    # 跳过"简图"，找有数据的题材
    found = False
    for theme in data:
        theme_name = theme.get('name', '')
        if theme_name == '简图':
            continue
        stock_list = theme.get('list', [])
        if len(stock_list) > 0:
            print(f"\n找到题材: {theme_name}")
            print(f"\n第一只股票的完整数据：")
            import json
            print(json.dumps(stock_list[0], indent=2, ensure_ascii=False))
            found = True
            break
    
    if not found:
        print("\n没有找到有数据的题材！")
else:
    print("未获取到数据")

