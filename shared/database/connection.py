"""
共享数据库连接 - 两个服务使用相同的数据库
"""
import os
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import text
from sqlalchemy.pool import NullPool

from shared.config.settings import get_shared_settings

settings = get_shared_settings()

# 确保数据目录存在
os.makedirs("./data", exist_ok=True)

# 创建共享引擎
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    future=True,
    poolclass=NullPool,
    connect_args={
        "check_same_thread": False,
        "timeout": 30,  # 增加超时时间到30秒
    }
)

# 创建异步会话工厂
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """获取数据库会话依赖"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_shared_db():
    """初始化数据库表（使用共享模型）"""
    from shared.models import Base
    
    try:
        # 创建表结构
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            
    except Exception as e:
        print(f"[WARN] Database init warning: {e}")



async def close_shared_db():
    """关闭数据库连接"""
    await engine.dispose()
