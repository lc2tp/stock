
import http.server
import socketserver
import os
import webbrowser

PORT = 5173

# 更改到前端目录
os.chdir(os.path.dirname(os.path.abspath(__file__)))

Handler = http.server.SimpleHTTPRequestHandler

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"前端服务器启动在 http://localhost:{PORT}")
    print("按 Ctrl+C 停止服务器")
    
    # 自动打开浏览器
    webbrowser.open(f"http://localhost:{PORT}")
    
    httpd.serve_forever()
