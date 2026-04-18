
import tushare as ts
import pandas as pd
from datetime import datetime, timedelta
from config import TUSHARE_TOKEN
from models.database import Database

class TushareService:
    def __init__(self):
        try:
            ts.set_token(TUSHARE_TOKEN)
        except Exception as e:
            print(f"设置 Tushare token 时出现警告（不影响使用）: {e}")
        self.pro = ts.pro_api()
        self.db = Database()
        self.db.connect()
        self.db.create_tables()
        self.db.close()
    
    def get_trade_days(self, end_date, count=11, cursor=None):
        """
        获取指定日期之前的N个交易日
        :param end_date: 结束日期，格式为'YYYYMMDD'
        :param count: 交易日数量
        :param cursor: 已有的数据库游标（可选）
        :return: 交易日列表，按日期升序排列
        """
        trade_days = []
        
        try:
            # 如果提供了cursor，直接使用
            if cursor:
                cursor.execute('''
                    SELECT DISTINCT date 
                    FROM daily_change 
                    WHERE date <= ? 
                    ORDER BY date DESC 
                    LIMIT ?
                ''', (end_date, count))
                
                results = cursor.fetchall()
                
                if len(results) >= 1:
                    trade_days = [row[0] for row in results]
                    trade_days.sort()
                    print(f"从数据库获取到交易日: {trade_days}")
                    return trade_days
            else:
                # 没有提供cursor，自己连接数据库
                self.db.connect()
                cursor = self.db.connection.cursor()
                
                cursor.execute('''
                    SELECT DISTINCT date 
                    FROM daily_change 
                    WHERE date <= ? 
                    ORDER BY date DESC 
                    LIMIT ?
                ''', (end_date, count))
                
                results = cursor.fetchall()
                
                if len(results) >= 1:
                    trade_days = [row[0] for row in results]
                    trade_days.sort()
                    self.db.close()
                    print(f"从数据库获取到交易日: {trade_days}")
                    return trade_days
                
                self.db.close()
            
        except Exception as e:
            print(f"从数据库获取交易日失败: {e}")
            if not cursor and self.db and self.db.connection:
                self.db.close()
        
        # 备用方案：从 Tushare 获取
        try:
            # 计算开始日期，往前推30天，确保能覆盖足够的交易日
            end_date_obj = datetime.strptime(end_date, '%Y%m%d')
            start_date_obj = end_date_obj - timedelta(days=30)
            start_date = start_date_obj.strftime('%Y%m%d')
            
            # 获取交易日历
            trade_cal = self.pro.trade_cal(
                start_date=start_date,
                end_date=end_date,
                is_open=1  # 1表示交易日
            )
            
            # 提取交易日列表并按日期升序排列
            trade_days = trade_cal['cal_date'].tolist()
            trade_days.sort()
            
            print(f"从Tushare获取到交易日: {trade_days}")
            
            # 如果交易日数量不足，返回所有可用的交易日
            if len(trade_days) < count:
                return trade_days
            
            # 返回最近的count个交易日
            return trade_days[-count:]
            
        except Exception as e:
            print(f"获取交易日历失败: {e}")
            return []
    
    def get_stock_basic_data(self):
        try:
            self.db.connect()
            stock_list = self.pro.stock_basic(exchange='', list_status='L', fields='ts_code,symbol,name,industry,market')
            
            for _, stock in stock_list.iterrows():
                symbol = stock['symbol']
                name = stock['name']
                self.db.insert_stock(symbol, name)
            
            print(f"成功存储 {len(stock_list)} 只股票的基础数据")
            return stock_list
        except Exception as e:
            print(f"获取股票基础数据失败: {e}")
            return []
        finally:
            self.db.close()
    
    def get_top_30_stocks(self, date):
        try:
            stock_list = self.pro.stock_basic(exchange='', list_status='L', fields='ts_code,symbol,name,industry,market')
            
            print(f"获取实时数据，日期：{date}")
            
            stock_symbols = stock_list['symbol'].tolist()[:200]
            print(f"将获取 {len(stock_symbols)} 只股票的实时数据")
            
            batch_size = 50
            self.db.connect()
            successful_symbols = []
            
            for i in range(0, len(stock_symbols), batch_size):
                batch_symbols = stock_symbols[i:i+batch_size]
                
                try:
                    realtime_data = ts.get_realtime_quotes(batch_symbols)
                    
                    for _, realtime_row in realtime_data.iterrows():
                        symbol = realtime_row['code']
                        
                        stock_info = stock_list[stock_list['symbol'] == symbol]
                        
                        if len(stock_info) > 0:
                            stock = stock_info.iloc[0]
                            ts_code = stock['ts_code']
                            
                            current_price = float(realtime_row['price'])
                            pre_close = float(realtime_row['pre_close'])
                            if pre_close > 0:
                                change_percent = ((current_price - pre_close) / pre_close) * 100
                            else:
                                change_percent = 0
                            
                            self.db.insert_daily_change(
                                ts_code=ts_code,
                                symbol=symbol,
                                name=stock['name'],
                                industry=stock['industry'],
                                close=current_price,
                                change=change_percent,
                                date=date
                            )
                            
                            successful_symbols.append(symbol)
                            
                except Exception as e:
                    print(f"获取股票 {batch_symbols} 实时数据失败: {e}")
                    continue
            
            print(f"\n从数据库读取数据并计算10日累计涨幅")
            print(f"成功获取了 {len(successful_symbols)} 只股票的数据")
            
            result = []
            cursor = self.db.connection.cursor()
            
            processed_stocks = stock_list[stock_list['symbol'].isin(successful_symbols)]
            
            for _, stock in processed_stocks.iterrows():
                ts_code = stock['ts_code']
                
                cursor.execute('''
                    SELECT date, close, change
                    FROM daily_change
                    WHERE ts_code = ?
                    ORDER BY date ASC
                ''', (ts_code,))
                
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
                        'symbol': stock['symbol'],
                        'name': stock['name'],
                        'industry': stock['industry'],
                        'ten_day_change': round(ten_day_change, 2),
                        'daily_change': round(daily_change, 2)
                    })
            
            self.db.close()
            
            result.sort(key=lambda x: x['ten_day_change'], reverse=True)
            return result[:30]
            
        except Exception as e:
            print(f"获取股票数据失败: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def calculate_top30(self, target_date, days=10, limit=30):
        """
        计算指定日期的累计涨幅前N的股票
        :param target_date: 日期，格式为'YYYYMMDD'
        :param days: 统计天数，默认为10
        :param limit: 返回数量，默认为30
        :return: 股票列表
        """
        try:
            self.db.connect()
            cursor = self.db.connection.cursor()
            
            # 首先找到 <= target_date 的最后一个实际交易日
            cursor.execute('''
                SELECT DISTINCT date 
                FROM daily_change 
                WHERE date <= ? 
                ORDER BY date DESC 
                LIMIT 1
            ''', (target_date,))
            
            last_trade_day_result = cursor.fetchone()
            
            if not last_trade_day_result:
                print(f"没有找到日期 {target_date} 之前的交易日")
                self.db.close()
                return []
            
            last_trade_day = last_trade_day_result[0]
            print(f"选择日期 {target_date}，使用最后一个交易日: {last_trade_day}")
            
            cursor.execute("SELECT DISTINCT ts_code, symbol, name, industry FROM daily_change WHERE date <= ?", (last_trade_day,))
            stocks_in_db = cursor.fetchall()
            
            print(f"从数据库中找到 {len(stocks_in_db)} 只股票（到{last_trade_day}为止）")
            
            result = []
            
            for stock_row in stocks_in_db:
                ts_code = stock_row[0]
                symbol = stock_row[1]
                name = stock_row[2]
                industry = stock_row[3]
                
                # 获取这只股票在 last_trade_day 之前的所有数据
                query = '''
                    SELECT date, close, change, amount, turnover
                    FROM daily_change
                    WHERE ts_code = ? AND date <= ?
                    ORDER BY date ASC
                '''
                
                cursor.execute(query, (ts_code, last_trade_day))
                stock_data = cursor.fetchall()
                
                if len(stock_data) < 2:
                    continue
                
                # 取最后 N+1 个交易日的数据（因为需要 N 天的涨幅）
                required_days = days + 1
                if len(stock_data) >= required_days:
                    stock_data = stock_data[-required_days:]
                
                # 使用实际获取到的交易日数据
                first_price = stock_data[0][1]
                last_price = stock_data[-1][1]
                
                if first_price > 0:
                    cumulative_change = ((last_price - first_price) / first_price) * 100
                else:
                    cumulative_change = 0
                
                daily_change = stock_data[-1][2] if len(stock_data) > 0 else 0
                
                # 获取最新的收盘价作为价格
                latest_price = stock_data[-1][1] if len(stock_data) > 0 else 0
                
                # 获取最新的成交金额和换手率
                latest_amount = stock_data[-1][3] if len(stock_data) > 0 else 0
                latest_turnover = stock_data[-1][4] if len(stock_data) > 0 else 0
                
                result.append({
                    'ts_code': ts_code,
                    'symbol': symbol,
                    'name': name,
                    'industry': industry,
                    'cumulative_change': round(cumulative_change, 2),
                    'daily_change': round(daily_change, 2),
                    'price': round(latest_price, 2),
                    'amount': round(latest_amount, 2),
                    'turnover': round(latest_turnover, 2)
                })
            
            self.db.close()
            
            result.sort(key=lambda x: x['cumulative_change'], reverse=True)
            return result[:limit]
            
        except Exception as e:
            print(f"计算涨幅失败: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def calculate_ten_day_top30(self, target_date):
        """
        计算指定日期的10日累计涨幅前30的股票（保持兼容）
        :param target_date: 日期，格式为'YYYYMMDD'
        :return: 股票列表
        """
        return self.calculate_top30(target_date, days=10)
    
    def get_rank_change(self, current_date, previous_date):
        current_top30 = self.calculate_ten_day_top30(current_date)
        previous_top30 = self.calculate_ten_day_top30(previous_date)
        
        current_rank = {stock['ts_code']: i+1 for i, stock in enumerate(current_top30)}
        previous_rank = {stock['ts_code']: i+1 for i, stock in enumerate(previous_top30)}
        
        result = []
        
        # 处理当前30名的股票
        for stock in current_top30:
            ts_code = stock['ts_code']
            current_r = current_rank.get(ts_code, 999)
            previous_r = previous_rank.get(ts_code, 999)
            rank_change = previous_r - current_r if previous_r != 999 else 'NEW'
            
            # 兼容新旧字段格式
            stock_copy = stock.copy()
            if 'cumulative_change' in stock_copy and 'ten_day_change' not in stock_copy:
                stock_copy['ten_day_change'] = stock_copy['cumulative_change']
            
            result.append({
                **stock_copy,
                'current_rank': current_r,
                'previous_rank': previous_r,
                'rank_change': rank_change
            })
        
        # 处理从昨天30名中消失的股票
        for stock in previous_top30:
            ts_code = stock['ts_code']
            if ts_code not in current_rank:
                previous_r = previous_rank.get(ts_code, 999)
                
                # 为消失的股票创建一个条目
                out_stock = {
                    'ts_code': ts_code,
                    'symbol': stock['symbol'],
                    'name': stock['name'],
                    'industry': stock['industry'],
                    'ten_day_change': 0,  # 消失的股票没有当前数据
                    'daily_change': 0,    # 消失的股票没有当前数据
                    'current_rank': 999,   # 不在当前30名
                    'previous_rank': previous_r,
                    'rank_change': 'OUT'   # 标记为消失
                }
                
                result.append(out_stock)
        
        return result
