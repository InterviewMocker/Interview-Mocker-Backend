"""
系统配置数据模型
"""
from typing import Optional

from sqlalchemy import String, Text, JSON, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, TimestampMixin, generate_uuid


class SystemConfig(Base, TimestampMixin):
    """系统配置表"""
    __tablename__ = "system_configs"
    
    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=generate_uuid
    )
    
    config_key: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    config_value: Mapped[dict] = mapped_column(JSON, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    config_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    is_public: Mapped[bool] = mapped_column(Boolean, default=False)
