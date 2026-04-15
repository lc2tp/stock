
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.tushare_service import TushareService

def generate_html_report(target_date='20260408'):
    # 创建服务实例
    tushare_service = TushareService()
    
    # 调用 calculate_ten_day_top30 方法
    print(f"=== 正在生成 {target_date} 的HTML报告 ===")
    result = tushare_service.calculate_ten_day_top30(target_date)
    
    # 生成HTML
    html_content = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>10日累计涨幅前30 - {target_date}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #333;
            text-align: center;
        }}
        .date-info {{
            text-align: center;
            color: #666;
            margin-bottom: 20px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #e0e0e0;
        }}
        th {{
            background-color: #f5f7fa;
            font-weight: bold;
            color: #606266;
        }}
        tr:hover {{
            background-color: #f5f7fa;
        }}
        .rank {{
            font-weight: bold;
            color: #409EFF;
        }}
        .positive {{
            color: #f56c6c;
        }}
        .negative {{
            color: #67c23a;
        }}
        .summary {{
            margin-top: 20px;
            padding: 15px;
            background-color: #f4f4f5;
            border-radius: 4px;
            color: #606266;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>10日累计涨幅前30</h1>
        <div class="date-info">目标日期: {target_date}</div>
        
        <table>
            <thead>
                <tr>
                    <th>排名</th>
                    <th>代码</th>
                    <th>名称</th>
                    <th>概念</th>
                    <th>10日涨幅(%)</th>
                    <th>单日涨幅(%)</th>
                </tr>
            </thead>
            <tbody>
"""
    
    # 添加数据行
    for i, stock in enumerate(result):
        ten_day_change_class = 'positive' if stock['ten_day_change'] >= 0 else 'negative'
        daily_change_class = 'positive' if stock['daily_change'] >= 0 else 'negative'
        ten_day_change_sign = '+' if stock['ten_day_change'] >= 0 else ''
        daily_change_sign = '+' if stock['daily_change'] >= 0 else ''
        
        html_content += f"""
                <tr>
                    <td class="rank">{i + 1}</td>
                    <td>{stock['symbol']}</td>
                    <td>{stock['name']}</td>
                    <td>{stock['industry'] or '-'}</td>
                    <td class="{ten_day_change_class}">{ten_day_change_sign}{stock['ten_day_change']}%</td>
                    <td class="{daily_change_class}">{daily_change_sign}{stock['daily_change']}%</td>
                </tr>
"""
    
    html_content += f"""
            </tbody>
        </table>
        
        <div class="summary">
            <strong>统计信息：</strong><br>
            目标日期: {target_date}<br>
            股票数量: {len(result)} 只<br>
            数据来源: tushare_service.calculate_ten_day_top30() 方法<br>
            生成时间: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        </div>
    </div>
</body>
</html>
"""
    
    # 保存HTML文件
    output_file = f'ten_day_top30_{target_date}.html'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"\n=== HTML报告已生成 ===")
    print(f"文件路径: {os.path.abspath(output_file)}")
    print(f"股票数量: {len(result)}")
    print(f"\n前10名股票:")
    for i, stock in enumerate(result[:10]):
        print(f"{i+1}. {stock['symbol']} {stock['name']} - 10日涨幅: {stock['ten_day_change']}%")
    
    return output_file

if __name__ == "__main__":
    # 生成20260408的报告
    output = generate_html_report('20260408')
    print(f"\n请用浏览器打开: {output}")
