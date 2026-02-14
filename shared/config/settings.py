"""
共享配置 - 两个服务使用相同的配置
"""
from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings


class SharedSettings(BaseSettings):
    """共享配置"""
    
    # 数据库配置 (开发阶段使用 SQLite)
    DATABASE_URL: str = "sqlite+aiosqlite:///./data/interview_mocker.db"
    
    # ChromaDB 向量数据库
    CHROMA_PERSIST_DIRECTORY: str = "./data/chroma"
    CHROMA_HOST: Optional[str] = None  # 生产环境使用 HTTP 客户端
    CHROMA_PORT: int = 8000
    
    # Redis (可选)
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # 服务地址
    MAIN_SERVICE_URL: str = "http://localhost:8000"
    AVATAR_SERVICE_URL: str = "http://localhost:8001"
    
    # 服务间认证
    INTERNAL_SERVICE_TOKEN: str = "dev-internal-token-change-in-production"
    
    # 调试模式
    DEBUG: bool = True
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"  # 忽略 .env 中的其他配置项


@lru_cache()
def get_shared_settings() -> SharedSettings:
    """获取共享配置单例"""
    return SharedSettings()
