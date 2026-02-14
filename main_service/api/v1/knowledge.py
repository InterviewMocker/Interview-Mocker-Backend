"""
知识库API
"""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.database import get_db
from ...core.dependencies import get_current_user
from ...schemas.knowledge import (
    KnowledgeDocumentCreate, KnowledgeDocumentUpdate,
    KnowledgeDocumentResponse, KnowledgeDocumentDetailResponse
)
from ...schemas.common import ResponseModel, PaginatedResponse
from ...services.knowledge_service import KnowledgeDocumentService
from shared.models import User

router = APIRouter()


@router.get("/documents", response_model=ResponseModel[PaginatedResponse[KnowledgeDocumentResponse]])
async def list_documents(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    category: Optional[str] = None,
    doc_type: Optional[str] = None,
    status_filter: Optional[str] = Query(None, alias="status"),
    db: AsyncSession = Depends(get_db)
):
    """获取知识文档列表"""
    service = KnowledgeDocumentService(db)
    docs, total = await service.list(
        page=page,
        page_size=page_size,
        category=category,
        doc_type=doc_type,
        status=status_filter
    )
    
    return ResponseModel(
        message="获取成功",
        data=PaginatedResponse(
            items=[KnowledgeDocumentResponse.model_validate(d) for d in docs],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=(total + page_size - 1) // page_size
        )
    )


@router.post("/documents", response_model=ResponseModel[KnowledgeDocumentResponse])
async def create_document(
    doc_data: KnowledgeDocumentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """创建知识文档"""
    service = KnowledgeDocumentService(db)
    doc = await service.create(
        data=doc_data.model_dump(),
        created_by=current_user.id
    )
    
    return ResponseModel(
        message="创建成功",
        data=KnowledgeDocumentResponse.model_validate(doc)
    )


@router.get("/documents/{document_id}", response_model=ResponseModel[KnowledgeDocumentDetailResponse])
async def get_document(
    document_id: str,
    db: AsyncSession = Depends(get_db)
):
    """获取知识文档详情"""
    service = KnowledgeDocumentService(db)
    doc = await service.get_by_id(document_id)
    
    if not doc:
        raise HTTPException(status_code=404, detail="文档不存在")
    
    # 增加浏览次数
    await service.increment_view_count(document_id)
    
    return ResponseModel(
        message="获取成功",
        data=KnowledgeDocumentDetailResponse.model_validate(doc)
    )


@router.put("/documents/{document_id}", response_model=ResponseModel[KnowledgeDocumentResponse])
async def update_document(
    document_id: str,
    doc_data: KnowledgeDocumentUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """更新知识文档"""
    service = KnowledgeDocumentService(db)
    doc = await service.update(
        doc_id=document_id,
        data=doc_data.model_dump(exclude_unset=True)
    )
    
    if not doc:
        raise HTTPException(status_code=404, detail="文档不存在")
    
    return ResponseModel(
        message="更新成功",
        data=KnowledgeDocumentResponse.model_validate(doc)
    )


@router.delete("/documents/{document_id}", response_model=ResponseModel)
async def delete_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """删除知识文档"""
    service = KnowledgeDocumentService(db)
    success = await service.delete(document_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="文档不存在")
    
    return ResponseModel(message="删除成功")


@router.post("/documents/{document_id}/vectorize", response_model=ResponseModel)
async def vectorize_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """触发文档向量化"""
    # TODO: 实现文档向量化
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="向量化功能开发中"
    )


@router.post("/search", response_model=ResponseModel)
async def search_knowledge(
    query: str,
    position_id: Optional[str] = None,
    category: Optional[str] = None,
    top_k: int = 5,
    db: AsyncSession = Depends(get_db)
):
    """知识库语义检索"""
    # TODO: 实现RAG检索
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="语义检索功能开发中"
    )
