"""
用户相关数据模型
"""
from datetime import datetime, date
from typing import Optional

from sqlalchemy import String, Boolean, Integer, Date, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin, SoftDeleteMixin, generate_uuid


class User(Base, TimestampMixin, SoftDeleteMixin):
    """用户表"""
    __tablename__ = "users"
    
    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=generate_uuid
    )
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String(100), unique=True, nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(20), unique=True, nullable=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # 用户信息
    real_name: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    avatar_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    gender: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    birth_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    school: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    major: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    graduation_year: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # 第三方登录预留字段
    wechat_openid: Mapped[Optional[str]] = mapped_column(String(100), unique=True, nullable=True)
    wechat_unionid: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    qq_openid: Mapped[Optional[str]] = mapped_column(String(100), unique=True, nullable=True)
    github_id: Mapped[Optional[str]] = mapped_column(String(100), unique=True, nullable=True)
    
    # 账号状态
    status: Mapped[str] = mapped_column(String(20), default="active")
    email_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    phone_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # 角色权限
    role: Mapped[str] = mapped_column(String(20), default="user")
    
    # 最后登录时间
    last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # 关系
    profile: Mapped[Optional["UserProfile"]] = relationship(
        "UserProfile",
        back_populates="user",
        uselist=False
    )
    login_logs: Mapped[list["UserLoginLog"]] = relationship(
        "UserLoginLog",
        back_populates="user"
    )


class UserProfile(Base, TimestampMixin):
    """用户画像表"""
    __tablename__ = "user_profiles"
    
    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=generate_uuid
    )
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False
    )
    
    # 目标岗位
    target_positions: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # 技能标签
    skill_tags: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # 能力评估
    technical_score: Mapped[int] = mapped_column(Integer, default=0)
    expression_score: Mapped[int] = mapped_column(Integer, default=0)
    logic_score: Mapped[int] = mapped_column(Integer, default=0)
    comprehensive_score: Mapped[int] = mapped_column(Integer, default=0)
    
    # 学习偏好
    preferred_difficulty: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    preferred_question_types: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # 统计数据
    total_interviews: Mapped[int] = mapped_column(Integer, default=0)
    total_questions_answered: Mapped[int] = mapped_column(Integer, default=0)
    total_study_hours: Mapped[int] = mapped_column(Integer, default=0)
    
    # 关系
    user: Mapped["User"] = relationship("User", back_populates="profile")


class UserLoginLog(Base):
    """用户登录日志表"""
    __tablename__ = "user_login_logs"
    
    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=generate_uuid
    )
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    
    login_type: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    device_type: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    
    login_status: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    failure_reason: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
    
    # 关系
    user: Mapped["User"] = relationship("User", back_populates="login_logs")
