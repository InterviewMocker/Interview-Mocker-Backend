"""
题库和题目管理API
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.database import get_db
from ...core.dependencies import get_current_user
from ...schemas.question import (
    QuestionBankCreate, QuestionBankUpdate, QuestionBankResponse,
    QuestionCreate, QuestionUpdate, QuestionResponse, QuestionDetailResponse
)
from ...schemas.common import ResponseModel, PaginatedResponse
from ...services.question_service import QuestionBankService, QuestionService
from shared.models import User

router = APIRouter()


# ==================== 题库 API ====================

@router.get("/banks", response_model=ResponseModel[PaginatedResponse[QuestionBankResponse]])
async def list_question_banks(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    category: Optional[str] = None,
    status_filter: Optional[str] = Query(None, alias="status"),
    db: AsyncSession = Depends(get_db)
):
    """获取题库列表"""
    service = QuestionBankService(db)
    banks, total = await service.list(
        page=page,
        page_size=page_size,
        category=category,
        status=status_filter
    )
    
    return ResponseModel(
        message="获取成功",
        data=PaginatedResponse(
            items=[QuestionBankResponse.model_validate(b) for b in banks],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=(total + page_size - 1) // page_size
        )
    )


@router.post("/banks", response_model=ResponseModel[QuestionBankResponse])
async def create_question_bank(
    bank_data: QuestionBankCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """创建题库"""
    service = QuestionBankService(db)
    
    bank = await service.create(
        data=bank_data.model_dump(),
        created_by=current_user.id
    )
    
    return ResponseModel(
        message="创建成功",
        data=QuestionBankResponse.model_validate(bank)
    )


@router.get("/banks/{bank_id}", response_model=ResponseModel[QuestionBankResponse])
async def get_question_bank(
    bank_id: str,
    db: AsyncSession = Depends(get_db)
):
    """获取题库详情"""
    service = QuestionBankService(db)
    bank = await service.get_by_id(bank_id)
    
    if not bank:
        raise HTTPException(status_code=404, detail="题库不存在")
    
    return ResponseModel(
        message="获取成功",
        data=QuestionBankResponse.model_validate(bank)
    )


@router.put("/banks/{bank_id}", response_model=ResponseModel[QuestionBankResponse])
async def update_question_bank(
    bank_id: str,
    bank_data: QuestionBankUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """更新题库"""
    service = QuestionBankService(db)
    bank = await service.update(
        bank_id=bank_id,
        data=bank_data.model_dump(exclude_unset=True)
    )
    
    if not bank:
        raise HTTPException(status_code=404, detail="题库不存在")
    
    return ResponseModel(
        message="更新成功",
        data=QuestionBankResponse.model_validate(bank)
    )


@router.delete("/banks/{bank_id}", response_model=ResponseModel)
async def delete_question_bank(
    bank_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """删除题库"""
    service = QuestionBankService(db)
    success = await service.delete(bank_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="题库不存在")
    
    return ResponseModel(message="删除成功")


# ==================== 题目 API ====================

@router.get("", response_model=ResponseModel[PaginatedResponse[QuestionResponse]])
async def list_questions(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    bank_id: Optional[str] = None,
    question_type: Optional[str] = Query(None, alias="type"),
    category: Optional[str] = None,
    difficulty: Optional[str] = None,
    status_filter: Optional[str] = Query(None, alias="status"),
    db: AsyncSession = Depends(get_db)
):
    """获取题目列表"""
    service = QuestionService(db)
    questions, total = await service.list(
        page=page,
        page_size=page_size,
        bank_id=bank_id,
        category=category,
        difficulty=difficulty,
        question_type=question_type,
        status=status_filter
    )
    
    return ResponseModel(
        message="获取成功",
        data=PaginatedResponse(
            items=[QuestionResponse.model_validate(q) for q in questions],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=(total + page_size - 1) // page_size
        )
    )


@router.post("", response_model=ResponseModel[QuestionResponse])
async def create_question(
    question_data: QuestionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """创建题目"""
    # 验证题库存在
    bank_service = QuestionBankService(db)
    bank = await bank_service.get_by_id(question_data.bank_id)
    if not bank:
        raise HTTPException(status_code=400, detail="所属题库不存在")
    
    service = QuestionService(db)
    question = await service.create(
        data=question_data.model_dump(),
        created_by=current_user.id
    )
    
    return ResponseModel(
        message="创建成功",
        data=QuestionResponse.model_validate(question)
    )


@router.get("/{question_id}", response_model=ResponseModel[QuestionDetailResponse])
async def get_question(
    question_id: str,
    db: AsyncSession = Depends(get_db)
):
    """获取题目详情"""
    service = QuestionService(db)
    question = await service.get_by_id(question_id)
    
    if not question:
        raise HTTPException(status_code=404, detail="题目不存在")
    
    return ResponseModel(
        message="获取成功",
        data=QuestionDetailResponse.model_validate(question)
    )


@router.put("/{question_id}", response_model=ResponseModel[QuestionResponse])
async def update_question(
    question_id: str,
    question_data: QuestionUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """更新题目"""
    service = QuestionService(db)
    question = await service.update(
        question_id=question_id,
        data=question_data.model_dump(exclude_unset=True)
    )
    
    if not question:
        raise HTTPException(status_code=404, detail="题目不存在")
    
    return ResponseModel(
        message="更新成功",
        data=QuestionResponse.model_validate(question)
    )


@router.delete("/{question_id}", response_model=ResponseModel)
async def delete_question(
    question_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """删除题目"""
    service = QuestionService(db)
    success = await service.delete(question_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="题目不存在")
    
    return ResponseModel(message="删除成功")
