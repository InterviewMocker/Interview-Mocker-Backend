"""
同时启动两个 FastAPI 服务
"""
import subprocess
import sys
import time
import signal
import os

# 确保在项目根目录运行
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

processes = []


def signal_handler(sig, frame):
    """处理 Ctrl+C 信号"""
    print("\n正在停止服务...")
    for p in processes:
        p.terminate()
    sys.exit(0)


def main():
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    print("=" * 50)
    print("启动 AI 模拟面试平台服务")
    print("=" * 50)
    
    # 启动主服务
    print("\n[1/2] 启动主服务 (端口 8000)...")
    main_service = subprocess.Popen([
        sys.executable, "-m", "uvicorn",
        "main_service.main:app",
        "--host", "0.0.0.0",
        "--port", "8000",
        "--reload"
    ])
    processes.append(main_service)
    
    time.sleep(2)  # 等待主服务启动
    
    # 启动数字人服务
    print("[2/2] 启动数字人面试服务 (端口 8001)...")
    avatar_service = subprocess.Popen([
        sys.executable, "-m", "uvicorn",
        "interview_avatar_service.main:app",
        "--host", "0.0.0.0",
        "--port", "8001",
        "--reload"
    ])
    processes.append(avatar_service)
    
    print("\n" + "=" * 50)
    print("服务已启动!")
    print("=" * 50)
    print("\n主服务 API 文档:       http://localhost:8000/docs")
    print("数字人服务 API 文档:   http://localhost:8001/docs")
    print("\n按 Ctrl+C 停止所有服务")
    print("=" * 50 + "\n")
    
    # 等待进程
    try:
        for p in processes:
            p.wait()
    except KeyboardInterrupt:
        signal_handler(None, None)


if __name__ == "__main__":
    main()
