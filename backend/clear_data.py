import sys
import os
from datetime import date, datetime, timedelta

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.database import Database

def clear_old_data():
    """
    清空数据库中的旧数据
    """
    print("=== 清空数据库中的旧数据 ===")
    
    db = Database()
    db.connect()
    
    # 清空daily_top30表
    cursor = db.connection.cursor()
    cursor.execute("DELETE FROM daily_top30")
    db.connection.commit()
    
    # 清空daily_change表
    cursor.execute("DELETE FROM daily_change")
    db.connection.commit()
    
    # 检查清空后的数据
    cursor.execute("SELECT COUNT(*) FROM daily_top30")
    top30_count = cursor.fetchone()[0]
    print(f"清空后，daily_top30表中还有 {top30_count} 条数据")
    
    cursor.execute("SELECT COUNT(*) FROM daily_change")
    change_count = cursor.fetchone()[0]
    print(f"清空后，daily_change表中还有 {change_count} 条数据")
    
    db.close()
    
    print("\n=== 清空完成 ===")

if __name__ == "__main__":
    clear_old_data()
