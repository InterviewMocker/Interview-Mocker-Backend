"""
面试会话相关Pydantic模型
"""
from datetime import datetime
from typing import Optional, List
from decimal import Decimal
from pydantic import BaseModel, Field


class InterviewSessionCreate(BaseModel):
    """创建面试会话请求"""
    position_id: str
    session_config: Optional[dict] = None
    interview_mode: str = "ai"
    scheduled_at: Optional[datetime] = None


class InterviewSessionResponse(BaseModel):
    """面试会话响应"""
    id: str
    user_id: str
    position_id: str
    status: str
    interview_mode: str
    total_questions: int
    answered_questions: int
    overall_score: Optional[float] = None
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class InterviewQARecordResponse(BaseModel):
    """面试问答记录响应"""
    id: str
    session_id: str
    question_id: str
    question_order: Optional[int] = None
    answer_text: Optional[str] = None
    score: Optional[float] = None
    ai_feedback: Optional[str] = None
    strengths: Optional[List[str]] = None
    weaknesses: Optional[List[str]] = None
    asked_at: Optional[datetime] = None
    answered_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class AnswerSubmit(BaseModel):
    """提交答案请求"""
    question_id: str
    answer_text: str
    answer_audio_url: Optional[str] = None
    thinking_time_seconds: Optional[int] = None
