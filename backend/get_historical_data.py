
import tushare as ts
import pandas as pd
from datetime import datetime, timedelta
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import TUSHARE_TOKEN
from models.database import Database

def get_trading_dates(end_date, count=10):
    ts.set_token(TUSHARE_TOKEN)
    pro = ts.pro_api()
    
    end_date_dt = datetime.strptime(end_date, '%Y%m%d')
    start_date_dt = end_date_dt - timedelta(days=30)
    start_date = start_date_dt.strftime('%Y%m%d')
    
    cal = pro.trade_cal(exchange='SSE', start_date=start_date, end_date=end_date)
    trading_dates = cal[cal['is_open'] == 1]['cal_date'].tolist()
    trading_dates.sort(reverse=True)
    
    return trading_dates[:count]

def get_historical_data():
    print("=== 获取历史数据 ===")
    
    ts.set_token(TUSHARE_TOKEN)
    pro = ts.pro_api()
    
    db = Database()
    db.connect()
    
    print("\n获取股票列表...")
    stock_list = pro.stock_basic(exchange='', list_status='L', fields='ts_code,symbol,name,industry,market')
    print(f"共 {len(stock_list)} 只股票")
    
    today = datetime.now().strftime('%Y%m%d')
    trading_dates = get_trading_dates(today, 10)
    print(f"\n过去10个交易日: {trading_dates}")
    
    stock_info_dict = {}
    for _, stock in stock_list.iterrows():
        stock_info_dict[stock['ts_code']] = {
            'symbol': stock['symbol'],
            'name': stock['name'],
            'industry': stock['industry']
        }
    
    total_inserted = 0
    for trade_date in trading_dates:
        print(f"\n获取 {trade_date} 的数据...")
        
        try:
            df = pro.daily(trade_date=trade_date)
            
            if df is not None and len(df) > 0:
                print(f"  找到 {len(df)} 条记录")
                
                for _, row in df.iterrows():
                    ts_code = row['ts_code']
                    
                    if ts_code in stock_info_dict:
                        stock_info = stock_info_dict[ts_code]
                        
                        pre_close = row['pre_close']
                        if pre_close > 0:
                            change_pct = ((row['close'] - pre_close) / pre_close) * 100
                        else:
                            change_pct = 0
                        
                        db.insert_daily_change(
                            ts_code=ts_code,
                            symbol=stock_info['symbol'],
                            name=stock_info['name'],
                            industry=stock_info['industry'],
                            close=row['close'],
                            change=change_pct,
                            date=trade_date
                        )
                        
                        total_inserted += 1
                
                print(f"  已插入 {total_inserted} 条记录")
        
        except Exception as e:
            print(f"  获取 {trade_date} 数据失败: {e}")
            continue
    
    print(f"\n=== 完成 ===")
    print(f"总共插入 {total_inserted} 条记录")
    
    db.close()

def get_daily_data(date):
    """
    获取指定日期的股票数据
    :param date: 日期，格式为'YYYYMMDD'
    """
    print(f"=== 获取 {date} 的数据 ===")
    
    ts.set_token(TUSHARE_TOKEN)
    pro = ts.pro_api()
    
    db = Database()
    db.connect()
    
    print("\n获取股票列表...")
    # 不包含float_share字段，避免API调用失败
    stock_list = pro.stock_basic(exchange='', list_status='L', fields='ts_code,symbol,name,industry,market')
    print(f"共 {len(stock_list)} 只股票")
    
    stock_info_dict = {}
    for _, stock in stock_list.iterrows():
        stock_info_dict[stock['ts_code']] = {
            'symbol': stock['symbol'],
            'name': stock['name'],
            'industry': stock['industry'],
            'float_share': 0  # 默认值为0
        }
    
    total_inserted = 0
    print(f"\n获取 {date} 的数据...")
    
    try:
        # 获取带成交额的日线数据
        df = pro.daily(trade_date=date, fields='ts_code,pre_close,close,amount,vol')
        
        if df is not None and len(df) > 0:
            print(f"  找到 {len(df)} 条记录")
            
            for _, row in df.iterrows():
                ts_code = row['ts_code']
                
                if ts_code in stock_info_dict:
                    stock_info = stock_info_dict[ts_code]
                    
                    pre_close = row['pre_close']
                    if pre_close > 0:
                        change_pct = ((row['close'] - pre_close) / pre_close) * 100
                    else:
                        change_pct = 0
                    
                    # 计算换手率 = 成交量(手) / 流通股本(万股) * 100%
                    amount = row['amount']  # 成交额（千元）
                    vol = row['vol']  # 成交量（手）
                    float_share = stock_info['float_share']  # 流通股本（万股）
                    
                    if float_share > 0:
                        turnover = (vol / float_share) * 100
                    else:
                        turnover = 0
                    
                    db.insert_daily_change(
                        ts_code=ts_code,
                        symbol=stock_info['symbol'],
                        name=stock_info['name'],
                        industry=stock_info['industry'],
                        close=row['close'],
                        change=change_pct,
                        amount=amount,
                        turnover=turnover,
                        date=date
                    )
                    
                    total_inserted += 1
            
            print(f"  已插入 {total_inserted} 条记录")
    
    except Exception as e:
        print(f"  获取 {date} 数据失败: {e}")
    
    print(f"\n=== 完成 ===")
    print(f"总共插入 {total_inserted} 条记录")
    
    db.close()

if __name__ == "__main__":
    get_historical_data()
