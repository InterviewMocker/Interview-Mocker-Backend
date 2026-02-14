"""
评估报告相关数据模型
"""
from typing import Optional
from decimal import Decimal

from sqlalchemy import String, Integer, Text, JSON, DECIMAL, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, TimestampMixin, generate_uuid


class EvaluationReport(Base, TimestampMixin):
    """评估报告表"""
    __tablename__ = "evaluation_reports"
    
    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=generate_uuid
    )
    
    # 关联信息
    session_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("interview_sessions.id", ondelete="CASCADE"),
        unique=True,
        nullable=False
    )
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
    
    # 综合评分
    overall_score: Mapped[Decimal] = mapped_column(DECIMAL(5, 2), nullable=False)
    
    # 多维度评分
    technical_score: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(5, 2), nullable=True)
    expression_score: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(5, 2), nullable=True)
    logic_score: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(5, 2), nullable=True)
    depth_score: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(5, 2), nullable=True)
    breadth_score: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(5, 2), nullable=True)
    
    # 能力雷达图数据
    radar_chart_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # 详细分析
    strengths: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    weaknesses: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    improvement_suggestions: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # 知识点掌握情况
    knowledge_mastery: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # 对比数据
    percentile_rank: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    compared_to_average: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # 报告内容
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    detailed_analysis: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # 报告状态
    status: Mapped[str] = mapped_column(String(20), default="generated")


class ImprovementPlan(Base, TimestampMixin):
    """能力提升建议表"""
    __tablename__ = "improvement_plans"
    
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
    report_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("evaluation_reports.id", ondelete="SET NULL"),
        nullable=True
    )
    
    # 薄弱点
    weak_points: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # 学习路径
    learning_path: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # 推荐资源
    recommended_docs: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    recommended_questions: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    recommended_courses: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # 目标设定
    target_skills: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    target_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    estimated_days: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # 进度跟踪
    progress: Mapped[Decimal] = mapped_column(DECIMAL(5, 2), default=0)
    status: Mapped[str] = mapped_column(String(20), default="active")
