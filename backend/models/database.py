import sqlite3
from datetime import datetime
import os

class Database:
    def __init__(self, db_path='stock_system.db'):
        self.db_path = db_path
        self.connection = None
    
    def connect(self):
        """
        连接数据库
        """
        try:
            self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
            self.connection.row_factory = sqlite3.Row
            cursor = self.connection.cursor()
            cursor.execute("PRAGMA encoding = 'UTF-8'")
            self.connection.commit()
            cursor.close()
            print(f"数据库连接成功: {self.db_path}")
            return True
        except Exception as e:
            print(f"数据库连接失败: {e}")
            return False
    
    def create_tables(self):
        """
        创建数据库表
        """
        if not self.connection:
            self.connect()
        
        cursor = self.connection.cursor()
        
        # 创建题材表
        create_theme_table = """
        CREATE TABLE IF NOT EXISTS theme (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        
        # 创建股票表
        create_stock_table = """
        CREATE TABLE IF NOT EXISTS stock (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT NOT NULL UNIQUE,
            name TEXT NOT NULL,
            market TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        
        # 创建涨停记录表
        create_limit_up_table = """
        CREATE TABLE IF NOT EXISTS limit_up (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            stock_id INTEGER NOT NULL,
            theme_id INTEGER NOT NULL,
            date DATE NOT NULL,
            time TEXT,
            reason TEXT,
            board_count INTEGER DEFAULT 1,
            price REAL,
            change_percent REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (stock_id) REFERENCES stock(id),
            FOREIGN KEY (theme_id) REFERENCES theme(id),
            UNIQUE(stock_id, date)
        )
        """
        
        # 创建每日涨幅表
        create_daily_change_table = """
        CREATE TABLE IF NOT EXISTS daily_change (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts_code TEXT NOT NULL,
            symbol TEXT NOT NULL,
            name TEXT NOT NULL,
            industry TEXT,
            close REAL NOT NULL,
            change REAL NOT NULL,
            amount REAL,
            turnover REAL,
            date TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(ts_code, date)
        )
        """
        
        # 创建每日涨幅前30表
        create_daily_top30_table = """
        CREATE TABLE IF NOT EXISTS daily_top30 (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts_code TEXT NOT NULL,
            symbol TEXT NOT NULL,
            name TEXT NOT NULL,
            industry TEXT,
            ten_day_change REAL NOT NULL,
            daily_change REAL NOT NULL,
            date TEXT NOT NULL,
            rank INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(ts_code, date)
        )
        """
        
        # 创建板块表
        create_concept_table = """
        CREATE TABLE IF NOT EXISTS concept (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            concept_code TEXT NOT NULL UNIQUE,
            concept_name TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        
        # 创建板块每日涨幅表
        create_concept_daily_table = """
        CREATE TABLE IF NOT EXISTS concept_daily (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            concept_code TEXT NOT NULL,
            date TEXT NOT NULL,
            close REAL NOT NULL,
            change_pct REAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(concept_code, date)
        )
        """
        
        # 创建韭研公社题材表
        create_jiuyang_theme_table = """
        CREATE TABLE IF NOT EXISTS jiuyang_theme (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            date TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(title, date)
        )
        """
        
        # 创建韭研公社股票异动表
        create_jiuyang_stock_action_table = """
        CREATE TABLE IF NOT EXISTS jiuyang_stock_action (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            theme_id INTEGER NOT NULL,
            code TEXT NOT NULL,
            name TEXT NOT NULL,
            article_id TEXT,
            title TEXT,
            expound TEXT,
            action_time TEXT,
            price REAL,
            shares_range REAL,
            create_time TEXT,
            update_time TEXT,
            sort_no INTEGER,
            comment_count INTEGER DEFAULT 0,
            like_count INTEGER DEFAULT 0,
            forward_count INTEGER DEFAULT 0,
            step_count INTEGER DEFAULT 0,
            is_like INTEGER DEFAULT 0,
            is_step INTEGER DEFAULT 0,
            is_crawl INTEGER DEFAULT 0,
            is_recommend INTEGER DEFAULT 0,
            is_delete TEXT DEFAULT '0',
            user_id TEXT,
            user_nickname TEXT,
            user_avatar TEXT,
            date TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (theme_id) REFERENCES jiuyang_theme(id),
            UNIQUE(code, date)
        )
        """
        
        # 执行创建表语句
        try:
            cursor.execute(create_theme_table)
            cursor.execute(create_stock_table)
            cursor.execute(create_limit_up_table)
            cursor.execute(create_daily_change_table)
            cursor.execute(create_daily_top30_table)
            cursor.execute(create_concept_table)
            cursor.execute(create_concept_daily_table)
            cursor.execute(create_jiuyang_theme_table)
            cursor.execute(create_jiuyang_stock_action_table)
            self.connection.commit()
            print("数据库表创建成功")
        except Exception as e:
            print(f"创建表失败: {e}")
        finally:
            cursor.close()
    
    def close(self):
        """
        关闭数据库连接
        """
        if self.connection:
            self.connection.close()
            print("数据库连接已关闭")
    
    def insert_theme(self, name):
        """
        插入题材
        """
        cursor = self.connection.cursor()
        try:
            cursor.execute("INSERT OR IGNORE INTO theme (name) VALUES (?)", (name,))
            self.connection.commit()
            cursor.execute("SELECT id FROM theme WHERE name = ?", (name,))
            theme_id = cursor.fetchone()[0]
            return theme_id
        finally:
            cursor.close()
    
    def insert_stock(self, code, name):
        """
        插入股票
        """
        cursor = self.connection.cursor()
        try:
            cursor.execute("INSERT OR IGNORE INTO stock (code, name) VALUES (?, ?)", (code, name))
            self.connection.commit()
            cursor.execute("SELECT id FROM stock WHERE code = ?", (code,))
            stock_id = cursor.fetchone()[0]
            return stock_id
        finally:
            cursor.close()
    
    def insert_limit_up(self, stock_id, theme_id, date, time=None, reason=None, board_count=1):
        """
        插入涨停记录
        """
        cursor = self.connection.cursor()
        try:
            cursor.execute(
                "INSERT OR IGNORE INTO limit_up (stock_id, theme_id, date, time, reason, board_count) VALUES (?, ?, ?, ?, ?, ?)",
                (stock_id, theme_id, date, time, reason, board_count)
            )
            self.connection.commit()
        finally:
            cursor.close()
    
    def get_limit_up_data(self, date=None, start_date=None, end_date=None, theme=None):
        """
        获取涨停数据，支持多种查询条件
        """
        cursor = self.connection.cursor()
        query = """
        SELECT t.name as theme, s.code, s.name as stock_name, l.date, l.time, l.reason, l.board_count, l.price, l.change_percent
        FROM limit_up l
        JOIN stock s ON l.stock_id = s.id
        JOIN theme t ON l.theme_id = t.id
        WHERE 1=1
        """
        params = []
        
        if date:
            query += " AND l.date = ?"
            params.append(date)
        
        if start_date:
            query += " AND l.date >= ?"
            params.append(start_date)
        
        if end_date:
            query += " AND l.date <= ?"
            params.append(end_date)
        
        if theme:
            query += " AND t.name = ?"
            params.append(theme)
        
        query += " ORDER BY l.date DESC, t.name, s.code"
        
        try:
            cursor.execute(query, params)
            results = [dict(row) for row in cursor.fetchall()]
            return results
        finally:
            cursor.close()
    
    def get_all_dates(self):
        """
        获取所有有数据的日期列表
        """
        cursor = self.connection.cursor()
        try:
            cursor.execute("SELECT DISTINCT date FROM limit_up ORDER BY date DESC")
            results = cursor.fetchall()
            return [row[0] for row in results]
        finally:
            cursor.close()
    
    def get_all_themes(self):
        """
        获取所有题材列表
        """
        cursor = self.connection.cursor()
        try:
            cursor.execute("SELECT * FROM theme ORDER BY name")
            results = [dict(row) for row in cursor.fetchall()]
            return results
        finally:
            cursor.close()
    
    def clear_all_data(self):
        """
        清空所有数据
        """
        cursor = self.connection.cursor()
        try:
            cursor.execute("DELETE FROM limit_up")
            cursor.execute("DELETE FROM stock")
            cursor.execute("DELETE FROM theme")
            self.connection.commit()
            print("数据清空成功")
            return True
        except Exception as e:
            print(f"清空数据失败: {e}")
            return False
        finally:
            cursor.close()
    
    def clear_data_by_date(self, date):
        """
        删除指定日期的涨停数据
        """
        cursor = self.connection.cursor()
        try:
            cursor.execute("DELETE FROM limit_up WHERE date = ?", (date,))
            deleted_count = cursor.rowcount
            self.connection.commit()
            print(f"已删除日期 {date} 的 {deleted_count} 条记录")
            return deleted_count
        except Exception as e:
            print(f"删除日期数据失败: {e}")
            return 0
        finally:
            cursor.close()
    
    def insert_daily_change(self, ts_code, symbol, name, industry, close, change, amount, turnover, date):
        """
        插入每日涨幅数据
        """
        cursor = self.connection.cursor()
        try:
            cursor.execute(
                "INSERT OR REPLACE INTO daily_change (ts_code, symbol, name, industry, close, change, amount, turnover, date) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (ts_code, symbol, name, industry, close, change, amount, turnover, date)
            )
            self.connection.commit()
        finally:
            cursor.close()
    
    def get_daily_change(self, ts_code, start_date, end_date):
        """
        获取指定股票在指定日期范围内的每日涨幅数据
        """
        cursor = self.connection.cursor()
        try:
            cursor.execute(
                "SELECT * FROM daily_change WHERE ts_code = ? AND date >= ? AND date <= ? ORDER BY date",
                (ts_code, start_date, end_date)
            )
            results = [dict(row) for row in cursor.fetchall()]
            return results
        finally:
            cursor.close()
    
    def insert_daily_top30(self, ts_code, symbol, name, industry, ten_day_change, daily_change, date, rank):
        """
        插入每日涨幅前30数据
        """
        cursor = self.connection.cursor()
        try:
            cursor.execute(
                "INSERT OR REPLACE INTO daily_top30 (ts_code, symbol, name, industry, ten_day_change, daily_change, date, rank) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (ts_code, symbol, name, industry, ten_day_change, daily_change, date, rank)
            )
            self.connection.commit()
        finally:
            cursor.close()
    
    def get_daily_top30(self, date):
        """
        获取指定日期的涨幅前30数据
        """
        cursor = self.connection.cursor()
        try:
            cursor.execute("SELECT * FROM daily_top30 WHERE date = ? ORDER BY rank", (date,))
            results = [dict(row) for row in cursor.fetchall()]
            return results
        finally:
            cursor.close()
    
    def get_top30_rank_change(self, current_date, previous_date):
        """
        获取排名变化
        """
        current_data = self.get_daily_top30(current_date)
        previous_data = self.get_daily_top30(previous_date)
        
        current_rank = {stock['ts_code']: stock['rank'] for stock in current_data}
        previous_rank = {stock['ts_code']: stock['rank'] for stock in previous_data}
        
        result = []
        for stock in current_data:
            ts_code = stock['ts_code']
            current_r = current_rank.get(ts_code, 999)
            previous_r = previous_rank.get(ts_code, 999)
            rank_change = previous_r - current_r if previous_r != 999 else 'NEW'
            
            result.append({
                **stock,
                'current_rank': current_r,
                'previous_rank': previous_r,
                'rank_change': rank_change
            })
        
        return result
    
    def insert_concept(self, concept_code, concept_name, concept_type=''):
        """
        插入板块
        """
        cursor = self.connection.cursor()
        try:
            cursor.execute(
                "INSERT OR IGNORE INTO concept (concept_code, concept_name, concept_type) VALUES (?, ?, ?)",
                (concept_code, concept_name, concept_type)
            )
            self.connection.commit()
            cursor.execute("SELECT id FROM concept WHERE concept_code = ?", (concept_code,))
            result = cursor.fetchone()
            return result[0] if result else None
        finally:
            cursor.close()
    
    def insert_concept_daily(self, concept_code, date, close, change_pct, volume=None, amount=None):
        """
        插入板块每日涨幅数据
        """
        cursor = self.connection.cursor()
        try:
            cursor.execute(
                "INSERT OR REPLACE INTO concept_daily (concept_code, date, close, change_pct, volume, amount) VALUES (?, ?, ?, ?, ?, ?)",
                (concept_code, date, close, change_pct, volume, amount)
            )
            self.connection.commit()
        finally:
            cursor.close()
    
    def get_concept_daily(self, start_date, end_date):
        """
        获取指定日期范围内的板块数据
        """
        cursor = self.connection.cursor()
        try:
            # 确保 start_date <= end_date
            if start_date > end_date:
                start_date, end_date = end_date, start_date
            
            cursor.execute(
                """
                SELECT cd.concept_code, c.concept_name, c.concept_type, cd.date, cd.close, cd.change_pct, cd.volume
                FROM concept_daily cd
                JOIN concept c ON cd.concept_code = c.concept_code
                WHERE cd.date BETWEEN ? AND ?
                ORDER BY cd.date, cd.change_pct DESC
                """,
                (start_date, end_date)
            )
            results = []
            for row in cursor.fetchall():
                results.append({
                    'concept_code': row[0],
                    'concept_name': row[1],
                    'concept_type': row[2],
                    'date': row[3],
                    'close': row[4],
                    'change_pct': row[5],
                    'volume': row[6]
                })
            return results
        finally:
            cursor.close()
    
    def get_concept_dates(self):
        """
        获取所有有数据的日期列表
        """
        cursor = self.connection.cursor()
        try:
            cursor.execute("SELECT DISTINCT date FROM concept_daily ORDER BY date DESC")
            results = cursor.fetchall()
            return [row[0] for row in results]
        finally:
            cursor.close()
    
    def get_all_concepts(self):
        """
        获取所有板块列表
        """
        cursor = self.connection.cursor()
        try:
            cursor.execute("SELECT * FROM concept ORDER BY concept_code")
            results = [dict(row) for row in cursor.fetchall()]
            return results
        finally:
            cursor.close()
    
    def insert_jiuyang_theme(self, title, date):
        """
        插入韭研公社题材
        """
        cursor = self.connection.cursor()
        try:
            cursor.execute(
                "INSERT OR IGNORE INTO jiuyang_theme (title, date) VALUES (?, ?)",
                (title, date)
            )
            self.connection.commit()
            cursor.execute("SELECT id FROM jiuyang_theme WHERE title = ? AND date = ?", (title, date))
            result = cursor.fetchone()
            return result[0] if result else None
        finally:
            cursor.close()
    
    def insert_jiuyang_stock_action(self, theme_id, code, name, article_id, title, expound, 
                                     action_time, price, shares_range, create_time, update_time, 
                                     sort_no, comment_count, like_count, forward_count, step_count,
                                     is_like, is_step, is_crawl, is_recommend, is_delete,
                                     user_id, user_nickname, user_avatar, date, num=None):
        """
        插入韭研公社股票异动
        """
        cursor = self.connection.cursor()
        try:
            cursor.execute(
                "INSERT OR REPLACE INTO jiuyang_stock_action " +
                "(theme_id, code, name, article_id, title, expound, action_time, price, shares_range, " +
                "create_time, update_time, sort_no, comment_count, like_count, forward_count, step_count, " +
                "is_like, is_step, is_crawl, is_recommend, is_delete, user_id, user_nickname, user_avatar, date, num) " +
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (theme_id, code, name, article_id, title, expound, action_time, price, shares_range,
                 create_time, update_time, sort_no, comment_count, like_count, forward_count, step_count,
                 is_like, is_step, is_crawl, is_recommend, is_delete, user_id, user_nickname, user_avatar, date, num)
            )
            self.connection.commit()
        finally:
            cursor.close()
    
    def get_jiuyang_data_by_date(self, date):
        """
        获取指定日期的韭研公社数据
        """
        cursor = self.connection.cursor()
        try:
            cursor.execute("SELECT * FROM jiuyang_theme WHERE date = ? ORDER BY id", (date,))
            themes = [dict(row) for row in cursor.fetchall()]
            
            result = []
            for theme in themes:
                cursor.execute(
                    "SELECT * FROM jiuyang_stock_action WHERE theme_id = ? AND date = ? ORDER BY sort_no",
                    (theme['id'], date)
                )
                stocks = [dict(row) for row in cursor.fetchall()]
                result.append({
                    'theme': theme,
                    'stocks': stocks
                })
            
            return result
        finally:
            cursor.close()
    
    def get_jiuyang_dates(self, limit=20):
        """
        获取韭研公社所有有数据的日期（只返回有股票数据的日期）
        limit: 返回的日期数量，默认20个
        """
        cursor = self.connection.cursor()
        try:
            cursor.execute("""
                SELECT DISTINCT t.date 
                FROM jiuyang_theme t
                INNER JOIN jiuyang_stock_action s ON t.id = s.theme_id
                ORDER BY t.date DESC
                LIMIT ?
            """, (limit,))
            results = cursor.fetchall()
            return [row[0] for row in results]
        finally:
            cursor.close()
    
    def clear_jiuyang_data_by_date(self, date):
        """
        删除指定日期的韭研公社数据
        """
        cursor = self.connection.cursor()
        try:
            cursor.execute("DELETE FROM jiuyang_stock_action WHERE date = ?", (date,))
            cursor.execute("DELETE FROM jiuyang_theme WHERE date = ?", (date,))
            self.connection.commit()
            print(f"已删除日期 {date} 的韭研公社数据")
        except Exception as e:
            print(f"删除韭研公社数据失败: {e}")
        finally:
            cursor.close()
