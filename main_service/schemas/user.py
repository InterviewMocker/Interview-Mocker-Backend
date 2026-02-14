"""
用户相关Pydantic模型
"""
from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, field_validator


class UserCreate(BaseModel):
    """用户注册请求"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: Optional[EmailStr] = Field(default=None, description="邮箱地址")
    password: str = Field(..., min_length=8, description="密码")
    real_name: Optional[str] = Field(default=None, description="真实姓名")
    school: Optional[str] = Field(default=None, description="学校")
    major: Optional[str] = Field(default=None, description="专业")
    
    @field_validator('email', mode='before')
    @classmethod
    def empty_string_to_none(cls, v):
        """将空字符串转换为 None"""
        if v == '' or v is None:
            return None
        return v
    
    @field_validator('real_name', 'school', 'major', mode='before')
    @classmethod
    def empty_str_to_none(cls, v):
        """将空字符串转换为 None"""
        if v == '' or v is None:
            return None
        return v


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
