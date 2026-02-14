"""
用户相关Pydantic模型
"""
from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    """用户注册请求"""
    username: str = Field(..., min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    password: str = Field(..., min_length=8)
    real_name: Optional[str] = None
    school: Optional[str] = None
    major: Optional[str] = None


class UserLogin(BaseModel):
    """用户登录请求"""
    username: str
    password: str
    device_type: Optional[str] = "web"


class UserUpdate(BaseModel):
    """用户信息更新"""
    real_name: Optional[str] = None
    avatar_url: Optional[str] = None
    gender: Optional[str] = None
    birth_date: Optional[date] = None
    school: Optional[str] = None
    major: Optional[str] = None
    graduation_year: Optional[int] = None


class UserResponse(BaseModel):
    """用户响应"""
    id: str
    username: str
    email: Optional[str] = None
    real_name: Optional[str] = None
    avatar_url: Optional[str] = None
    role: str
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """Token响应"""
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_in: int
    user: UserResponse


class PasswordChange(BaseModel):
    """密码修改"""
    old_password: str
    new_password: str = Field(..., min_length=8)


class UserProfileResponse(BaseModel):
    """用户画像响应"""
    id: str
    user_id: str
    target_positions: Optional[List[str]] = None
    skill_tags: Optional[dict] = None
    technical_score: int = 0
    expression_score: int = 0
    logic_score: int = 0
    comprehensive_score: int = 0
    total_interviews: int = 0
    total_questions_answered: int = 0
    
    class Config:
        from_attributes = True
