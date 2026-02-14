"""
数字人面试服务 - FastAPI 入口
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from shared.config.settings import get_shared_settings
from shared.database import init_shared_db, close_shared_db

settings = get_shared_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时
    await init_shared_db()
    yield
    # 关闭时
    await close_shared_db()


app = FastAPI(
    title="AI数字人面试服务",
    description="提供数字人面试交互功能，与主服务通过HTTP通信",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """根路径"""
    return {
        "service": "AI数字人面试服务",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    import httpx
    
    status = {
        "service": "avatar-service",
        "status": "healthy",
        "checks": {}
    }
    
    # 检查主服务连接
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{settings.MAIN_SERVICE_URL}/health")
            if resp.status_code == 200:
                status["checks"]["main_service"] = "reachable"
            else:
                status["checks"]["main_service"] = f"status: {resp.status_code}"
    except Exception as e:
        status["checks"]["main_service"] = f"unreachable: {str(e)}"
        status["status"] = "degraded"
    
    return status


# TODO: 添加更多路由
# from .api.v1 import router as api_v1_router
# app.include_router(api_v1_router, prefix="/api/v1")
