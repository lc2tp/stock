
import requests

try:
    response = requests.get("http://localhost:8000/api/concept/data?days=10", timeout=10)
    print(f"Status Code: {response.status_code}")
    
    data = response.json()
    
    if data.get('success') and data.get('data'):
        items = data['data']
        print(f"\n返回了 {len(items)} 条数据")
        
        print("\n=== 找名称包含'钴'的板块 ===")
        for i, item in enumerate(items):
            if '钴' in item['concept_name']:
                print(f"\n{i+1}. {item['concept_name']}")
                print(f"   concept_code: {item['concept_code']}")
                print(f"   concept_type: {item.get('concept_type')}")
                print(f"   today_change: {item.get('today_change')}")
                print(f"   today_volume: {item.get('today_volume')}")
                
except Exception as e:
    print(f"Error: {e}")

