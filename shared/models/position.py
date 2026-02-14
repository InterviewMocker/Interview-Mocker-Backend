"""
岗位相关数据模型
"""
from typing import Optional

from sqlalchemy import String, Integer, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin, SoftDeleteMixin, generate_uuid


class Position(Base, TimestampMixin, SoftDeleteMixin):
    """岗位表"""
    __tablename__ = "positions"
    
    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=generate_uuid
    )
    
    # 基本信息
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    category: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # 岗位描述
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    requirements: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # 技能要求
    required_skills: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    skill_weights: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # 难度级别
    difficulty_level: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    
    # 关联配置
    default_question_count: Mapped[int] = mapped_column(Integer, default=10)
    default_duration: Mapped[int] = mapped_column(Integer, default=30)
    
    # 状态
    status: Mapped[str] = mapped_column(String(20), default="active")
    
    # 关系
    knowledge_points: Mapped[list["PositionKnowledgePoint"]] = relationship(
        "PositionKnowledgePoint",
        back_populates="position"
    )


class PositionKnowledgePoint(Base, TimestampMixin):
    """岗位知识点表"""
    __tablename__ = "position_knowledge_points"
    
    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=generate_uuid
    )
    position_id: Mapped[str] = mapped_column(
        String(36),
        nullable=False
    )
    
    # 知识点信息
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    category: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # 重要程度
    importance: Mapped[int] = mapped_column(Integer, default=5)
    
    # 关联资源
    related_docs: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # 关系
    position: Mapped["Position"] = relationship(
        "Position",
        back_populates="knowledge_points",
        foreign_keys=[position_id]
    )
