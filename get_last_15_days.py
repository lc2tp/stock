
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from get_concept_data import (
    get_concept_data_from_url, 
    parse_concept_data, 
    save_concept_data_to_db,
    is_trade_day
)
from datetime import datetime, timedelta

def get_last_n_trade_days(n=15):
    """
    获取最近n个交易日（从今天往前数）
    """
    trade_days = []
    current_date = datetime.now()
    
    while len(trade_days) < n:
        if is_trade_day(current_date):
            trade_days.append(current_date.strftime('%Y-%m-%d'))
        current_date -= timedelta(days=1)
    
    return trade_days

if __name__ == '__main__':
    print("="*60)
    print("获取最近15个交易日的板块数据")
    print("="*60)
    
    # 获取最近15个交易日
    trade_days = get_last_n_trade_days(15)
    print(f"\n需要获取的交易日:")
    for i, day in enumerate(trade_days, 1):
        print(f"  {i}. {day}")
    
    print(f"\n共 {len(trade_days)} 个交易日\n")
    
    # 逐个获取数据
    success_count = 0
    fail_count = 0
    
    for i, date in enumerate(trade_days, 1):
        print(f"\n[{i}/{len(trade_days)}] 正在处理 {date} ...")
        print("-"*60)
        
        try:
            # 获取数据
            df = get_concept_data_from_url(date)
            
            if df is not None:
                # 解析数据
                data = parse_concept_data(df, date)
                
                if data:
                    # 保存到数据库
                    save_concept_data_to_db(data)
                    success_count += 1
                    print(f"✅ {date} 成功: {len(data)} 条数据")
                else:
                    fail_count += 1
                    print(f"❌ {date} 解析失败: 无数据")
            else:
                fail_count += 1
                print(f"❌ {date} 获取失败")
                
        except Exception as e:
            fail_count += 1
            print(f"❌ {date} 异常: {e}")
        
        # 间隔一下，避免请求过快
        if i < len(trade_days):
            import time
            time.sleep(2)
    
    print("\n" + "="*60)
    print(f"完成！成功: {success_count}, 失败: {fail_count}")
    print("="*60)

