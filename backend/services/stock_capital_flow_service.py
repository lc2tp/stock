from datetime import datetime, timedelta
from models.database import Database

def fetch_stock_capital_flow(date_str):
    """
    获取指定日期的个股资金流向数据（使用pywencai）
    格式类似：20260414主力流向
    """
    try:
        import pywencai
        
        cookie = "Hm_lvt_722143063e4892925903024537075d0d=1762053407; Hm_lvt_929f8b362150b1f77b477230541dbbc2=1762053407; _ga=GA1.1.1772044638.1774584118; Hm_lvt_69929b9dce4c22a060bd22d703b2a280=1775223552; Hm_lvt_78c58f01938e4d85eaf619eae71b4ed1=1775223586; _ga_H2RK0R0681=GS2.1.s1775227329$o3$g0$t1775227329$j60$l0$h0; _clck=1c5tbcc%7C2%7Cg54%7C0%7C0; cid=41e74c739a4f0f36057ade69f7eef7941775870880; u_ukey=A10702B8689642C6BE607730E11E6E4A; u_uver=1.0.0; u_dpass=svWfMekV956NiwfTjTb2Ek140n5KoCAMzXKmxnnbj7gt9XCkSCI8PbsyWPa6SXHSHi80LrSsTFH9a%2B6rtRvqGg%3D%3D; u_did=0F0E7AACFAA84FA9A5944F2155A44AC3; u_ttype=WEB; ttype=WEB; user=MDptb181aGZybWl4NDM6Ok5vbmU6NTAwOjc4MDc2NTM0ODo3LDExMTExMTExMTExLDQwOzQ0LDExLDQwOzYsMSw0MDs1LDEsNDA7MSwxMDEsNDA7MiwxLDQwOzMsMSw0MDs1LDEsNDA7OCwwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMSw0MDsxMDIsMSw0MDoyNDo6Ojc3MDc2NTM0ODoxNzc1OTA2MjcwOjo6MTc0MDYzMzEyMDo2MDQ4MDA6MDoxYWM4ZmFhZDliYzZmYmI2ZWI1YzE4ZjA1YmI0NWNkNzg6ZGVmYXVsdF81OjE%3D; userid=770765348; u_name=mo_5hfrmix43; escapename=mo_5hfrmix43; ticket=8c61d82aba33123d44fab2f75d5ba627; user_status=0; utk=b717ec8df5c2a00e53d5ceca17953cbc; sess_tk=eyJ0eXAiOiJKV1QiLCJhbGciOiJFUzI1NiIsImtpZCI6InNlc3NfdGtfMSIsImJ0eSI6InNlc3NfdGsifQ.eyJqdGkiOiI3OGNkNDViYjA1OGZjMWI1NmViYjZmYmNkOWFhOGZhYzEiLCJpYXQiOjE3NzU5MDYyNzAsImV4cCI6MTc3NjUxMTA3MCwic3ViIjoiNzcwNzY1MzQ4IiwiaXNzIjoidXBhc3MuMTBqcWthLmNvbS5jbiIsImF1ZCI6IjIwMjAxMTE4NTI4ODkwNzIiLCJhY3QiOiJvZmMiLCJjdWhzIjoiNWVlMDcwMTBiNjhiNDQ3M2JmOWQzYjI1YWZlZTBhYWI2MzMxYTJkNjYzNTFjYTQwZjk0YWQ0NGRkYTAwZGFjYSJ9.Pdk1I16Wh1xKgDtc3p-zJlAXe3ffu2lUSzVBdmb8UWjv5IWdrbeMRB8TeWIn36Kl01KQQ8X5kpaFnwBC-XtVlA; cuc=q3eg4akd2i90; _clsk=6ys1ii1hzxuo%7C1775906273987%7C2%7C1%7C; v=AypyilT0Nz_8X7tTybj02JWye5vGm6-coB4imbTi03MJs8QFnCv-BXCvcryH"
        
        query = f"{date_str}主力流向"
        print(f"正在查询个股资金流向: {query}")
        
        df = pywencai.get(
            query=query,
            query_type='stock',
            cookie=cookie,
            loop=True,
            log=False
        )
        
        if df is None or df.empty:
            print(f"未获取到 {date_str} 的个股资金流向数据")
            return []
        
        print(f"DataFrame列名: {list(df.columns)}")
        
        data_list = []
        for idx, row in df.iterrows():
            try:
                code = str(row.get('股票代码', ''))
                name = str(row.get('股票简称', ''))
                
                # 转换为 tushare 格式
                ts_code = None
                symbol = None
                if code:
                    if code.startswith('6'):
                        ts_code = f"{code}.SH"
                        symbol = code
                    elif code.startswith('0') or code.startswith('3'):
                        ts_code = f"{code}.SZ"
                        symbol = code
                
                # 动态查找资金流向列
                main_flow_col = None
                for col in df.columns:
                    if '主力资金流向' in col:
                        main_flow_col = col
                        break
                
                main_capital_flow = 0.0
                if main_flow_col:
                    val = row[main_flow_col]
                    if str(val) != 'nan':
                        main_capital_flow = float(val)
                
                # 获取涨跌幅
                change_percent = 0.0
                for col in df.columns:
                    if '涨跌幅' in col or '涨跌幅' in col:
                        val = row[col]
                        if str(val) != 'nan':
                            change_percent = float(val)
                        break
                
                if ts_code and symbol:
                    data_list.append({
                        'ts_code': ts_code,
                        'symbol': symbol,
                        'name': name,
                        'main_capital_flow': main_capital_flow,
                        'change_percent': change_percent
                    })
            except Exception as e:
                print(f"解析第 {idx+1} 条数据失败: {e}")
                continue
        
        print(f"获取到 {len(data_list)} 条个股资金流向数据")
        return data_list
    except Exception as e:
        print(f"获取个股资金流向数据失败: {e}")
        import traceback
        traceback.print_exc()
        return []

def save_stock_capital_flow_to_db(data_list, date_str):
    """
    将个股资金流向数据保存到数据库
    """
    db = Database()
    if not db.connect():
        return False
    
    try:
        for data in data_list:
            db.insert_stock_capital_flow(
                data.get('ts_code'),
                data.get('symbol'),
                data.get('name'),
                date_str,
                data.get('main_capital_flow'),
                data.get('change_percent')
            )
        print(f"已保存 {len(data_list)} 条个股资金流向数据到 {date_str}")
        return True
    except Exception as e:
        print(f"保存个股资金流向数据失败: {e}")
        return False
    finally:
        db.close()

def fetch_and_save_stock_capital_flow(date_str=None):
    """
    获取并保存指定日期的个股资金流向数据
    """
    if not date_str:
        date_str = datetime.now().strftime("%Y-%m-%d")
    
    date_num = date_str.replace("-", "")
    
    data_list = fetch_stock_capital_flow(date_num)
    
    if data_list:
        return save_stock_capital_flow_to_db(data_list, date_str)
    
    return False

def calculate_consecutive_stock_capital_flow(days=2, flow_type='inflow'):
    """
    计算连续N日资金流入/流出的个股
    days: 连续天数（2-6）
    flow_type: 'inflow' 连续流入，'outflow' 连续流出
    """
    db = Database()
    if not db.connect():
        return []
    
    try:
        dates = db.get_stock_capital_flow_dates()
        if len(dates) < days:
            return []
        
        target_dates = dates[:days]
        
        all_data = db.get_stock_capital_flow(target_dates[-1], target_dates[0])
        
        stock_data = {}
        for data in all_data:
            ts_code = data['ts_code']
            if ts_code not in stock_data:
                stock_data[ts_code] = {
                    'ts_code': ts_code,
                    'symbol': data['symbol'],
                    'name': data['name'],
                    'daily_flows': {},
                    'daily_changes': {}
                }
            stock_data[ts_code]['daily_flows'][data['date']] = data['main_capital_flow']
            stock_data[ts_code]['daily_changes'][data['date']] = data.get('change_percent', 0)
        
        result = []
        for ts_code, data in stock_data.items():
            has_all_dates = True
            is_consecutive = True
            
            for d in target_dates:
                if d not in data['daily_flows']:
                    has_all_dates = False
                    break
                
                flow = data['daily_flows'][d]
                if flow is None:
                    has_all_dates = False
                    break
                
                if flow_type == 'inflow' and flow <= 0:
                    is_consecutive = False
                    break
                
                if flow_type == 'outflow' and flow >= 0:
                    is_consecutive = False
                    break
            
            if has_all_dates and is_consecutive:
                total_flow = sum(data['daily_flows'][d] for d in target_dates)
                result.append({
                    'ts_code': data['ts_code'],
                    'symbol': data['symbol'],
                    'name': data['name'],
                    'days': days,
                    'flow_type': flow_type,
                    'total_net_inflow': total_flow,
                    'daily_flows': data['daily_flows'],
                    'daily_changes': data['daily_changes']
                })
        
        if flow_type == 'inflow':
            result.sort(key=lambda x: x['total_net_inflow'], reverse=True)
        else:
            result.sort(key=lambda x: x['total_net_inflow'])
        
        return result
    except Exception as e:
        print(f"计算连续个股资金流向失败: {e}")
        return []
    finally:
        db.close()
