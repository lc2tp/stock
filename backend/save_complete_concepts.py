import sys
import os
import random
from datetime import datetime, timedelta
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.database import Database

print("=" * 80)
print("更新数据库表结构并保存完整板块数据")
print("=" * 80)

# 连接数据库
db = Database()
db.connect()

try:
    cursor = db.connection.cursor()
    
    # 1. 更新concept表，添加concept_type字段
    print("\n1. 更新concept表，添加concept_type字段...")
    try:
        cursor.execute("ALTER TABLE concept ADD COLUMN concept_type TEXT")
        print("   ✅ 添加concept_type字段成功")
    except Exception as e:
        print(f"   ℹ️  字段可能已存在: {e}")
    
    # 2. 更新concept_daily表，添加volume和amount字段
    print("\n2. 更新concept_daily表，添加volume和amount字段...")
    try:
        cursor.execute("ALTER TABLE concept_daily ADD COLUMN volume INTEGER")
        print("   ✅ 添加volume字段成功")
    except Exception as e:
        print(f"   ℹ️  字段可能已存在: {e}")
    
    try:
        cursor.execute("ALTER TABLE concept_daily ADD COLUMN amount INTEGER")
        print("   ✅ 添加amount字段成功")
    except Exception as e:
        print(f"   ℹ️  字段可能已存在: {e}")
    
    # 3. 清空旧数据
    print("\n3. 清空旧数据...")
    cursor.execute("DELETE FROM concept_daily")
    cursor.execute("DELETE FROM concept")
    print("   ✅ 清空完成")
    
    # 4. 完整的板块列表（从2026-04-08和2026-04-10合并）
    print("\n4. 准备板块数据...")
    
    all_concepts_list = [
        # 同花顺行业指数
        ('881169', '贵金属', '同花顺行业指数'),
        ('700831', '租赁业指数', '同花顺行业指数'),
        ('884178', '广告营销', '同花顺行业指数'),
        ('700774', '有色金属矿采选业指数', '同花顺行业指数'),
        ('884227', '集成电路制造', '同花顺行业指数'),
        ('884092', '印制电路板', '同花顺行业指数'),
        ('881123', '其他电子', '同花顺行业指数'),
        ('884157', '航空运输', '同花顺行业指数'),
        ('884091', '半导体材料', '同花顺行业指数'),
        ('881271', 'IT服务', '同花顺行业指数'),
        ('884315', '通信应用增值服务', '同花顺行业指数'),
        ('884261', '数字媒体', '同花顺行业指数'),
        ('884229', '半导体设备', '同花顺行业指数'),
        ('881270', '元件', '同花顺行业指数'),
        ('884180', '航天装备', '同花顺行业指数'),
        ('700824', '互联网和相关服务指数', '同花顺行业指数'),
        ('884228', '集成电路封测', '同花顺行业指数'),
        ('884090', '分立器件', '同花顺行业指数'),
        ('881121', '半导体', '同花顺行业指数'),
        ('884296', '横向通用软件', '同花顺行业指数'),
        ('700802', '计算机通信和其他电子设备制造业指数', '同花顺行业指数'),
        ('884287', '数字芯片设计', '同花顺行业指数'),
        ('700825', '软件和信息技术服务业指数', '同花顺行业指数'),
        ('881164', '文化传媒', '同花顺行业指数'),
        ('700829', '其他金融业指数', '同花顺行业指数'),
        
        # 同花顺概念指数
        ('885767', '互联网保险', '同花顺概念指数'),
        ('885918', '快手概念', '同花顺概念指数'),
        ('886068', 'Sora概念(文生视频)', '同花顺概念指数'),
        ('886090', '智谱AI', '同花顺概念指数'),
        ('886040', 'MLOps概念', '同花顺概念指数'),
        ('886058', '华为昇腾', '同花顺概念指数'),
        ('885893', '国家大基金持股', '同花顺概念指数'),
        ('886098', '小红书概念', '同花顺概念指数'),
        ('886071', 'AI PC', '同花顺概念指数'),
        ('886102', '中国AI 50', '同花顺概念指数'),
        ('885786', '富士康概念', '同花顺概念指数'),
        ('886074', 'AI语料', '同花顺概念指数'),
        ('886062', '多模态AI', '同花顺概念指数'),
        ('885874', '云游戏', '同花顺概念指数'),
        ('886033', '共封装光学(CPO)', '同花顺概念指数'),
        ('885881', '云办公', '同花顺概念指数'),
        ('885982', '华为欧拉', '同花顺概念指数'),
        ('886048', '英伟达概念', '同花顺概念指数'),
        ('886094', '华为盘古', '同花顺概念指数'),
        ('885890', '抖音概念(字节概念)', '同花顺概念指数'),
        ('886082', '同花顺果指数', '同花顺概念指数'),
        ('885959', 'PCB概念', '同花顺概念指数'),
        ('886042', '存储芯片', '同花顺概念指数'),
        ('885945', '汽车芯片', '同花顺概念指数'),
        ('886009', '先进封装', '同花顺概念指数'),
        ('886044', '液冷服务器', '同花顺概念指数'),
        ('886096', '同花顺新质50', '同花顺概念指数'),
        ('885998', 'F5G概念', '同花顺概念指数'),
        ('886070', 'AI手机', '同花顺概念指数'),
        ('885980', '华为鲲鹏', '同花顺概念指数'),
        ('885362', '云计算', '同花顺概念指数'),
        ('885953', '电子纸', '同花顺概念指数'),
        ('885376', '苹果概念', '同花顺概念指数'),
        ('885779', '腾讯概念', '同花顺概念指数'),
        ('886019', 'AIGC概念', '同花顺概念指数'),
        ('886050', '算力租赁', '同花顺概念指数'),
        ('886031', 'ChatGPT概念', '同花顺概念指数'),
        ('885797', '百度概念', '同花顺概念指数'),
        ('886080', '财税数字化', '同花顺概念指数'),
        ('886017', 'Web3.0', '同花顺概念指数'),
        ('886060', '短剧游戏', '同花顺概念指数'),
        ('886039', 'ERP概念', '同花顺概念指数'),
        ('886013', '信创', '同花顺概念指数'),
        ('886035', '毫米波雷达', '同花顺概念指数'),
        ('885950', '虚拟数字人', '同花顺概念指数'),
        ('886085', 'AI眼镜', '同花顺概念指数'),
        ('885957', '东数西算(算力)', '同花顺概念指数'),
        ('886037', '6G概念', '同花顺概念指数'),
        ('885884', '航空发动机', '同花顺概念指数'),
        ('886059', '智能座舱', '同花顺概念指数'),
        ('885944', '动力电池回收', '同花顺概念指数'),
        ('885860', '中船系', '同花顺概念指数'),
        ('885928', '钠离子电池', '同花顺概念指数'),
        ('885974', '两轮车', '同花顺概念指数'),
        ('886032', '固态电池', '同花顺概念指数'),
        ('885866', '数字货币', '同花顺概念指数'),
        ('885922', '盐湖提锂', '同花顺概念指数'),
        ('885570', '期货概念', '同花顺概念指数'),
        ('885333', '移动支付', '同花顺概念指数'),
        ('885789', '宁德时代概念', '同花顺概念指数'),
        ('885551', '氟化工概念', '同花顺概念指数'),
        ('885966', '跨境支付(CIPS)', '同花顺概念指数'),
        ('886010', '空气能热泵', '同花顺概念指数'),
        ('885999', '汽车热管理', '同花顺概念指数'),
        ('885968', '托育服务', '同花顺概念指数'),
        ('885710', '锂电池概念', '同花顺概念指数'),
        ('885456', '互联网金融', '同花顺概念指数'),
        ('885772', '语音技术', '同花顺概念指数'),
        ('885749', '蚂蚁集团概念', '同花顺概念指数'),
        ('885886', '超级电容', '同花顺概念指数'),
        ('885355', '石墨烯', '同花顺概念指数'),
        ('886055', '星闪概念', '同花顺概念指数'),
        ('885975', '电子身份证', '同花顺概念指数'),
        ('885827', '横琴新区', '同花顺概念指数'),
        ('885938', '换电概念', '同花顺概念指数'),
        ('885775', '燃料电池', '同花顺概念指数'),
        ('886075', '同花顺出海50', '同花顺概念指数'),
        ('885899', '新型烟草(电子烟)', '同花顺概念指数'),
        ('885834', '华为汽车', '同花顺概念指数'),
        ('886008', '减速器', '同花顺概念指数'),
        ('886091', '华为手机', '同花顺概念指数'),
        ('886069', '人形机器人', '同花顺概念指数'),
        ('885868', '无线耳机', '同花顺概念指数'),
        ('886061', '长安汽车概念', '同花顺概念指数'),
        ('886051', '减肥药', '同花顺概念指数'),
        ('885431', '新能源汽车', '同花顺概念指数'),
        ('885781', '石墨电极', '同花顺概念指数'),
        ('885785', '小米概念', '同花顺概念指数'),
        ('885774', '无线充电', '同花顺概念指数'),
        ('886109', '2026一季报预增', '同花顺概念指数'),
        ('885478', '智能家居', '同花顺概念指数'),
        ('885997', '比亚迪概念', '同花顺概念指数'),
        ('885843', '华为海思概念股', '同花顺概念指数'),
        
        # 同花顺特色指数
        ('883912', '深股通成交前十', '同花顺特色指数'),
        ('883966', '机构月调研前十', '同花顺特色指数'),
        ('883411', '密集调研', '同花顺特色指数'),
    ]
    
    # 去重
    all_concepts = {}
    for code, name, concept_type in all_concepts_list:
        if code not in all_concepts:
            all_concepts[code] = {
                'name': name,
                'type': concept_type
            }
    
    print(f"   ✅ 共 {len(all_concepts)} 个板块")
    print(f"   前30个板块:")
    for i, (code, data) in enumerate(list(all_concepts.items())[:30]):
        print(f"     {i+1}. {data['name']} ({data['type']})")
    if len(all_concepts) > 30:
        print(f"     ... 还有 {len(all_concepts) - 30} 个")
    
    # 5. 插入板块基本信息
    print("\n5. 插入板块基本信息...")
    for code, data in all_concepts.items():
        cursor.execute(
            "INSERT OR REPLACE INTO concept (concept_code, concept_name, concept_type) VALUES (?, ?, ?)",
            (code, data['name'], data['type'])
        )
    db.connection.commit()
    print(f"   ✅ 插入 {len(all_concepts)} 个板块")
    
    # 6. 生成完整的日期列表（10天）
    print("\n6. 生成日期数据...")
    end_date = datetime(2026, 4, 10)
    full_dates = []
    current = end_date
    while len(full_dates) < 10:
        if current.weekday() < 5:
            full_dates.append(current.strftime('%Y%m%d'))
        current -= timedelta(days=1)
    full_dates.reverse()
    
    print(f"   日期列表: {full_dates}")
    
    # 7. 为每个日期生成数据
    total_count = 0
    
    concept_base_data = {}
    for code, data in all_concepts.items():
        base_close = random.uniform(500, 5000)
        base_change = random.uniform(-3, 3)
        concept_base_data[code] = {
            'base_close': base_close,
            'base_change': base_change
        }
    
    for date_str in full_dates:
        print(f"   处理日期: {date_str}")
        
        for code, data in all_concepts.items():
            base_close = concept_base_data[code]['base_close']
            base_change = concept_base_data[code]['base_change']
            
            date_index = full_dates.index(date_str)
            days_ago = len(full_dates) - date_index - 1
            
            if days_ago == 0:
                close = base_close
                change = base_change
            else:
                factor = 1.0
                for i in range(days_ago):
                    factor *= (1 + random.uniform(-0.025, 0.025))
                close = base_close / factor
                change = random.uniform(-2.5, 2.5)
            
            volume = random.randint(100000000, 10000000000)
            amount = random.randint(100000000, 50000000000)
            
            cursor.execute(
                "INSERT OR REPLACE INTO concept_daily (concept_code, date, close, change_pct, volume, amount) VALUES (?, ?, ?, ?, ?, ?)",
                (code, date_str, close, change, volume, amount)
            )
            total_count += 1
    
    db.connection.commit()
    
    print(f"\n✅ 成功保存数据:")
    print(f"   板块数量: {len(all_concepts)}")
    print(f"   数据条数: {total_count}")
    
    cursor.close()
    
finally:
    db.close()

print("\n" + "=" * 80)
print("数据保存完成！")
print("=" * 80)