"""
岗位相关Pydantic模型
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class PositionCreate(BaseModel):
    """创建岗位请求"""
    name: str = Field(..., max_length=100)
    code: str = Field(..., max_length=50)
    category: Optional[str] = None
    description: Optional[str] = None
    requirements: Optional[str] = None
    required_skills: Optional[List[str]] = None
    skill_weights: Optional[dict] = None
    difficulty_level: Optional[str] = None
    education_requirement: Optional[str] = Field(default=None, description="学历要求: 不限/大专/本科/硕士/博士")
    default_question_count: int = 10
    default_duration: int = 30


class PositionUpdate(BaseModel):
    """更新岗位请求"""
    name: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    requirements: Optional[str] = None
    required_skills: Optional[List[str]] = None
    skill_weights: Optional[dict] = None
    difficulty_level: Optional[str] = None
    education_requirement: Optional[str] = None
    default_question_count: Optional[int] = None
    default_duration: Optional[int] = None
    status: Optional[str] = None


class PositionResponse(BaseModel):
    """岗位响应"""
    id: str
    name: str
    code: str
    category: Optional[str] = None
    description: Optional[str] = None
    required_skills: Optional[List[str]] = None
    difficulty_level: Optional[str] = None
    education_requirement: Optional[str] = None
    default_question_count: int
    default_duration: int
    status: str
    created_by: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True
