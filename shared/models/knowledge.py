"""
知识库相关数据模型
"""
from typing import Optional

from sqlalchemy import String, Integer, Text, JSON, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin, SoftDeleteMixin, generate_uuid


class KnowledgeDocument(Base, TimestampMixin, SoftDeleteMixin):
    """知识文档表"""
    __tablename__ = "knowledge_documents"
    
    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=generate_uuid
    )
    
    # 文档信息
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # 文档类型
    doc_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # 分类标签
    category: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    tags: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # 关联岗位
    related_positions: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # 难度级别
    difficulty: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    
    # 原始文件信息
    original_filename: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    file_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    file_type: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    
    # 向量化状态
    vectorized: Mapped[bool] = mapped_column(Boolean, default=False)
    vector_ids: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    chunk_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # 质量评分
    quality_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # 统计数据
    view_count: Mapped[int] = mapped_column(Integer, default=0)
    reference_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # 状态
    status: Mapped[str] = mapped_column(String(20), default="active")
    
    # 创建者
    created_by: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("users.id"),
        nullable=True
    )
    
    # 关系
    chunks: Mapped[list["DocumentChunk"]] = relationship(
        "DocumentChunk",
        back_populates="document"
    )


class DocumentChunk(Base):
    """文档分块表"""
    __tablename__ = "document_chunks"
    
    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=generate_uuid
    )
    
    # 关联文档
    document_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("knowledge_documents.id", ondelete="CASCADE"),
        nullable=False
    )
    
    # 分块信息
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    chunk_text: Mapped[str] = mapped_column(Text, nullable=False)
    chunk_size: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # 向量信息
    vector_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # 元数据
    chunk_metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # 关系
    document: Mapped["KnowledgeDocument"] = relationship(
        "KnowledgeDocument",
        back_populates="chunks"
    )
