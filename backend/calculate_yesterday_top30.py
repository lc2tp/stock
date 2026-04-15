
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.database import Database

def calculate_top30_for_date(target_date):
    print(f"=== 计算 {target_date} 的10日累计涨幅前30 ===")
    
    db = Database()
    db.connect()
    cursor = db.connection.cursor()
    
    cursor.execute("SELECT DISTINCT date FROM daily_change WHERE date <= ? ORDER BY date ASC", (target_date,))
    dates = cursor.fetchall()
    print(f"可用交易日（到{target_date}）: {[d[0] for d in dates]}")
    
    cursor.execute("SELECT DISTINCT ts_code, symbol, name, industry FROM daily_change WHERE date <= ?", (target_date,))
    stocks_in_db = cursor.fetchall()
    print(f"有数据的股票数: {len(stocks_in_db)}")
    
    result = []
    
    for stock_row in stocks_in_db:
        ts_code = stock_row[0]
        symbol = stock_row[1]
        name = stock_row[2]
        industry = stock_row[3]
        
        cursor.execute('''
            SELECT date, close, change
            FROM daily_change
            WHERE ts_code = ? AND date <= ?
            ORDER BY date ASC
        ''', (ts_code, target_date))
        
        stock_data = cursor.fetchall()
        
        if len(stock_data) >= 1:
            if len(stock_data) >= 10:
                recent_10_days = stock_data[-10:]
                first_price = recent_10_days[0][1]
                last_price = recent_10_days[-1][1]
                
                if first_price > 0:
                    ten_day_change = ((last_price - first_price) / first_price) * 100
                else:
                    ten_day_change = 0
            elif len(stock_data) >= 2:
                first_price = stock_data[0][1]
                last_price = stock_data[-1][1]
                
                if first_price > 0:
                    ten_day_change = ((last_price - first_price) / first_price) * 100
                else:
                    ten_day_change = 0
            else:
                ten_day_change = stock_data[0][2]
            
            daily_change = stock_data[-1][2] if len(stock_data) > 0 else 0
            
            result.append({
                'ts_code': ts_code,
                'symbol': symbol,
                'name': name,
                'industry': industry,
                'ten_day_change': round(ten_day_change, 2),
                'daily_change': round(daily_change, 2)
            })
    
    db.close()
    
    result.sort(key=lambda x: x['ten_day_change'], reverse=True)
    top30 = result[:30]
    
    print(f"\n获取到 {len(top30)} 只股票")
    
    print("\n排名\t代码\t名称\t\t概念\t\t10日涨幅(%)\t单日涨幅(%)")
    print("-" * 80)
    
    for i, stock in enumerate(top30):
        print(f"{i+1}\t{stock['symbol']}\t{stock['name']}\t{stock['industry'] or '-'}\t{stock['ten_day_change']}\t\t{stock['daily_change']}")
    
    print("\n=== 完成 ===")
    
    return top30

if __name__ == "__main__":
    yesterday = "20260408"
    calculate_top30_for_date(yesterday)
