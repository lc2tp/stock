
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from services.jiuyang_service import fetch_jiuyang_data
from models.database import Database
from datetime import datetime, timedelta

db = Database()
db.db_path = os.path.join(os.path.dirname(__file__), 'backend', 'stock_system.db')
if not db.connect():
    print("数据库连接失败")
    sys.exit(1)

print("正在获取最近几天的数据...\n")

dates_to_refresh = ['2026-04-08', '2026-04-09', '2026-04-10', '2026-04-13', '2026-04-14']

for date_str in dates_to_refresh:
    print(f"正在处理 {date_str}...")
    
    # 先删除该日期的旧数据
    cursor = db.connection.cursor()
    cursor.execute("DELETE FROM jiuyang_stock_action WHERE date = ?", (date_str,))
    cursor.execute("DELETE FROM jiuyang_theme WHERE date = ?", (date_str,))
    db.connection.commit()
    cursor.close()
    
    # 获取数据
    data = fetch_jiuyang_data(date_str)
    if not data:
        print(f"⚠️ {date_str} 没有获取到数据")
        print("-" * 50)
        continue
    
    # 直接保存到数据库（不调用 service 里的方法，避免路径问题）
    count_theme = 0
    count_stock = 0
    
    for theme_data in data:
        theme_title = theme_data.get("name", "")
        if not theme_title:
            continue
        
        # 插入题材
        cursor = db.connection.cursor()
        cursor.execute(
            "INSERT OR IGNORE INTO jiuyang_theme (title, date) VALUES (?, ?)",
            (theme_title, date_str)
        )
        db.connection.commit()
        
        # 获取题材ID
        cursor.execute("SELECT id FROM jiuyang_theme WHERE title = ? AND date = ?", (theme_title, date_str))
        result = cursor.fetchone()
        cursor.close()
        
        if not result:
            continue
        theme_id = result[0]
        count_theme += 1
        
        # 处理股票
        stock_list = theme_data.get("list", [])
        for stock_data in stock_list:
            code = stock_data.get("code", "")
            name = stock_data.get("name", "")
            article = stock_data.get("article", {})
            action_info = article.get("action_info", {})
            user = article.get("user", {})
            
            article_id = article.get("article_id", "")
            title = article.get("title", "")
            expound = action_info.get("expound", "")
            action_time = action_info.get("time", "")
            price = action_info.get("price", 0)
            shares_range = action_info.get("shares_range", 0)
            create_time = article.get("create_time", "")
            update_time = action_info.get("update_time", "")
            sort_no = action_info.get("sort_no", 0)
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
            num = action_info.get("num", "")
            
            # 插入股票
            cursor = db.connection.cursor()
            cursor.execute(
                """INSERT OR REPLACE INTO jiuyang_stock_action 
                   (theme_id, code, name, article_id, title, expound, action_time, price, shares_range,
                    create_time, update_time, sort_no, comment_count, like_count, forward_count, step_count,
                    is_like, is_step, is_crawl, is_recommend, is_delete, user_id, user_nickname, user_avatar, date, num)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (theme_id, code, name, article_id, title, expound, action_time, price, shares_range,
                 create_time, update_time, sort_no, comment_count, like_count, forward_count, step_count,
                 is_like, is_step, is_crawl, is_recommend, is_delete, user_id, user_nickname, user_avatar, date_str, num)
            )
            db.connection.commit()
            cursor.close()
            count_stock += 1
    
    print(f"✅ {date_str} 保存成功！{count_theme} 个题材，{count_stock} 只股票")
    print("-" * 50)

print("\n✅ 全部完成！")
db.close()

