
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from services.jiuyang_service import fetch_and_save_jiuyang_data, get_recent_trading_days
from models.database import Database

print("正在获取最近 20 个交易日的数据...\n")

# 获取最近 20 个交易日
dates = get_recent_trading_days(20)
print(f"准备获取 {len(dates)} 个交易日的数据：")
print(f"  {dates}")
print()

for date_str in dates:
    print(f"正在处理 {date_str}...")
    success = fetch_and_save_jiuyang_data(date_str)
    if success:
        print(f"  ✅ {date_str} 数据保存成功！")
    else:
        print(f"  ⚠️ {date_str} 未获取到数据")
    print()

print("✅ 全部完成！")

