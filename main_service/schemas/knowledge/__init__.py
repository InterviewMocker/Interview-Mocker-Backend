"""
知识库相关 Schema
"""
from .knowledge import (
    KnowledgeDocumentCreate, KnowledgeDocumentUpdate,
    KnowledgeDocumentResponse, KnowledgeDocumentDetailResponse,
)

__all__ = [
    "KnowledgeDocumentCreate", "KnowledgeDocumentUpdate",
    "KnowledgeDocumentResponse", "KnowledgeDocumentDetailResponse",
]
