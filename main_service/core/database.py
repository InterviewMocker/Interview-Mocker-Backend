"""
数据库配置 - 使用共享数据库连接
"""
from shared.database import (
    engine,
    AsyncSessionLocal,
    get_db_session,
    init_shared_db,
    close_shared_db,
)
from shared.models import Base

# 重新导出，保持兼容性
async_session_maker = AsyncSessionLocal
get_db = get_db_session
init_db = init_shared_db
close_db = close_shared_db
