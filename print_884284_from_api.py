
import requests
import json

try:
    response = requests.get("http://localhost:8000/api/concept/data?days=10", timeout=10)
    print(f"Status Code: {response.status_code}")
    
    data = response.json()
    
    if data.get('success') and data.get('data'):
        items = data['data']
        
        for i, item in enumerate(items):
            if item.get('concept_code') == '884284':
                print(f"\n找到第 {i+1} 条是 884284!")
                print(json.dumps(item, indent=2, ensure_ascii=False))
                break
                
except Exception as e:
    print(f"Error: {e}")

