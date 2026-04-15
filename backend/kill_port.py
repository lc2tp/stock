import subprocess
import re

def kill_process_on_port(port):
    try:
        # 使用 netstat 查找端口
        result = subprocess.run(
            ['netstat', '-ano'], 
            capture_output=True, 
            text=True, 
            encoding='gbk', 
            errors='ignore'
        )
        
        lines = result.stdout.split('\n')
        pids = []
        
        for line in lines:
            if f':{port}' in line and 'LISTENING' in line:
                # 提取 PID
                parts = re.split(r'\s+', line.strip())
                if parts:
                    pid = parts[-1]
                    if pid.isdigit():
                        pids.append(pid)
        
        if pids:
            print(f"找到进程: {pids}")
            for pid in pids:
                try:
                    subprocess.run(['taskkill', '/F', '/PID', pid], check=True)
                    print(f"已杀掉进程 {pid}")
                except Exception as e:
                    print(f"杀掉进程 {pid} 失败: {e}")
        else:
            print(f"端口 {port} 没有找到监听进程")
            
    except Exception as e:
        print(f"错误: {e}")

if __name__ == "__main__":
    kill_process_on_port(8000)
