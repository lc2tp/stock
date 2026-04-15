import requests
import json
import time

url = "https://app.jiuyangongshe.com/jystock-app/api/v1/action/field"

headers = {
    "accept": "application/json, text/plain, */*",
    "accept-encoding": "gzip, deflate, br, zstd",
    "accept-language": "zh-CN,zh;q=0.9",
    "connection": "keep-alive",
    "content-type": "application/json",
    "host": "app.jiuyangongshe.com",
    "origin": "https://www.jiuyangongshe.com",
    "platform": "3",
    "referer": "https://www.jiuyangongshe.com/action/2026-04-09",
    "sec-ch-ua": '"Not A(Brand";v="8", "Chromium";v="132", "Google Chrome";v="132"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
    "timestamp": str(int(time.time() * 1000)),
    "token": "ae7353a8af85f29021935df2dbdd74d5",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36"
}

cookie = "SESSION=ZTlhYmFkOWQtZjg2Mi00ZTA1LTkxYjAtMTJjMjAzMDFmODRk; Hm_lvt_58aa18061df7855800f2a1b32d6da7f4=1775223702,1775713239,1775884456,1776123373; Hm_lpvt_58aa18061df7855800f2a1b32d6da7f4=1776123373"

# 解析cookie
cookies = {}
for item in cookie.split('; '):
    if '=' in item:
        key, value = item.split('=', 1)
        cookies[key] = value

data = {
    "date": "2026-04-09",
    "pc": 1
}

try:
    response = requests.post(url, headers=headers, cookies=cookies, json=data)
    print("Status Code:", response.status_code)
    print("\nResponse:")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))
except Exception as e:
    print("Error:", e)
    import traceback
    traceback.print_exc()
