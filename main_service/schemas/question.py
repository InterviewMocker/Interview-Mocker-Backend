"""
题目相关Pydantic模型
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class QuestionBankCreate(BaseModel):
    """创建题库请求"""
    name: str = Field(..., max_length=100)
    description: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None


class QuestionBankUpdate(BaseModel):
    """更新题库请求"""
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    status: Optional[str] = None


class QuestionBankResponse(BaseModel):
    """题库响应"""
    id: str
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    status: str
    created_by: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class QuestionCreate(BaseModel):
    """创建题目请求"""
    bank_id: str = Field(..., description="所属题库ID")
    title: str = Field(..., max_length=200)
    content: str
    type: str = Field(..., description="technical/scenario/algorithm/behavioral")
    category: Optional[str] = None
    difficulty: str = Field(..., description="easy/medium/hard")
    difficulty_score: Optional[int] = Field(None, ge=1, le=10)
    tags: Optional[List[str]] = None
    reference_answer: Optional[str] = None
    answer_key_points: Optional[List[str]] = None
    scoring_criteria: Optional[dict] = None


class QuestionUpdate(BaseModel):
    """更新题目请求"""
    title: Optional[str] = None
    content: Optional[str] = None
    type: Optional[str] = None
    category: Optional[str] = None
    difficulty: Optional[str] = None
    difficulty_score: Optional[int] = None
    tags: Optional[List[str]] = None
    reference_answer: Optional[str] = None
    answer_key_points: Optional[List[str]] = None
    scoring_criteria: Optional[dict] = None
    status: Optional[str] = None


class QuestionResponse(BaseModel):
    """题目响应"""
    id: str
    bank_id: str
    title: str
    content: str
    type: str
    category: Optional[str] = None
    difficulty: str
    difficulty_score: Optional[int] = None
    tags: Optional[List[str]] = None
    usage_count: int = 0
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class QuestionDetailResponse(QuestionResponse):
    """题目详情响应（包含答案）"""
    reference_answer: Optional[str] = None
    answer_key_points: Optional[List[str]] = None
    scoring_criteria: Optional[dict] = None
