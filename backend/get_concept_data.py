import requests
import re
from datetime import datetime, timedelta
from models.database import Database
import time
import pywencai

def is_trade_day(date_obj):
    """
    判断是否为交易日（简单实现，周末不是交易日）
    """
    return date_obj.weekday() < 5  # 0-4 代表周一到周五

def get_trade_days(start_date, end_date):
    """
    获取指定日期范围内的交易日（简单实现，假设除了周末都是交易日）
    """
    trade_days = []
    current_date = start_date
    while current_date <= end_date:
        if is_trade_day(current_date):
            trade_days.append(current_date.strftime('%Y-%m-%d'))
        current_date += timedelta(days=1)
    return trade_days

def parse_concept_data(df, date):
    """
    从DataFrame解析板块数据
    """
    data = []
    
    if df is None or len(df) == 0:
        return data
    
    date_str = date.replace('-', '')
    
    for idx, row in df.iterrows():
        try:
            code = str(row['code'])
            name = str(row['指数简称'])
            
            # 提取板块类型
            concept_type = '同花顺板块指数'
            if '指数@同花顺板块指数' in row:
                type_val = str(row['指数@同花顺板块指数'])
                if type_val and type_val != 'nan':
                    concept_type = type_val
            
            # 查找收盘价列
            close_col = None
            for col in df.columns:
                if '收盘价' in col and date_str in col:
                    close_col = col
                    break
            
            # 查找涨跌幅列
            change_col = None
            for col in df.columns:
                if '涨跌幅' in col and date_str in col:
                    change_col = col
                    break
            
            # 查找成交额列
            volume_col = None
            for col in df.columns:
                if '成交额' in col and date_str in col:
                    volume_col = col
                    break
            
            close = 0.0
            change_pct = 0.0
            volume = 0.0
            
            if close_col:
                close = float(row[close_col]) if str(row[close_col]) != 'nan' else 0.0
            if change_col:
                change_pct = float(row[change_col]) if str(row[change_col]) != 'nan' else 0.0
            if volume_col:
                volume = float(row[volume_col]) if str(row[volume_col]) != 'nan' else 0.0
            
            data.append({
                'rank': idx + 1,
                'concept_code': code,
                'concept_name': name,
                'concept_type': concept_type,
                'close': close,
                'change_pct': change_pct,
                'volume': volume,
                'date': date
            })
            
        except Exception as e:
            print(f"解析第 {idx+1} 条数据失败: {e}")
            continue
    
    return data

def get_concept_data_from_url(date):
    """
    从同花顺URL获取指定日期的板块数据（使用pywencai）
    """
    cookie = "Hm_lvt_722143063e4892925903024537075d0d=1762053407; Hm_lvt_929f8b362150b1f77b477230541dbbc2=1762053407; _ga=GA1.1.1772044638.1774584118; Hm_lvt_69929b9dce4c22a060bd22d703b2a280=1775223552; Hm_lvt_78c58f01938e4d85eaf619eae71b4ed1=1775223586; _ga_H2RK0R0681=GS2.1.s1775227329$o3$g0$t1775227329$j60$l0$h0; _clck=1c5tbcc%7C2%7Cg54%7C0%7C0; cid=41e74c739a4f0f36057ade69f7eef7941775870880; u_ukey=A10702B8689642C6BE607730E11E6E4A; u_uver=1.0.0; u_dpass=svWfMekV956NiwfTjTb2Ek140n5KoCAMzXKmxnnbj7gt9XCkSCI8PbsyWPa6SXHSHi80LrSsTFH9a%2B6rtRvqGg%3D%3D; u_did=0F0E7AACFAA84FA9A5944F2155A44AC3; u_ttype=WEB; ttype=WEB; user=MDptb181aGZybWl4NDM6Ok5vbmU6NTAwOjc4MDc2NTM0ODo3LDExMTExMTExMTExLDQwOzQ0LDExLDQwOzYsMSw0MDs1LDEsNDA7MSwxMDEsNDA7MiwxLDQwOzMsMSw0MDs1LDEsNDA7OCwwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMSw0MDsxMDIsMSw0MDoyNDo6Ojc3MDc2NTM0ODoxNzc1OTA2MjcwOjo6MTc0MDYzMzEyMDo2MDQ4MDA6MDoxYWM4ZmFhZDliYzZmYmI2ZWI1YzE4ZjA1YmI0NWNkNzg6ZGVmYXVsdF81OjE%3D; userid=770765348; u_name=mo_5hfrmix43; escapename=mo_5hfrmix43; ticket=8c61d82aba33123d44fab2f75d5ba627; user_status=0; utk=b717ec8df5c2a00e53d5ceca17953cbc; sess_tk=eyJ0eXAiOiJKV1QiLCJhbGciOiJFUzI1NiIsImtpZCI6InNlc3NfdGtfMSIsImJ0eSI6InNlc3NfdGsifQ.eyJqdGkiOiI3OGNkNDViYjA1OGZjMWI1NmViYjZmYmNkOWFhOGZhYzEiLCJpYXQiOjE3NzU5MDYyNzAsImV4cCI6MTc3NjUxMTA3MCwic3ViIjoiNzcwNzY1MzQ4IiwiaXNzIjoidXBhc3MuMTBqcWthLmNvbS5jbiIsImF1ZCI6IjIwMjAxMTE4NTI4ODkwNzIiLCJhY3QiOiJvZmMiLCJjdWhzIjoiNWVlMDcwMTBiNjhiNDQ3M2JmOWQzYjI1YWZlZTBhYWI2MzMxYTJkNjYzNTFjYTQwZjk0YWQ0NGRkYTAwZGFjYSJ9.Pdk1I16Wh1xKgDtc3p-zJlAXe3ffu2lUSzVBdmb8UWjv5IWdrbeMRB8TeWIn36Kl01KQQ8X5kpaFnwBC-XtVlA; cuc=q3eg4akd2i90; _clsk=6ys1ii1hzxuo%7C1775906273987%7C2%7C1%7C; v=AypyilT0Nz_8X7tTybj02JWye5vGm6-coB4imbTi03MJs8QFnCv-BXCvcryH"
    
    try:
        # 转换日期格式 2026-04-13 -> 20260413
        dt = datetime.strptime(date, '%Y-%m-%d')
        display_date = f"{dt.year}{dt.month:02d}{dt.day:02d}"
        
        print(f"使用pywencai获取 {display_date} 的数据...")
        
        df = pywencai.get(
            query=f'{display_date}同花顺板块成交额',
            query_type='zhishu',
            cookie=cookie,
            loop=True,
            log=False
        )
        
        if df is not None and len(df) > 0:
            print(f"成功获取 {len(df)} 条数据")
            return df
        else:
            print(f"未获取到数据")
            return None
            
    except Exception as e:
        print(f"获取 {date} 数据失败: {e}")
        return None

def save_concept_data_to_db(data):
    """
    将板块数据保存到数据库
    """
    db = Database()
    db.connect()
    db.create_tables()
    
    try:
        for item in data:
            # 插入板块信息
            db.insert_concept(item['concept_code'], item['concept_name'], item.get('concept_type', ''))
            
            # 插入板块每日数据
            date_str = item['date'].replace('-', '')
            db.insert_concept_daily(
                item['concept_code'],
                date_str,
                item['close'],
                item['change_pct'],
                item.get('volume', 0.0)
            )
        
        print(f"成功保存 {len(data)} 条板块数据")
    finally:
        db.close()

def get_mock_data(date):
    """
    获取模拟数据（用于测试）
    """
    import random
    mock_data = [
        {'rank': 1, 'concept_code': '885767', 'concept_name': '互联网保险', 'concept_type': '概念', 'close': 1003.60, 'change_pct': 1.51, 'date': date},
        {'rank': 2, 'concept_code': '885918', 'concept_name': '快手概念', 'concept_type': '概念', 'close': 2036.48, 'change_pct': 0.33, 'date': date},
        {'rank': 3, 'concept_code': '886068', 'concept_name': 'Sora概念(文生视频)', 'concept_type': '概念', 'close': 2349.76, 'change_pct': 0.32, 'date': date},
        {'rank': 4, 'concept_code': '886090', 'concept_name': '智谱AI', 'concept_type': '概念', 'close': 1533.26, 'change_pct': 0.93, 'date': date},
        {'rank': 5, 'concept_code': '886040', 'concept_name': 'MLOps概念', 'concept_type': '概念', 'close': 1100.68, 'change_pct': 0.89, 'date': date},
        {'rank': 6, 'concept_code': '886058', 'concept_name': '华为昇腾', 'concept_type': '概念', 'close': 1706.25, 'change_pct': 0.44, 'date': date},
        {'rank': 7, 'concept_code': '885893', 'concept_name': '国家大基金持股', 'concept_type': '概念', 'close': 2197.96, 'change_pct': 1.48, 'date': date},
        {'rank': 8, 'concept_code': '886098', 'concept_name': '小红书概念', 'concept_type': '概念', 'close': 1577.49, 'change_pct': 0.41, 'date': date},
        {'rank': 9, 'concept_code': '886071', 'concept_name': 'AI PC', 'concept_type': '概念', 'close': 2164.84, 'change_pct': 1.59, 'date': date},
        {'rank': 10, 'concept_code': '886102', 'concept_name': '中国AI 50', 'concept_type': '概念', 'close': 1947.18, 'change_pct': 1.34, 'date': date},
        {'rank': 11, 'concept_code': '885889', 'concept_name': 'ChatGPT概念', 'concept_type': '概念', 'close': 1678.32, 'change_pct': 0.78, 'date': date},
        {'rank': 12, 'concept_code': '885946', 'concept_name': '东数西算', 'concept_type': '概念', 'close': 1234.56, 'change_pct': 1.12, 'date': date},
        {'rank': 13, 'concept_code': '886012', 'concept_name': 'Web3.0', 'concept_type': '概念', 'close': 876.54, 'change_pct': 0.56, 'date': date},
        {'rank': 14, 'concept_code': '885936', 'concept_name': '信创', 'concept_type': '概念', 'close': 1456.78, 'change_pct': 0.89, 'date': date},
        {'rank': 15, 'concept_code': '885922', 'concept_name': '汽车芯片', 'concept_type': '概念', 'close': 2345.67, 'change_pct': 1.23, 'date': date},
        {'rank': 16, 'concept_code': '885929', 'concept_name': '钠离子电池', 'concept_type': '概念', 'close': 1890.12, 'change_pct': 0.67, 'date': date},
        {'rank': 17, 'concept_code': '885919', 'concept_name': '虚拟数字人', 'concept_type': '概念', 'close': 1123.45, 'change_pct': 0.98, 'date': date},
        {'rank': 18, 'concept_code': '885947', 'concept_name': '钒电池', 'concept_type': '概念', 'close': 987.65, 'change_pct': 0.54, 'date': date},
        {'rank': 19, 'concept_code': '885924', 'concept_name': 'NFT概念', 'concept_type': '概念', 'close': 1567.89, 'change_pct': 1.02, 'date': date},
        {'rank': 20, 'concept_code': '885722', 'concept_name': '电子竞技', 'concept_type': '概念', 'close': 1789.01, 'change_pct': 0.87, 'date': date},
        {'rank': 21, 'concept_code': '885764', 'concept_name': '电子化学品', 'concept_type': '行业', 'close': 2100.23, 'change_pct': 1.15, 'date': date},
        {'rank': 22, 'concept_code': '885843', 'concept_name': '金属新材料', 'concept_type': '行业', 'close': 1678.90, 'change_pct': 0.72, 'date': date},
        {'rank': 23, 'concept_code': '885695', 'concept_name': '其他塑料制品', 'concept_type': '行业', 'close': 1234.89, 'change_pct': 0.95, 'date': date},
        {'rank': 24, 'concept_code': '885734', 'concept_name': '其他电子', 'concept_type': '行业', 'close': 987.56, 'change_pct': 0.63, 'date': date},
        {'rank': 25, 'concept_code': '885828', 'concept_name': '其他专用设备', 'concept_type': '行业', 'close': 1456.23, 'change_pct': 1.08, 'date': date},
        {'rank': 26, 'concept_code': '885912', 'concept_name': '工程机械', 'concept_type': '行业', 'close': 2345.45, 'change_pct': 0.81, 'date': date},
        {'rank': 27, 'concept_code': '885704', 'concept_name': '玻璃玻纤', 'concept_type': '行业', 'close': 1890.78, 'change_pct': 1.21, 'date': date},
        {'rank': 28, 'concept_code': '885802', 'concept_name': '橡胶', 'concept_type': '行业', 'close': 1123.67, 'change_pct': 0.58, 'date': date},
        {'rank': 29, 'concept_code': '885952', 'concept_name': '摩托车及其他', 'concept_type': '行业', 'close': 1567.34, 'change_pct': 1.32, 'date': date},
        {'rank': 30, 'concept_code': '885836', 'concept_name': '计算机应用', 'concept_type': '行业', 'close': 1789.56, 'change_pct': 0.91, 'date': date},
    ]
    
    # 随机添加一些涨跌幅变化，让数据更真实
    for item in mock_data:
        item['change_pct'] = round(random.uniform(-3, 5), 2)
    
    return mock_data

def fetch_and_save_concept_data(start_date, end_date, use_mock=False):
    """
    获取指定日期范围内的板块数据并保存到数据库
    """
    # 获取交易日列表
    start = datetime.strptime(start_date, '%Y-%m-%d')
    end = datetime.strptime(end_date, '%Y-%m-%d')
    trade_days = get_trade_days(start, end)
    
    print(f"开始获取 {start_date} 到 {end_date} 的板块数据")
    print(f"交易日数量: {len(trade_days)}")
    
    all_data = []
    
    for date in trade_days:
        print(f"处理日期: {date}")
        
        if use_mock:
            data = get_mock_data(date)
        else:
            df = get_concept_data_from_url(date)
            if df is not None:
                data = parse_concept_data(df, date)
            else:
                data = []
        
        if data:
            all_data.extend(data)
            save_concept_data_to_db(data)
            print(f"  保存了 {len(data)} 条数据")
        else:
            print(f"  未获取到数据")
        
        # 避免请求过快
        time.sleep(1)
    
    print(f"完成！共保存 {len(all_data)} 条数据")
    return all_data

if __name__ == "__main__":
    # 获取近10日的数据（2026-04-01 到 2026-04-10）
    end_date = '2026-04-10'
    start_date = '2026-04-01'
    
    fetch_and_save_concept_data(start_date, end_date, use_mock=True)
