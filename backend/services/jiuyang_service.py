import requests
import json
import time
from datetime import datetime, timedelta
from models.database import Database

JIUYANG_URL = "https://app.jiuyangongshe.com/jystock-app/api/v1/action/field"

HEADERS = {
    "accept": "application/json, text/plain, */*",
    "accept-encoding": "gzip, deflate, br, zstd",
    "accept-language": "zh-CN,zh;q=0.9",
    "connection": "keep-alive",
    "content-type": "application/json",
    "host": "app.jiuyangongshe.com",
    "origin": "https://www.jiuyangongshe.com",
    "platform": "3",
    "referer": "https://www.jiuyangongshe.com/action",
    "sec-ch-ua": '"Not A(Brand";v="8", "Chromium";v="132", "Google Chrome";v="132"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
    "token": "ae7353a8af85f29021935df2dbdd74d5",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36"
}

COOKIE = "SESSION=ZTlhYmFkOWQtZjg2Mi00ZTA1LTkxYjAtMTJjMjAzMDFmODRk; Hm_lvt_58aa18061df7855800f2a1b32d6da7f4=1775223702,1775713239,1775884456,1776123373; Hm_lpvt_58aa18061df7855800f2a1b32d6da7f4=1776123373"

def parse_cookie(cookie_str):
    cookies = {}
    for item in cookie_str.split('; '):
        if '=' in item:
            key, value = item.split('=', 1)
            cookies[key] = value
    return cookies

def fetch_jiuyang_data(date_str):
    """
    获取指定日期的韭研公社数据
    """
    headers = HEADERS.copy()
    headers["timestamp"] = str(int(time.time() * 1000))
    headers["referer"] = f"https://www.jiuyangongshe.com/action/{date_str}"
    
    cookies = parse_cookie(COOKIE)
    
    data = {
        "date": date_str,
        "pc": 1
    }
    
    try:
        response = requests.post(JIUYANG_URL, headers=headers, cookies=cookies, json=data)
        if response.status_code == 200:
            result = response.json()
            if result.get("errCode") == "0":
                return result.get("data", [])
            else:
                print(f"获取 {date_str} 数据失败: {result.get('msg')}")
                return None
        else:
            print(f"请求失败，状态码: {response.status_code}")
            return None
    except Exception as e:
        print(f"请求异常: {e}")
        return None

def save_jiuyang_data_to_db(data_list, date_str):
    """
    将韭研公社数据保存到数据库
    """
    db = Database()
    if not db.connect():
        return False
    
    try:
        db.clear_jiuyang_data_by_date(date_str)
        
        for theme_data in data_list:
            theme_title = theme_data.get("name", "")
            stock_list = theme_data.get("list", [])
            
            theme_id = db.insert_jiuyang_theme(theme_title, date_str)
            if not theme_id:
                continue
            
            for stock_data in stock_list:
                code = stock_data.get("code", "")
                name = stock_data.get("name", "")
                article = stock_data.get("article", {})
                action_info = article.get("action_info", {})
                num = action_info.get("num", "")
                user = article.get("user", {})
                
                article_id = article.get("article_id", "")
                title = article.get("title", "")
                expound = action_info.get("expound", "")
                action_time = action_info.get("time", "")
                price = action_info.get("price")
                shares_range = action_info.get("shares_range")
                create_time = action_info.get("create_time", "")
                update_time = action_info.get("update_time", "")
                sort_no = action_info.get("sort_no")
                comment_count = article.get("comment_count", 0)
                like_count = article.get("like_count", 0)
                forward_count = article.get("forward_count", 0)
                step_count = article.get("step_count", 0)
                is_like = article.get("is_like", 0)
                is_step = article.get("is_step", 0)
                is_crawl = action_info.get("is_crawl", 0)
                is_recommend = action_info.get("is_recommend", 0)
                is_delete = action_info.get("is_delete", "0")
                user_id = user.get("user_id", "")
                user_nickname = user.get("nickname", "")
                user_avatar = user.get("avatar", "")
                
                db.insert_jiuyang_stock_action(
                    theme_id, code, name, article_id, title, expound,
                    action_time, price, shares_range, create_time, update_time,
                    sort_no, comment_count, like_count, forward_count, step_count,
                    is_like, is_step, is_crawl, is_recommend, is_delete,
                    user_id, user_nickname, user_avatar, date_str, num
                )
        
        print(f"成功保存 {date_str} 的韭研公社数据")
        return True
    except Exception as e:
        print(f"保存数据失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

def fetch_and_save_jiuyang_data(date_str):
    """
    获取并保存指定日期的韭研公社数据
    """
    print(f"正在获取 {date_str} 的韭研公社数据...")
    data = fetch_jiuyang_data(date_str)
    if data:
        print(f"获取到 {len(data)} 个题材")
        save_jiuyang_data_to_db(data, date_str)
        return True
    else:
        print(f"未获取到 {date_str} 的数据")
        return False

def is_trading_day(date_str):
    """
    简单判断是否为交易日（周一到周五）
    """
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        return dt.weekday() < 5
    except:
        return False

def get_recent_trading_days(count=10):
    """
    获取最近N个交易日
    """
    days = []
    today = datetime.now()
    
    for i in range(count * 2):
        date_str = (today - timedelta(days=i)).strftime("%Y-%m-%d")
        if is_trading_day(date_str):
            days.append(date_str)
            if len(days) >= count:
                break
    
    return days[::-1]

def fetch_recent_jiuyang_data(days=10):
    """
    获取最近N个交易日的韭研公社数据
    """
    trading_days = get_recent_trading_days(days)
    print(f"准备获取 {len(trading_days)} 个交易日的数据: {trading_days}")
    
    success_count = 0
    for date_str in trading_days:
        if fetch_and_save_jiuyang_data(date_str):
            success_count += 1
        time.sleep(1)
    
    print(f"完成！成功获取 {success_count}/{len(trading_days)} 天的数据")
    return success_count

if __name__ == "__main__":
    fetch_recent_jiuyang_data(10)
