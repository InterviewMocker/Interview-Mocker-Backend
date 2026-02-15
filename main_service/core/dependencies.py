"""
FastAPI 依赖注入
"""
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from .database import get_db
from .security import decode_token
from .config import settings
from shared.models import User


security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    获取当前登录用户
    
    开发模式 (AUTH_DEV_MODE=true):
    - 跳过JWT验证
    - 返回或创建模拟用户
    
    生产模式:
    1. 提取Token
    2. 验证Token签名
    3. 检查Token是否过期
    4. 从数据库获取用户信息
    5. 检查用户状态
    """
    # 开发模式：跳过认证，使用模拟用户
    if settings.auth_dev_mode:
        return await _get_or_create_dev_user(db)
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无效的认证凭证",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    if credentials is None:
        raise credentials_exception
    
    token = credentials.credentials
    payload = decode_token(token)
    
    if payload is None:
        raise credentials_exception
    
    user_id: str = payload.get("sub")
    token_type: str = payload.get("type")
    
    if user_id is None or token_type != "access":
        raise credentials_exception
    
    # 从数据库获取用户
    result = await db.execute(
        select(User).where(
            User.id == user_id,
            User.deleted_at.is_(None)
        )
    )
    user = result.scalar_one_or_none()
    
    if user is None:
        raise credentials_exception
    
    # 检查用户状态
    if user.status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="账号已被禁用"
        )
    
    return user


async def _get_or_create_dev_user(db: AsyncSession) -> User:
    """获取或创建开发模式用户"""
    DEV_USER_ID = "dev-user-00000000-0000-0000-0000-000000000000"
    
    result = await db.execute(
        select(User).where(User.id == DEV_USER_ID)
    )
    user = result.scalar_one_or_none()
    
    if user is None:
        from .security import hash_password
        user = User(
            id=DEV_USER_ID,
            username="dev_user",
            password_hash=hash_password("dev123456"),
            real_name="开发测试用户",
            status="active",
            role="admin"
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
    
    return user


async def get_current_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    """获取当前管理员用户，非管理员返回 403"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限"
        )
    return current_user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """获取当前活跃用户"""
    if current_user.status != "active":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户账号未激活"
        )
    return current_user


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(
        HTTPBearer(auto_error=False)
    ),
    db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    """可选的用户认证(用于公开API)"""
    if credentials is None:
        return None
    
    try:
        return await get_current_user(credentials, db)
    except HTTPException:
        return None
