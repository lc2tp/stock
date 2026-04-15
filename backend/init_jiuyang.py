import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.database import Database
from services.jiuyang_service import fetch_recent_jiuyang_data

def init_database():
    print("=" * 50)
    print("初始化数据库...")
    print("=" * 50)
    
    db = Database()
    if not db.connect():
        print("数据库连接失败！")
        return False
    
    try:
        db.create_tables()
        print("数据库表创建成功！")
        return True
    except Exception as e:
        print(f"初始化失败: {e}")
        return False
    finally:
        db.close()

def main():
    print("\n" + "=" * 50)
    print("韭研公社数据初始化")
    print("=" * 50 + "\n")
    
    if not init_database():
        return
    
    print("\n" + "=" * 50)
    print("获取近10个交易日的数据...")
    print("=" * 50 + "\n")
    
    fetch_recent_jiuyang_data(10)
    
    print("\n" + "=" * 50)
    print("初始化完成！")
    print("=" * 50 + "\n")

if __name__ == "__main__":
    main()
