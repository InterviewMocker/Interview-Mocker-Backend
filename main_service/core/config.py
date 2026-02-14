"""
应用配置管理
"""
from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置"""
    
    # 应用设置
    app_name: str = "AI模拟面试平台"
    app_env: str = "development"
    debug: bool = True
    api_v1_prefix: str = "/api/v1"
    
    # 服务器设置
    host: str = "0.0.0.0"
    port: int = 8000
    
    # 数据库设置 (开发阶段使用SQLite)
    database_url: str = "sqlite+aiosqlite:///./data/interview_mocker.db"
    
    # JWT设置
    jwt_secret_key: str = "your-super-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 120
    refresh_token_expire_days: int = 7
    
    # Redis设置 (可选)
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    
    # LLM设置
    openai_api_key: Optional[str] = None
    llm_provider: str = "openai"
    llm_model: str = "gpt-4"
    
    # ChromaDB设置
    chroma_persist_directory: str = "./data/chroma"
    
    # 存储设置
    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin"
    minio_bucket: str = "interview-files"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """获取配置单例"""
    return Settings()


settings = get_settings()
