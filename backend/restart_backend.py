import subprocess
import time
import sys

def kill_all_python():
    try:
        result = subprocess.run(
            ['tasklist', '/FI', 'IMAGENAME eq python.exe'],
            capture_output=True, 
            text=True, 
            encoding='gbk', 
            errors='ignore'
        )
        print("Python进程:")
        print(result.stdout)
        
        # 杀掉所有python.exe
        subprocess.run(['taskkill', '/F', '/IM', 'python.exe'], capture_output=True)
        time.sleep(2)
        print("已尝试杀掉所有Python进程")
    except Exception as e:
        print(f"杀掉进程失败: {e}")

if __name__ == "__main__":
    kill_all_python()
    print("\n等待2秒...")
    time.sleep(2)
    print("现在请手动运行: start_backend.bat")
