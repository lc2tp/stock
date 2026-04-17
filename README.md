# 股票数据系统

## 项目简介
这是一个股票数据查询和分析系统，包含前端和后端两部分，提供板块数据查询、个股资金流向分析等功能。

## 数据库说明

### 数据库文件
**当前使用的数据库**：`E:\stock\backend\stock_system.db`

### 数据库表结构

**concept 表（板块信息表）**
- `concept_code` - 板块代码
- `concept_name` - 板块名称
- `concept_type` - 板块类型（概念/行业）

**concept_daily 表（板块每日数据表）**
- `concept_code` - 板块代码
- `date` - 日期（格式: YYYYMMDD）
- `close` - 收盘价
- `change_pct` - 涨跌幅
- `volume` - 成交量
- `amount` - 成交额

## 项目结构

```
E:\stock
├── backend/              # 后端代码
│   ├── api/             # API路由
│   │   └── routes.py    # 主要接口
│   ├── models/          # 数据模型
│   │   └── database.py  # 数据库操作
│   ├── services/        # 业务服务
│   ├── main.py          # 后端启动文件
│   └── stock_system.db  # 数据库文件
├── frontend/            # 前端代码
│   ├── src/
│   ├── package.json
│   └── vite.config.js
└── backups/             # 备份文件
```

## 启动方式

### 1. 后端启动
```bash
cd E:\stock\backend
python main.py
```
后端运行在 http://localhost:8000

### 2. 前端启动
```bash
cd E:\stock\frontend
npm run dev
```
前端运行在 http://localhost:5173

### 3. 一键启动
双击运行 `start_all.bat` 可以同时启动前端和后端。

## 核心功能

### 1. 板块数据同步
- **接口**：`POST /api/concept/refresh`
- **功能**：从同花顺问财获取板块数据并同步到数据库
- **使用工具**：pywencai（同花顺问财Python SDK）

### 2. 板块数据查询
- **接口**：`GET /api/concept/data?days=5`
- **功能**：查询指定天数的板块涨幅排名
- **区间涨跌幅计算方式**：使用区间首尾收盘价计算，公式为 `((结束收盘价 - 起始收盘价) / 起始收盘价) * 100`

### 3. 十日涨幅榜
- **接口**：`GET /api/tushare/ten-day-top30`
- **功能**：查询近10日涨幅榜TOP30

### 4. 个股资金流向
- **接口**：`GET /api/stock-capital-flow/consecutive`
- **功能**：查询个股连续资金流入/流出数据

## 修复记录

### 1. 板块同步数据字段匹配错误（2026-04-17）
- **问题**：之前错误地匹配了含"排名"的列（如"涨跌幅排名基数"），导致当日涨跌幅数据不正确
- **修复**：在 `backend/api/routes.py` 中添加了 `'排名' not in col` 条件，确保只匹配真正的涨跌幅列
- **修改位置**：`E:\stock\backend\api\routes.py:617`

### 2. 区间涨跌幅计算方式错误（2026-04-17）
- **问题**：之前用单日涨跌幅连乘，和同花顺的计算方式不一致
- **修复**：改为用区间首尾收盘价来计算，这样就能和同花顺完全一致了
- **计算方式**：`((结束收盘价 - 起始收盘价) / 起始收盘价) * 100`
- **修改位置**：`E:\stock\backend\api\routes.py:729-749`
- **验证结果**：884284（钴板块）的5日涨幅正确显示为14.81%，和同花顺一致

## 数据来源

- **同花顺问财** - https://www.iwencai.com/
- **tushare** - 股票行情数据

## 注意事项

1. **日期格式**：
   - 查询时使用 `YYYY-M-D` 格式（不带前导0）
   - 数据库存储使用 `YYYYMMDD` 格式

2. **Cookie 有效期**：同花顺Cookie可能会过期，需要定期更新

3. **交易日判断**：周末不是交易日，无需查询数据

4. **请求频率**：建议每次请求间隔1秒，避免请求过快

## 常用命令

```bash
# 查看数据库中的日期
python -c "
import sqlite3
conn = sqlite3.connect('E:/stock/backend/stock_system.db')
cursor = conn.cursor()
cursor.execute('SELECT DISTINCT date FROM concept_daily ORDER BY date DESC')
print([row[0] for row in cursor.fetchall()])
conn.close()
"
```
