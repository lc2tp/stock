
import requests

try:
    response = requests.get("http://localhost:8000/api/concept/data?days=10", timeout=10)
    print(f"Status Code: {response.status_code}")
    
    data = response.json()
    print(f"\nSuccess: {data.get('success')}")
    print(f"Message: {data.get('message')}")
    
    if data.get('success') and data.get('data'):
        items = data['data']
        print(f"\n返回了 {len(items)} 条数据")
        
        print("\n=== 前3条数据 ===")
        for i, item in enumerate(items[:3]):
            print(f"{i+1}. {item['concept_name']}")
            print(f"   today_change: {item.get('today_change')}")
            print(f"   today_volume: {item.get('today_volume')}")
            
except Exception as e:
    print(f"Error: {e}")

