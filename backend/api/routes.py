from fastapi import APIRouter, UploadFile, File, Form, Query
from services.ocr_service import OCRService
from services.excel_service import ExcelService
from services.tushare_service import TushareService
from models.database import Database
from datetime import date, timedelta
import os
import uuid
import sys

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

router = APIRouter()

ocr_service = OCRService()
excel_service = ExcelService()

_tushare_service = None

def get_tushare_service():
    global _tushare_service
    if _tushare_service is None:
        try:
            _tushare_service = TushareService()
            # 避免模块级别的 get_stock_basic_data() 可能有风险，注释掉或改成可选
        except Exception as e:
            print(f"初始化 TushareService 失败: {e}")
            raise
    return _tushare_service

@router.post("/api/ocr/upload")
async def upload_image(file: UploadFile = File(...), record_date: str = Form(None)):
    ext = os.path.splitext(file.filename)[1] if file.filename else '.jpg'
    image_path = f"temp_{uuid.uuid4().hex}{ext}"
    with open(image_path, "wb") as buffer:
        buffer.write(await file.read())
    
    try:
        result = ocr_service.process_image(image_path)
        
        import json
        try:
            print(f"OCR结果: {json.dumps(result, ensure_ascii=False)}")
            if 'raw_text' in result:
                print(f"原始识别文本前500字符: {result['raw_text'][:500]}")
        except Exception as e:
            print(f"OCR结果打印失败: {e}")
            print(f"OCR结果(原始): {result}")
        
        if 'error' in result:
            return {"success": False, "message": result['error']}
        
        if not result.get('data') or len(result.get('data', {})) == 0:
            return {
                "success": True, 
                "message": "图片已上传，但未能识别出股票数据",
                "raw_data": {},
                "raw_text": result.get('raw_text', '')[:1000],
                "debug_info": "OCR识别结果为空"
            }
        
        if result.get('date'):
            today = date.fromisoformat(result['date'])
        elif record_date:
            today = date.fromisoformat(record_date)
        else:
            today = date.today()
        
        db = Database()
        db.connect()
        
        db.clear_data_by_date(today)
        
        total_stocks = 0
        imported_themes = []
        
        try:
            for theme_name, stocks in result['data'].items():
                if not stocks:
                    continue
                
                theme_id = db.insert_theme(theme_name)
                imported_themes.append(theme_name)
                
                for stock_info in stocks:
                    code = stock_info['code']
                    name = stock_info['name']
                    board_count = stock_info.get('board_count', 1)
                    reason = stock_info.get('reason')
                    
                    stock_id = db.insert_stock(code, name)
                    
                    time = stock_info.get('time')
                    db.insert_limit_up(stock_id, theme_id, today, time=time, reason=reason, board_count=board_count)
                    total_stocks += 1
            
            return {
                "success": True, 
                "message": f"导入成功！共导入 {len(imported_themes)} 个题材，{total_stocks} 只股票",
                "themes": imported_themes,
                "total_stocks": total_stocks,
                "raw_data": result['data']
            }
        finally:
            db.close()
    
    except Exception as e:
        return {"success": False, "message": f"导入失败: {str(e)}"}
    
    finally:
        if os.path.exists(image_path):
            os.remove(image_path)

@router.post("/api/excel/upload")
async def upload_excel(file: UploadFile = File(...), record_date: str = Form(None)):
    ext = os.path.splitext(file.filename)[1] if file.filename else '.xlsx'
    excel_path = f"temp_{uuid.uuid4().hex}{ext}"
    with open(excel_path, "wb") as buffer:
        buffer.write(await file.read())
    
    try:
        result = excel_service.process_excel(excel_path)
        
        import json
        try:
            print(f"Excel结果: {json.dumps(result, ensure_ascii=False)}")
        except Exception as e:
            print(f"Excel结果打印失败: {e}")
            print(f"Excel结果(原始): {result}")
        
        if 'error' in result:
            return {"success": False, "message": result['error']}
        
        if not result.get('data') or len(result.get('data', {})) == 0:
            return {
                "success": True, 
                "message": "Excel已上传，但未能识别出股票数据",
                "raw_data": {}
            }
        
        if result.get('date'):
            today = date.fromisoformat(result['date'])
        elif record_date:
            today = date.fromisoformat(record_date)
        else:
            today = date.today()
        
        db = Database()
        db.connect()
        
        db.clear_data_by_date(today)
        
        total_stocks = 0
        imported_themes = []
        
        try:
            for theme_name, stocks in result['data'].items():
                if not stocks:
                    continue
                
                theme_id = db.insert_theme(theme_name)
                imported_themes.append(theme_name)
                
                for stock_info in stocks:
                    code = stock_info['code']
                    name = stock_info['name']
                    board_count = stock_info.get('board_count', 1)
                    reason = stock_info.get('reason')
                    
                    stock_id = db.insert_stock(code, name)
                    
                    time = stock_info.get('time')
                    db.insert_limit_up(stock_id, theme_id, today, time=time, reason=reason, board_count=board_count)
                    total_stocks += 1
            
            return {
                "success": True, 
                "message": f"导入成功！共导入 {len(imported_themes)} 个题材，{total_stocks} 只股票",
                "themes": imported_themes,
                "total_stocks": total_stocks,
                "raw_data": result['data']
            }
        finally:
            db.close()
    
    except Exception as e:
        return {"success": False, "message": f"导入失败: {str(e)}"}
    
    finally:
        if os.path.exists(excel_path):
            os.remove(excel_path)

@router.post("/api/ocr/test")
async def test_ocr(file: UploadFile = File(...)):
    ext = os.path.splitext(file.filename)[1] if file.filename else '.jpg'
    image_path = f"temp_test_{uuid.uuid4().hex}{ext}"
    with open(image_path, "wb") as buffer:
        buffer.write(await file.read())
    
    try:
        result = ocr_service.process_image(image_path)
        return result
    finally:
        if os.path.exists(image_path):
            os.remove(image_path)

@router.get("/api/limit-up")
def get_limit_up(
    date: str = None,
    start_date: str = None,
    end_date: str = None,
    theme: str = None
):
    db = Database()
    db.connect()
    
    try:
        results = db.get_limit_up_data(date=date, start_date=start_date, end_date=end_date, theme=theme)
        
        grouped_data = {}
        for item in results:
            theme_name = item["theme"]
            if theme_name not in grouped_data:
                grouped_data[theme_name] = []
            grouped_data[theme_name].append({
                "code": item["code"],
                "name": item["stock_name"],
                "date": str(item["date"]),
                "time": item["time"],
                "reason": item["reason"],
                "board_count": item["board_count"],
                "price": item["price"],
                "change_percent": item["change_percent"]
            })
        
        return {"success": True, "data": grouped_data, "count": len(results)}
    except Exception as e:
        return {"success": False, "message": f"获取数据失败: {str(e)}"}
    finally:
        db.close()

@router.get("/api/dates")
def get_all_dates():
    db = Database()
    db.connect()
    
    try:
        dates = db.get_all_dates()
        return {"success": True, "dates": dates}
    except Exception as e:
        return {"success": False, "message": f"获取日期列表失败: {str(e)}"}
    finally:
        db.close()

@router.get("/api/stats/summary")
def get_stats_summary(days: int = Query(30, ge=1, le=365)):
    db = Database()
    db.connect()
    
    try:
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        results = db.get_limit_up_data(start_date=start_date.isoformat(), end_date=end_date.isoformat())
        
        theme_stats = {}
        date_stats = {}
        date_theme_stats = {}
        
        for item in results:
            theme = item["theme"]
            record_date = str(item["date"])
            
            if theme not in theme_stats:
                theme_stats[theme] = {"count": 0, "dates": set()}
            theme_stats[theme]["count"] += 1
            theme_stats[theme]["dates"].add(record_date)
            
            if record_date not in date_stats:
                date_stats[record_date] = {"themes": set(), "stocks": 0}
            date_stats[record_date]["themes"].add(theme)
            date_stats[record_date]["stocks"] += 1
            
            if record_date not in date_theme_stats:
                date_theme_stats[record_date] = {}
            if theme not in date_theme_stats[record_date]:
                date_theme_stats[record_date][theme] = 0
            date_theme_stats[record_date][theme] += 1
        
        theme_list = [
            {
                "theme": theme,
                "count": stats["count"],
                "active_days": len(stats["dates"])
            }
            for theme, stats in theme_stats.items()
        ]
        theme_list.sort(key=lambda x: x["count"], reverse=True)
        
        return {
            "success": True,
            "data": {
                "total_themes": len(theme_stats),
                "total_stocks": len(results),
                "total_days": len(date_stats),
                "avg_stocks_per_day": round(len(results) / max(len(date_stats), 1), 1),
                "theme_ranking": theme_list[:20],
                "date_stats": {
                    "dates": sorted(date_stats.keys()),
                    "total_stocks": [date_stats[d]["stocks"] for d in sorted(date_stats.keys())],
                    "total_themes": [len(date_stats[d]["themes"]) for d in sorted(date_stats.keys())]
                },
                "date_theme_stats": date_theme_stats
            }
        }
    except Exception as e:
        return {"success": False, "message": f"获取统计失败: {str(e)}"}
    finally:
        db.close()

@router.get("/api/stats/trend")
def get_trend_analysis(days: int = Query(30, ge=2, le=365)):
    db = Database()
    db.connect()
    
    try:
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        results = db.get_limit_up_data(start_date=start_date.isoformat(), end_date=end_date.isoformat())
        
        date_theme_stats = {}
        all_themes = set()
        
        for item in results:
            theme = item["theme"]
            record_date = str(item["date"])
            all_themes.add(theme)
            
            if record_date not in date_theme_stats:
                date_theme_stats[record_date] = {}
            if theme not in date_theme_stats[record_date]:
                date_theme_stats[record_date][theme] = 0
            date_theme_stats[record_date][theme] += 1
        
        dates = []
        current_date = start_date
        while current_date <= end_date:
            dates.append(current_date.isoformat())
            current_date += timedelta(days=1)
        
        trends = {
            "up": [],
            "down": [],
            "new": [],
            "disappear": []
        }
        
        for theme in all_themes:
            recent_dates = sorted(dates)[-2:]
            if len(recent_dates) < 2:
                continue
            
            current_count = date_theme_stats.get(recent_dates[-1], {}).get(theme, 0)
            previous_count = date_theme_stats.get(recent_dates[-2], {}).get(theme, 0)
            
            if current_count > previous_count:
                trends["up"].append({
                    "theme": theme,
                    "current": current_count,
                    "previous": previous_count,
                    "change": current_count - previous_count
                })
            elif current_count < previous_count:
                trends["down"].append({
                    "theme": theme,
                    "current": current_count,
                    "previous": previous_count,
                    "change": previous_count - current_count
                })
            elif current_count > 0 and previous_count == 0:
                trends["new"].append({
                    "theme": theme,
                    "current": current_count
                })
        
        for theme in all_themes:
            recent_dates = sorted(dates)[-2:]
            if len(recent_dates) < 2:
                continue
            
            current_count = date_theme_stats.get(recent_dates[-1], {}).get(theme, 0)
            previous_count = date_theme_stats.get(recent_dates[-2], {}).get(theme, 0)
            
            if current_count == 0 and previous_count > 0:
                trends["disappear"].append({
                    "theme": theme,
                    "previous": previous_count
                })
        
        trends["up"].sort(key=lambda x: x["change"], reverse=True)
        trends["down"].sort(key=lambda x: x["change"], reverse=True)
        trends["new"].sort(key=lambda x: x["current"], reverse=True)
        
        return {
            "success": True,
            "data": {
                "dates": dates,
                "date_theme_stats": date_theme_stats,
                "trends": trends
            }
        }
    except Exception as e:
        return {"success": False, "message": f"获取趋势分析失败: {str(e)}"}
    finally:
        db.close()

@router.get("/api/tushare/top30")
def get_tushare_top30(date: str = None):
    try:
        if not date:
            date = date.today().strftime('%Y%m%d')
        
        db = Database()
        db.connect()
        
        try:
            db_data = db.get_daily_top30(date)
            
            if db_data:
                stocks = []
                for item in db_data:
                    stocks.append({
                        'ts_code': item['ts_code'],
                        'symbol': item['symbol'],
                        'name': item['name'],
                        'industry': item['industry'],
                        'ten_day_change': item['ten_day_change'],
                        'daily_change': item['daily_change']
                    })
                return {"success": True, "data": stocks, "date": date}
            
            stocks = get_tushare_service().get_top_30_stocks(date)
            
            for i, stock in enumerate(stocks):
                db.insert_daily_top30(
                    ts_code=stock['ts_code'],
                    symbol=stock['symbol'],
                    name=stock['name'],
                    industry=stock['industry'],
                    ten_day_change=stock['ten_day_change'],
                    daily_change=stock['daily_change'],
                    date=date,
                    rank=i+1
                )
        finally:
            db.close()
        
        return {"success": True, "data": stocks, "date": date}
    except Exception as e:
        return {"success": False, "message": f"获取数据失败: {str(e)}"}

@router.get("/api/tushare/rank-change")
def get_rank_change(current_date: str = None, previous_date: str = None):
    try:
        if not current_date:
            current_date = date.today().strftime('%Y%m%d')
        if not previous_date:
            previous_date = (date.today() - timedelta(days=1)).strftime('%Y%m%d')
        
        # 直接调用calculate_ten_day_top30计算数据，确保与ten-day-top30接口数据一致
        current_top30 = get_tushare_service().calculate_ten_day_top30(current_date)
        previous_top30 = get_tushare_service().calculate_ten_day_top30(previous_date)
        
        # 计算排名变化
        current_rank = {stock['ts_code']: i+1 for i, stock in enumerate(current_top30)}
        previous_rank = {stock['ts_code']: i+1 for i, stock in enumerate(previous_top30)}
        
        rank_change = []
        for stock in current_top30:
            ts_code = stock['ts_code']
            current_r = current_rank.get(ts_code, 999)
            previous_r = previous_rank.get(ts_code, 999)
            rank_change_value = previous_r - current_r if previous_r != 999 else 'NEW'
            
            rank_change.append({
                **stock,
                'current_rank': current_r,
                'previous_rank': previous_r,
                'rank_change': rank_change_value
            })
        
        return {"success": True, "data": rank_change, "current_date": current_date, "previous_date": previous_date}
    except Exception as e:
        return {"success": False, "message": f"获取排名变化失败: {str(e)}"}

@router.get("/api/tushare/ten-day-top30")
def get_ten_day_top30(target_date: str = None, days: int = Query(10, ge=2, le=10)):
    try:
        if not target_date:
            today = date.today()
            target_date = today.strftime('%Y%m%d')
        
        stocks = get_tushare_service().calculate_top30(target_date, days=days)
        
        return {"success": True, "data": stocks, "date": target_date, "days": days}
    except Exception as e:
        return {"success": False, "message": f"获取数据失败: {str(e)}"}

@router.get("/api/tushare/get-historical-data")
def get_historical_data_api(date: str):
    try:
        from get_historical_data import get_daily_data
        get_daily_data(date)
        return {"success": True, "message": f"{date} 数据获取成功"}
    except Exception as e:
        return {"success": False, "message": f"数据获取失败: {str(e)}"}

@router.get("/api/concept/refresh")
def refresh_concept_data():
    try:
        from datetime import date
        today = date.today()
        
        return {"success": True, "message": "数据已存在，无需刷新"}
    except Exception as e:
        return {"success": False, "message": f"同步失败: {str(e)}"}

@router.get("/api/concept/data")
def get_concept_data(days: int = Query(10, ge=2, le=10)):
    try:
        db = Database()
        db.connect()
        db.create_tables()
        
        try:
            concept_dates = db.get_concept_dates()  # 返回格式: '20260410'
            
            if len(concept_dates) < 2:
                return {"success": False, "message": f"数据不足，当前只有 {len(concept_dates)} 天数据"}
            
            # 实际使用的天数取最小的可用天数和请求天数
            actual_days = min(days, len(concept_dates))
            selected_dates = concept_dates[:actual_days]  # 保持 '20260410' 格式，降序（最新在前）
            
            # 排序用于查询日期范围
            sorted_dates = sorted(selected_dates)
            start_date = sorted_dates[0]
            end_date = sorted_dates[-1]
            
            all_data = db.get_concept_daily(start_date, end_date)
            
            concept_data = {}
            for item in all_data:
                code = item['concept_code']
                if code not in concept_data:
                    concept_data[code] = {
                        'concept_code': code,
                        'concept_name': item['concept_name'],
                        'concept_type': item.get('concept_type', ''),
                        'daily_change': {},
                        'daily_volume': {}
                    }
                concept_data[code]['daily_change'][item['date']] = item['change_pct']
                concept_data[code]['daily_volume'][item['date']] = item.get('volume', 0.0)
            
            result = []
            for code, data in concept_data.items():
                # 只统计概念指数和行业指数
                concept_type = data.get('concept_type', '')
                if not ('概念' in concept_type or '行业' in concept_type):
                    continue
                
                cumulative_change = 1.0
                valid_days = 0
                
                for d in sorted_dates:
                    if d in data['daily_change']:
                        change_pct = data['daily_change'][d]
                        cumulative_change *= (1 + change_pct / 100)
                        valid_days += 1
                
                # 只要有1天以上数据就算有效
                if valid_days >= 1:
                    cumulative_change_pct = (cumulative_change - 1) * 100
                    
                    # 获取今日涨幅和成交额
                    today_change = 0.0
                    today_volume = 0.0
                    
                    # 1. today_change：用最新日期的change
                    if concept_dates and concept_dates[0] in data['daily_change']:
                        today_change = data['daily_change'][concept_dates[0]]
                    
                    # 2. today_volume：优先用最新日期的volume，没有就找最近的
                    if concept_dates:
                        for d in concept_dates:
                            if d in data['daily_volume'] and data['daily_volume'][d] is not None:
                                today_volume = data['daily_volume'][d]
                                break
                    
                    # 确保永远不是 None
                    if today_volume is None:
                        today_volume = 0.0
                    
                    result.append({
                        'concept_code': code,
                        'concept_name': data['concept_name'],
                        'concept_type': data.get('concept_type', ''),
                        'cumulative_change': cumulative_change_pct,
                        'today_change': today_change,
                        'today_volume': today_volume
                    })
            
            result.sort(key=lambda x: x['cumulative_change'], reverse=True)
            
            return {"success": True, "data": result, "days": actual_days}
        finally:
            db.close()
    except Exception as e:
        return {"success": False, "message": f"获取数据失败: {str(e)}"}

@router.get("/api/concept/dates")
def get_concept_dates():
    try:
        db = Database()
        db.connect()
        
        try:
            dates = db.get_concept_dates()
            # 将日期格式从 'YYYYMMDD' 转换为 'YYYY-MM-DD'
            formatted_dates = []
            for d in dates:
                if len(d) == 8:
                    formatted_dates.append(f"{d[:4]}-{d[4:6]}-{d[6:8]}")
                else:
                    formatted_dates.append(d)
            return {"success": True, "dates": formatted_dates}
        finally:
            db.close()
    except Exception as e:
        return {"success": False, "message": f"获取日期失败: {str(e)}"}

@router.get("/api/concept/analysis")
def get_concept_analysis(days: int = Query(10, ge=1, le=10)):
    """
    获取板块分析数据：
    - 获得指定天数涨幅前10的板块
    - 返回这些板块近10日的每日数据
    """
    try:
        db = Database()
        db.connect()
        db.create_tables()
        
        try:
            concept_dates = db.get_concept_dates()
            
            if len(concept_dates) < 2:
                return {"success": False, "message": f"数据不足，当前只有 {len(concept_dates)} 天数据"}
            
            # 先获取用于计算涨幅的日期范围
            rank_days = min(days, len(concept_dates))
            rank_selected_dates = concept_dates[:rank_days]
            rank_selected_dates.sort()
            
            # 获取近10日的所有日期（用于折线图横轴）
            chart_days = min(10, len(concept_dates))
            chart_selected_dates = concept_dates[:chart_days]
            chart_selected_dates.sort()
            
            # 获取所有板块在近10日的每日数据
            all_data = db.get_concept_daily(chart_selected_dates[0], chart_selected_dates[-1])
            
            concept_data = {}
            for item in all_data:
                code = item['concept_code']
                if code not in concept_data:
                    concept_data[code] = {
                        'concept_code': code,
                        'concept_name': item['concept_name'],
                        'concept_type': item.get('concept_type', ''),
                        'daily_data': {}
                    }
                concept_data[code]['daily_data'][item['date']] = item['change_pct']
            
            # 计算每个板块在指定天数内的累计涨幅
            result = []
            for code, data in concept_data.items():
                # 只统计概念指数和行业指数
                concept_type = data.get('concept_type', '')
                if not ('概念' in concept_type or '行业' in concept_type):
                    continue
                
                # 计算指定天数内的累计涨幅
                cumulative_change = 1.0
                valid_days = 0
                
                for d in rank_selected_dates:
                    if d in data['daily_data']:
                        change_pct = data['daily_data'][d]
                        cumulative_change *= (1 + change_pct / 100)
                        valid_days += 1
                
                if valid_days >= 1:
                    cumulative_change_pct = (cumulative_change - 1) * 100
                    
                    # 收集近10日的每日数据
                    daily_changes = []
                    for d in chart_selected_dates:
                        daily_changes.append({
                            'date': d,
                            'change_pct': data['daily_data'].get(d, 0.0)
                        })
                    
                    result.append({
                        'concept_code': code,
                        'concept_name': data['concept_name'],
                        'concept_type': data.get('concept_type', ''),
                        'cumulative_change': cumulative_change_pct,
                        'daily_changes': daily_changes
                    })
            
            # 按累计涨幅排序，取前30
            result.sort(key=lambda x: x['cumulative_change'], reverse=True)
            top10_concepts = result[:30]
            
            return {
                "success": True, 
                "data": top10_concepts, 
                "days": rank_days,
                "chart_dates": chart_selected_dates
            }
        finally:
            db.close()
    except Exception as e:
        return {"success": False, "message": f"获取数据失败: {str(e)}"}


@router.get("/api/concept/sync-historical")
def sync_historical_concept_data():
    try:
        from get_concept_data import fetch_and_save_concept_data
        
        start_date = '2026-04-01'
        end_date = '2026-04-10'
        
        fetch_and_save_concept_data(start_date, end_date, use_mock=True)
        
        return {"success": True, "message": "历史板块数据同步成功"}
    except Exception as e:
        return {"success": False, "message": f"同步失败: {str(e)}"}


@router.get("/api/jiuyang/dates")
def get_jiuyang_dates():
    try:
        db = Database()
        if not db.connect():
            return {"success": False, "message": "数据库连接失败"}
        
        try:
            dates = db.get_jiuyang_dates()
            return {"success": True, "data": dates}
        finally:
            db.close()
    except Exception as e:
        return {"success": False, "message": f"获取日期列表失败: {str(e)}"}


@router.get("/api/jiuyang/data")
def get_jiuyang_data(date: str = Query(None)):
    try:
        db = Database()
        if not db.connect():
            return {"success": False, "message": "数据库连接失败"}
        
        try:
            if not date:
                dates = db.get_jiuyang_dates()
                if dates:
                    # 找第一个有完整数据（有股票）的日期
                    for candidate_date in dates:
                        data = db.get_jiuyang_data_by_date(candidate_date)
                        total_stocks = sum(len(item['stocks']) for item in data)
                        if total_stocks > 0:
                            date = candidate_date
                            break
                    else:
                        # 如果所有日期都没数据，用第一个
                        date = dates[0]
                else:
                    return {"success": True, "data": [], "date": None}
            
            data = db.get_jiuyang_data_by_date(date)
            return {"success": True, "data": data, "date": date}
        finally:
            db.close()
    except Exception as e:
        return {"success": False, "message": f"获取数据失败: {str(e)}"}


@router.get("/api/jiuyang/refresh")
def refresh_jiuyang_data(date: str = Query(None)):
    try:
        from services.jiuyang_service import fetch_and_save_jiuyang_data
        
        if not date:
            from datetime import datetime
            date = datetime.now().strftime("%Y-%m-%d")
        
        success = fetch_and_save_jiuyang_data(date)
        
        if success:
            return {"success": True, "message": f"{date} 数据刷新成功"}
        else:
            return {"success": False, "message": f"{date} 数据刷新失败"}
    except Exception as e:
        return {"success": False, "message": f"刷新失败: {str(e)}"}


@router.get("/api/jiuyang/theme-change")
def get_jiuyang_theme_change():
    try:
        db = Database()
        if not db.connect():
            return {"success": False, "message": "数据库连接失败"}
        
        try:
            dates = db.get_jiuyang_dates()
            if not dates or len(dates) < 2:
                return {"success": True, "data": [], "dates": dates}
            
            # 取近10个交易日
            selected_dates = dates[:10]
            selected_dates.reverse()
            
            # 获取所有题材的历史数据
            all_themes = {}
            
            for date in selected_dates:
                data = db.get_jiuyang_data_by_date(date)
                for theme in data:
                    theme_title = theme.get('theme', {}).get('title', '')
                    if not theme_title:
                        continue
                    
                    if theme_title not in all_themes:
                        all_themes[theme_title] = {
                            'theme': theme_title,
                            'history': [0] * len(selected_dates),
                            'history_with_zhaban': [0] * len(selected_dates),
                            'zhaban_history': [0] * len(selected_dates)
                        }
                    
                    date_idx = selected_dates.index(date)
                    stocks = theme.get('stocks', [])
                    # 统计真正涨停的（有 action_time）和炸板的（无 action_time）
                    real_limit_up = 0
                    zhaban_count = 0
                    for stock in stocks:
                        if stock.get('action_time'):
                            real_limit_up += 1
                        else:
                            zhaban_count += 1
                    
                    all_themes[theme_title]['history'][date_idx] = real_limit_up
                    all_themes[theme_title]['history_with_zhaban'][date_idx] = len(stocks)
                    all_themes[theme_title]['zhaban_history'][date_idx] = zhaban_count
            
            # 转换为列表并按最后一天涨停数排序
            result = list(all_themes.values())
            result.sort(key=lambda x: x['history'][-1] if x['history'] else 0, reverse=True)
            
            # 标记消失的题材（用真正的涨停数判断）
            for item in result:
                if len(item['history']) >= 2:
                    yesterday_count = item['history'][-2] if len(item['history']) >= 2 else 0
                    today_count = item['history'][-1]
                    item['disappeared'] = (yesterday_count > 0 and today_count == 0)
            
            return {"success": True, "data": result, "dates": selected_dates}
        finally:
            db.close()
    except Exception as e:
        return {"success": False, "message": f"获取数据失败: {str(e)}"}


@router.get("/api/jiuyang/stock-theme")
def search_stock_theme(keyword: str):
    try:
        db = Database()
        if not db.connect():
            return {"success": False, "message": "数据库连接失败"}
        
        try:
            cursor = db.connection.cursor()
            try:
                # 搜索匹配的股票（模糊查询）
                cursor.execute("""
                    SELECT DISTINCT s.code, s.name
                    FROM jiuyang_stock_action s
                    WHERE s.code LIKE ? OR s.name LIKE ?
                    ORDER BY s.date DESC
                    LIMIT 50
                """, (f'%{keyword}%', f'%{keyword}%'))
                
                stocks = cursor.fetchall()
                
                if not stocks:
                    return {"success": True, "data": []}
                
                results = []
                for stock in stocks:
                    stock_code = stock[0]
                    stock_name = stock[1]
                    
                    # 查询这只股票出现在哪些题材里
                    cursor.execute("""
                        SELECT DISTINCT t.date, t.title
                        FROM jiuyang_theme t
                        INNER JOIN jiuyang_stock_action s ON t.id = s.theme_id
                        WHERE s.code = ?
                        ORDER BY t.date DESC
                    """, (stock_code,))
                    
                    theme_list = cursor.fetchall()
                    
                    results.append({
                        'code': stock_code,
                        'name': stock_name,
                        'themes': [{'date': item[0], 'title': item[1]} for item in theme_list]
                    })
                
                return {"success": True, "data": results}
            finally:
                cursor.close()
        finally:
            db.close()
    except Exception as e:
        return {"success": False, "message": f"查询失败: {str(e)}"}


@router.get("/api/capital-flow/dates")
def get_capital_flow_dates():
    """
    获取资金流向日期列表
    """
    try:
        from models.database import Database
        db = Database()
        if not db.connect():
            return {"success": False, "message": "数据库连接失败"}
        
        try:
            dates = db.get_concept_capital_flow_dates()
            return {"success": True, "data": dates}
        finally:
            db.close()
    except Exception as e:
        return {"success": False, "message": f"获取日期列表失败: {str(e)}"}


@router.get("/api/capital-flow/types")
def get_capital_flow_types():
    """
    获取板块类型列表
    """
    try:
        from models.database import Database
        db = Database()
        if not db.connect():
            return {"success": False, "message": "数据库连接失败"}
        
        try:
            types = db.get_concept_capital_flow_types()
            return {"success": True, "data": types}
        finally:
            db.close()
    except Exception as e:
        return {"success": False, "message": f"获取类型列表失败: {str(e)}"}


@router.get("/api/capital-flow/consecutive")
def get_consecutive_capital_flow(days: int = 2, flow_type: str = 'inflow', concept_type: str = None):
    """
    获取连续N日资金流入/流出的板块
    days: 连续天数（2-6）
    flow_type: 'inflow' 连续流入，'outflow' 连续流出
    concept_type: 板块类型筛选
    """
    try:
        from services.capital_flow_service import calculate_consecutive_capital_flow
        
        if days < 2 or days > 6:
            return {"success": False, "message": "天数必须在2-6之间"}
        
        if flow_type not in ['inflow', 'outflow']:
            return {"success": False, "message": "flow_type必须是inflow或outflow"}
        
        data = calculate_consecutive_capital_flow(days, flow_type, concept_type)
        return {"success": True, "data": data}
    except Exception as e:
        return {"success": False, "message": f"查询失败: {str(e)}"}


@router.get("/api/capital-flow/refresh")
def refresh_capital_flow(date: str = Query(None)):
    """
    刷新资金流向数据
    """
    try:
        from services.capital_flow_service import fetch_and_save_concept_capital_flow
        from datetime import datetime
        
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")
        
        success = fetch_and_save_concept_capital_flow(date)
        
        if success:
            return {"success": True, "message": f"{date} 资金流向数据刷新成功"}
        else:
            return {"success": False, "message": f"{date} 资金流向数据刷新失败"}
    except Exception as e:
        return {"success": False, "message": f"刷新失败: {str(e)}"}


@router.get("/api/rank-analysis/dates")
def get_rank_analysis_dates():
    """
    获取榜单分析日期列表
    """
    try:
        db = Database()
        if not db.connect():
            return {"success": False, "message": "数据库连接失败"}
        
        try:
            cursor = db.connection.cursor()
            cursor.execute("SELECT DISTINCT date FROM daily_change ORDER BY date DESC")
            dates = cursor.fetchall()
            cursor.close()
            
            formatted_dates = []
            for d in dates:
                date_str = d[0]
                if len(date_str) == 8:
                    formatted_dates.append(f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}")
                else:
                    formatted_dates.append(date_str)
            
            return {"success": True, "data": formatted_dates}
        finally:
            db.close()
    except Exception as e:
        return {"success": False, "message": f"获取日期列表失败: {str(e)}"}


@router.get("/api/rank-analysis/stocks")
def get_rank_analysis_stocks(start_date: str, end_date: str):
    """
    获取在指定日期范围内的榜单股票
    """
    try:
        # 转换日期格式
        def to_db_date(date_str):
            return date_str.replace('-', '')
        
        start_db = to_db_date(start_date)
        end_db = to_db_date(end_date)
        
        # 获取所有有数据的交易日
        db = Database()
        if not db.connect():
            return {"success": False, "message": "数据库连接失败"}
        
        try:
            cursor = db.connection.cursor()
            cursor.execute("""
                SELECT DISTINCT date FROM daily_change 
                WHERE date >= ? AND date <= ? 
                ORDER BY date
            """, (start_db, end_db))
            dates = [row[0] for row in cursor.fetchall()]
            cursor.close()
            
            if not dates:
                return {"success": True, "data": {"dates": [], "stocks": [], "total_days": 0}}
            
            # 对每个交易日，计算前30名
            tushare_service = get_tushare_service()
            stocks_data = {}
            
            for date_str in dates:
                # 计算当天的前30名
                top30 = tushare_service.calculate_top30(date_str, days=10)
                
                # 记录每只股票的出现情况
                for idx, stock in enumerate(top30):
                    ts_code = stock['ts_code']
                    if ts_code not in stocks_data:
                        stocks_data[ts_code] = {
                            'ts_code': ts_code,
                            'symbol': stock['symbol'],
                            'name': stock['name'],
                            'industry': stock.get('industry', '-'),
                            'appearances': []
                        }
                    
                    # 转换日期格式
                    formatted_date = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
                    
                    stocks_data[ts_code]['appearances'].append({
                        'date': formatted_date,
                        'rank': idx + 1,
                        'ten_day_change': stock.get('cumulative_change', 0),
                        'daily_change': stock.get('daily_change', 0)
                    })
            
            # 转换为列表并排序
            result = []
            for ts_code, data in stocks_data.items():
                data['days_count'] = len(data['appearances'])
                data['dates_list'] = [app['date'] for app in data['appearances']]
                result.append(data)
            
            result.sort(key=lambda x: x['days_count'], reverse=True)
            
            # 转换日期格式
            formatted_dates = [f"{d[:4]}-{d[4:6]}-{d[6:8]}" for d in dates]
            
            return {
                "success": True, 
                "data": {
                    "dates": formatted_dates,
                    "stocks": result,
                    "total_days": len(dates)
                }
            }
        finally:
            db.close()
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"success": False, "message": f"获取榜单股票失败: {str(e)}"}


@router.get("/api/rank-analysis/daily-changes")
def get_rank_analysis_daily_changes(ts_codes: str, start_date: str, end_date: str):
    """
    获取指定股票的每日涨幅数据
    ts_codes: 股票代码列表，用逗号分隔
    """
    try:
        db = Database()
        if not db.connect():
            return {"success": False, "message": "数据库连接失败"}
        
        try:
            ts_code_list = ts_codes.split(',')
            
            # 转换日期格式
            def to_db_date(date_str):
                return date_str.replace('-', '')
            
            start_db = to_db_date(start_date)
            end_db = to_db_date(end_date)
            
            # 获取所有有数据的交易日
            cursor = db.connection.cursor()
            cursor.execute("""
                SELECT DISTINCT date FROM daily_change 
                WHERE date >= ? AND date <= ? 
                ORDER BY date
            """, (start_db, end_db))
            dates = [row[0] for row in cursor.fetchall()]
            
            # 获取每只股票的数据
            stocks_data = {}
            for ts_code in ts_code_list:
                cursor.execute("""
                    SELECT ts_code, symbol, name, industry, date, close, change
                    FROM daily_change 
                    WHERE ts_code = ? AND date >= ? AND date <= ?
                    ORDER BY ts_code, date
                """, (ts_code, start_db, end_db))
                
                rows = cursor.fetchall()
                if not rows:
                    continue
                
                stock_info = None
                daily_changes = {}
                for row in rows:
                    if not stock_info:
                        stock_info = {
                            'ts_code': row[0],
                            'symbol': row[1],
                            'name': row[2],
                            'industry': row[3] or '-'
                        }
                    daily_changes[row[4]] = {
                        'close': row[5],
                        'change': row[6]
                    }
                
                if stock_info:
                    stocks_data[ts_code] = {
                        **stock_info,
                        'daily_changes': daily_changes
                    }
            
            cursor.close()
            
            # 转换为列表，并补全所有日期
            result = []
            formatted_dates = [f"{d[:4]}-{d[4:6]}-{d[6:8]}" for d in dates]
            
            for ts_code, data in stocks_data.items():
                complete_changes = []
                for d in dates:
                    formatted_d = f"{d[:4]}-{d[4:6]}-{d[6:8]}"
                    change_data = data['daily_changes'].get(d, {'close': None, 'change': 0.0})
                    complete_changes.append({
                        'date': formatted_d,
                        'close': change_data['close'],
                        'change': change_data['change']
                    })
                
                result.append({
                    **data,
                    'daily_changes': complete_changes
                })
            
            return {
                "success": True, 
                "data": {
                    "dates": formatted_dates,
                    "stocks_data": result
                }
            }
        finally:
            db.close()
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"success": False, "message": f"获取每日涨幅数据失败: {str(e)}"}
