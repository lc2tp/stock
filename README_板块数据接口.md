# 板块数据接口说明

## 使用工具
- **pywencai** - 同花顺问财Python SDK

## 数据来源
- **同花顺问财** - https://www.iwencai.com/

## 接口参数

### 1. 基本查询
```python
import pywencai

df = pywencai.get(
    query=f'同花顺板块{display_date}涨幅排名',
    query_type='zhishu',
    cookie=cookie,
    loop=True,
    log=False
)
```

### 2. 参数说明

| 参数 | 说明 | 示例 |
|------|------|------|
| `query` | 查询语句 | `同花顺板块2026-4-13涨幅排名` |
| `query_type` | 查询类型 | `zhishu` (指数) |
| `cookie` | 同花顺登录Cookie | 见下方完整Cookie |
| `loop` | 是否循环查询 | `True` |
| `log` | 是否输出日志 | `False` |

### 3. 日期格式
- Python `datetime` 对象转换格式：`2026-4-13` （注意月份和日期不带前导0）
- 数据库存储格式：`20260413`

## Cookie 信息

```
Hm_lvt_722143063e4892925903024537075d0d=1762053407; Hm_lvt_929f8b362150b1f77b477230541dbbc2=1762053407; _ga=GA1.1.1772044638.1774584118; Hm_lvt_69929b9dce4c22a060bd22d703b2a280=1775223552; Hm_lvt_78c58f01938e4d85eaf619eae71b4ed1=1775223586; _ga_H2RK0R0681=GS2.1.s1775227329$o3$g0$t1775227329$j60$l0$h0; _clck=1c5tbcc%7C2%7Cg54%7C0%7C0; cid=41e74c739a4f0f36057ade69f7eef7941775870880; u_ukey=A10702B8689642C6BE607730E11E6E4A; u_uver=1.0.0; u_dpass=svWfMekV956NiwfTjTb2Ek140n5KoCAMzXKmxnnbj7gt9XCkSCI8PbsyWPa6SXHSHi80LrSsTFH9a%2B6rtRvqGg%3D%3D; u_did=0F0E7AACFAA84FA9A5944F2155A44AC3; u_ttype=WEB; ttype=WEB; user=MDptb181aGZybWl4NDM6Ok5vbmU6NTAwOjc4MDc2NTM0ODo3LDExMTExMTExMTExLDQwOzQ0LDExLDQwOzYsMSw0MDs1LDEsNDA7MSwxMDEsNDA7MiwxLDQwOzMsMSw0MDs1LDEsNDA7OCwwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMSw0MDsxMDIsMSw0MDoyNDo6Ojc3MDc2NTM0ODoxNzc1OTA2MjcwOjo6MTc0MDYzMzEyMDo2MDQ4MDA6MDoxYWM4ZmFhZDliYzZmYmI2ZWI1YzE4ZjA1YmI0NWNkNzg6ZGVmYXVsdF81OjE%3D; userid=770765348; u_name=mo_5hfrmix43; escapename=mo_5hfrmix43; ticket=8c61d82aba33123d44fab2f75d5ba627; user_status=0; utk=b717ec8df5c2a00e53d5ceca17953cbc; sess_tk=eyJ0eXAiOiJKV1QiLCJhbGciOiJFUzI1NiIsImtpZCI6InNlc3NfdGtfMSIsImJ0eSI6InNlc3NfdGsifQ.eyJqdGkiOiI3OGNkNDViYjA1OGZjMWI1NmViYjZmYmNkOWFhOGZhYzEiLCJpYXQiOjE3NzU5MDYyNzAsImV4cCI6MTc3NjUxMTA3MCwic3ViIjoiNzcwNzY1MzQ4IiwiaXNzIjoidXBhc3MuMTBqcWthLmNvbS5jbiIsImF1ZCI6IjIwMjAxMTE4NTI4ODkwNzIiLCJhY3QiOiJvZmMiLCJjdWhzIjoiNWVlMDcwMTBiNjhiNDQ3M2JmOWQzYjI1YWZlZTBhYWI2MzMxYTJkNjYzNTFjYTQwZjk0YWQ0NGRkYTAwZGFjYSJ9.Pdk1I16Wh1xKgDtc3p-zJlAXe3ffu2lUSzVBdmb8UWjv5IWdrbeMRB8TeWIn36Kl01KQQ8X5kpaFnwBC-XtVlA; cuc=q3eg4akd2i90; _clsk=6ys1ii1hzxuo%7C1775906273987%7C2%7C1%7C; v=AypyilT0Nz_8X7tTybj02JWye5vGm6-coB4imbTi03MJs8QFnCv-BXCvcryH
```

## 返回数据字段

从 pywencai 返回的 DataFrame 包含以下关键字段：

| 字段 | 说明 | 示例 |
|------|------|------|
| `code` | 板块代码 | `885767` |
| `指数简称` | 板块名称 | `互联网保险` |
| `指数@同花顺板块指数` | 板块类型 | `概念` / `行业` |
| `收盘价{日期}` | 收盘价 | `1003.60` |
| `涨跌幅{日期}` | 涨跌幅 | `1.51` |

## 数据存储

### 数据库表结构

**concept 表：**
- `concept_code` - 板块代码
- `concept_name` - 板块名称
- `concept_type` - 板块类型

**concept_daily 表：**
- `concept_code` - 板块代码
- `date` - 日期 (格式: YYYYMMDD)
- `close` - 收盘价
- `change_pct` - 涨跌幅
- `volume` - 成交量
- `amount` - 成交额

## 使用示例

```python
import pywencai
from datetime import datetime

# 1. 准备参数
date = '2026-04-13'
dt = datetime.strptime(date, '%Y-%m-%d')
display_date = f"{dt.year}-{dt.month}-{dt.day}"  # 2026-4-13

# 2. 查询数据
df = pywencai.get(
    query=f'同花顺板块{display_date}涨幅排名',
    query_type='zhishu',
    cookie=cookie,
    loop=True,
    log=False
)

# 3. 解析数据
date_str = date.replace('-', '')  # 20260413

for idx, row in df.iterrows():
    code = str(row['code'])
    name = str(row['指数简称'])
    
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
    
    close = float(row[close_col]) if close_col else 0.0
    change_pct = float(row[change_col]) if change_col else 0.0
```

## 注意事项

1. **日期格式**：查询时使用 `YYYY-M-D` 格式（不带前导0），数据库存储使用 `YYYYMMDD` 格式
2. **Cookie 有效期**：Cookie 可能会过期，需要定期更新
3. **交易日判断**：周末不是交易日，无需查询
4. **请求频率**：建议每次请求间隔1秒，避免请求过快

## 文件位置

- 数据获取脚本：`E:\stock\backend\get_concept_data.py`
- API 接口：`E:\stock\backend\api\routes.py` - `/api/concept/refresh`
