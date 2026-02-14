"""
认证授权API
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.database import get_db
from ...core.dependencies import get_current_user
from ...schemas.user import UserCreate, UserLogin, TokenResponse, UserResponse, PasswordChange
from ...schemas.common import ResponseModel
from ...services.auth_service import AuthService
from shared.models import User

router = APIRouter()


@router.post("/register", response_model=ResponseModel[UserResponse])
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """用户注册"""
    # 调试输出
    print(f"[DEBUG] 注册请求数据: username={user_data.username}, password长度={len(user_data.password)}")
    auth_service = AuthService(db)
    user = await auth_service.register(user_data)
    print(f"[DEBUG] 注册成功: user_id={user.id}")
    return ResponseModel(
        message="注册成功",
        data=UserResponse.model_validate(user)
    )


@router.post("/login", response_model=ResponseModel[TokenResponse])
async def login(
    login_data: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    """用户登录"""
    auth_service = AuthService(db)
    result = await auth_service.login(login_data)
    return ResponseModel(
        message="登录成功",
        data=result
    )


@router.post("/logout", response_model=ResponseModel)
async def logout(
    current_user: User = Depends(get_current_user)
):
    """用户登出"""
    # TODO: 实现Token黑名单
    return ResponseModel(message="登出成功")


@router.post("/refresh", response_model=ResponseModel[TokenResponse])
async def refresh_token(
    db: AsyncSession = Depends(get_db)
):
    """刷新Token"""
    # TODO: 实现Token刷新
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="功能开发中"
    )


@router.post("/password/change", response_model=ResponseModel)
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """修改密码"""
    auth_service = AuthService(db)
    await auth_service.change_password(
        current_user.id,
        password_data.old_password,
        password_data.new_password
    )
    return ResponseModel(message="密码修改成功")


@router.get("/me", response_model=ResponseModel[UserResponse])
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """获取当前用户信息"""
    return ResponseModel(
        data=UserResponse.model_validate(current_user)
    )
