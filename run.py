"""
开发服务器启动脚本

用法:
    python run.py              # 同时启动主服务和数字人服务
    python run.py main         # 仅启动主服务 (8000)
    python run.py avatar       # 仅启动数字人服务 (8001)
    python run.py all          # 同时启动两个服务
"""
import sys
import asyncio
import signal
import uvicorn
from multiprocessing import Process

from main_service.core.config import settings


def run_main_service():
    """启动主服务"""
    uvicorn.run(
        "main_service.main:app",
        host=settings.host,
        port=8000,
        reload=settings.debug
    )


def run_avatar_service():
    """启动数字人服务"""
    uvicorn.run(
        "interview_avatar_service.main:app",
        host=settings.host,
        port=8001,
        reload=settings.debug
    )


def run_all_services():
    """同时启动两个服务"""
    processes = []
    
    # 启动主服务
    main_proc = Process(target=run_main_service, name="main_service")
    main_proc.start()
    processes.append(main_proc)
    print(f"✅ 主服务启动中... http://localhost:8000")
    
    # 启动数字人服务
    avatar_proc = Process(target=run_avatar_service, name="avatar_service")
    avatar_proc.start()
    processes.append(avatar_proc)
    print(f"✅ 数字人服务启动中... http://localhost:8001")
    
    print("\n📋 API 文档:")
    print("   主服务: http://localhost:8000/docs")
    print("   数字人服务: http://localhost:8001/docs")
    print("\n按 Ctrl+C 停止所有服务\n")
    
    def signal_handler(sig, frame):
        print("\n\n🛑 正在停止所有服务...")
        for proc in processes:
            proc.terminate()
            proc.join(timeout=5)
        print("✅ 所有服务已停止")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # 等待所有进程
    for proc in processes:
        proc.join()


if __name__ == "__main__":
    service = sys.argv[1] if len(sys.argv) > 1 else "all"
    
    if service == "main":
        print("🚀 启动主服务 (端口 8000)...")
        run_main_service()
    elif service == "avatar":
        print("🚀 启动数字人服务 (端口 8001)...")
        run_avatar_service()
    else:
        print("🚀 启动所有服务...")
        run_all_services()
