
import requests
import json

BASE_URL = "http://localhost:8000"

print("=== 测试 API 接口 ===\n")

print("1. 测试 /api/jiuyang/dates")
try:
    response = requests.get(f"{BASE_URL}/api/jiuyang/dates", timeout=5)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"   成功: {result.get('success')}")
        if result.get('success'):
            dates = result.get('data', [])
            print(f"   日期数量: {len(dates)}")
            if len(dates) > 0 and print(f"   前3个日期: {dates[:3]}")
except Exception as e:
    print(f"   ❌ 错误: {e}")

print("\n2. 测试 /api/jiuyang/data (默认日期)")
try:
    response = requests.get(f"{BASE_URL}/api/jiuyang/data", timeout=5)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"   成功: {result.get('success')}")
        if result.get('success'):
            data = result.get('data', [])
            print(f"   数据数量: {len(data)}")
except Exception as e:
    print(f"   ❌ 错误: {e}")

