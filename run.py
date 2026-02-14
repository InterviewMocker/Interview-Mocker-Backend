"""
开发服务器启动脚本
"""
import uvicorn

from main_service.core.config import settings

if __name__ == "__main__":
    uvicorn.run(
        "main_service.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
