"""
健康检查API
"""
from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "service": "AI模拟面试平台-主服务"
    }


@router.get("/")
async def root():
    """根路径"""
    return {
        "message": "AI模拟面试平台 API",
        "version": "1.0.0",
        "docs": "/docs"
    }
