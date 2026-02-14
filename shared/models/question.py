"""
题库相关数据模型
"""
from typing import Optional
from decimal import Decimal

from sqlalchemy import String, Integer, Text, JSON, DECIMAL, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, TimestampMixin, SoftDeleteMixin, generate_uuid


class Question(Base, TimestampMixin, SoftDeleteMixin):
    """题目表"""
    __tablename__ = "questions"
    
    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=generate_uuid
    )
    
    # 题目内容
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    
    # 题目分类
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    category: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # 难度
    difficulty: Mapped[str] = mapped_column(String(20), nullable=False)
    difficulty_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # 标签
    tags: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # 参考答案
    reference_answer: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    answer_key_points: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # 评分标准
    scoring_criteria: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # 追问题目
    follow_up_questions: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # 统计数据
    usage_count: Mapped[int] = mapped_column(Integer, default=0)
    avg_score: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(5, 2), nullable=True)
    
    # 状态
    status: Mapped[str] = mapped_column(String(20), default="active")
    
    # 创建者
    created_by: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("users.id"),
        nullable=True
    )


class PositionQuestion(Base):
    """岗位题目关联表"""
    __tablename__ = "position_questions"
    
    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=generate_uuid
    )
    position_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("positions.id", ondelete="CASCADE"),
        nullable=False
    )
    question_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("questions.id", ondelete="CASCADE"),
        nullable=False
    )
    
    # 关联权重
    weight: Mapped[Decimal] = mapped_column(DECIMAL(5, 2), default=1.0)
    priority: Mapped[int] = mapped_column(Integer, default=5)
    
    # 出现频率控制
    frequency_limit: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
