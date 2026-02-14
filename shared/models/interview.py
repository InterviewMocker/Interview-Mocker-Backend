"""
面试会话相关数据模型
"""
from datetime import datetime
from typing import Optional
from decimal import Decimal

from sqlalchemy import String, Integer, Text, JSON, DECIMAL, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin, generate_uuid


class InterviewSession(Base, TimestampMixin):
    """面试会话表"""
    __tablename__ = "interview_sessions"
    
    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=generate_uuid
    )
    
    # 关联信息
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    position_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("positions.id"),
        nullable=False
    )
    
    # 会话配置
    session_config: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # 会话状态
    status: Mapped[str] = mapped_column(String(20), default="pending")
    
    # 时间信息
    scheduled_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    ended_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    duration_seconds: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # 面试模式
    interview_mode: Mapped[str] = mapped_column(String(20), default="ai")
    
    # AI数字人微服务会话ID
    avatar_session_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # 统计数据
    total_questions: Mapped[int] = mapped_column(Integer, default=0)
    answered_questions: Mapped[int] = mapped_column(Integer, default=0)
    
    # 综合评分
    overall_score: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(5, 2), nullable=True)
    
    # 关系
    qa_records: Mapped[list["InterviewQARecord"]] = relationship(
        "InterviewQARecord",
        back_populates="session"
    )


class InterviewQARecord(Base, TimestampMixin):
    """面试问答记录表"""
    __tablename__ = "interview_qa_records"
    
    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=generate_uuid
    )
    
    # 关联信息
    session_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("interview_sessions.id", ondelete="CASCADE"),
        nullable=False
    )
    question_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("questions.id"),
        nullable=False
    )
    
    # 问题序号
    question_order: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # 问题内容快照
    question_snapshot: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # 用户回答
    answer_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    answer_audio_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    answer_duration_seconds: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # 回答时间
    asked_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    answered_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    thinking_time_seconds: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # 评估结果
    score: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(5, 2), nullable=True)
    evaluation_result: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # AI反馈
    ai_feedback: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    strengths: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    weaknesses: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # 是否追问
    is_follow_up: Mapped[bool] = mapped_column(Boolean, default=False)
    parent_qa_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("interview_qa_records.id"),
        nullable=True
    )
    
    # 关系
    session: Mapped["InterviewSession"] = relationship(
        "InterviewSession",
        back_populates="qa_records"
    )
