"""
知识文档相关Pydantic模型
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class KnowledgeDocumentCreate(BaseModel):
    """创建知识文档请求"""
    title: str = Field(..., max_length=200)
    content: str
    summary: Optional[str] = None
    doc_type: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    related_positions: Optional[List[str]] = Field(default=None, description="关联岗位ID列表")
    difficulty: Optional[str] = None


class KnowledgeDocumentUpdate(BaseModel):
    """更新知识文档请求"""
    title: Optional[str] = None
    content: Optional[str] = None
    summary: Optional[str] = None
    doc_type: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    related_positions: Optional[List[str]] = None
    difficulty: Optional[str] = None
    status: Optional[str] = None


class KnowledgeDocumentResponse(BaseModel):
    """知识文档响应"""
    id: str
    title: str
    summary: Optional[str] = None
    doc_type: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    related_positions: Optional[List[str]] = None
    difficulty: Optional[str] = None
    vectorized: bool = False
    chunk_count: int = 0
    view_count: int = 0
    reference_count: int = 0
    status: str
    created_by: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class KnowledgeDocumentDetailResponse(KnowledgeDocumentResponse):
    """知识文档详情响应（包含内容）"""
    content: str
