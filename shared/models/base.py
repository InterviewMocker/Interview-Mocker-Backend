"""
共享数据模型基类
"""
from datetime import datetime
from typing import Optional
from uuid import uuid4

from sqlalchemy import DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


def generate_uuid() -> str:
    """生成 UUID 字符串"""
    return str(uuid4())


class Base(DeclarativeBase):
    """SQLAlchemy 声明式基类 - 两个服务共享"""
    pass


class TimestampMixin:
    """时间戳 Mixin"""
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )


class SoftDeleteMixin:
    """软删除 Mixin"""
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True
    )
