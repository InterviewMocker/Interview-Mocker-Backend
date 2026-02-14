"""
题库管理API
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.database import get_db
from ...core.dependencies import get_current_user
from ...schemas.question import QuestionCreate, QuestionUpdate, QuestionResponse, QuestionDetailResponse
from ...schemas.common import ResponseModel, PaginatedResponse
from shared.models import User

router = APIRouter()


@router.get("", response_model=ResponseModel[PaginatedResponse[QuestionResponse]])
async def list_questions(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    type: Optional[str] = None,
    category: Optional[str] = None,
    difficulty: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """获取题目列表"""
    # TODO: 实现题目列表查询
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="功能开发中"
    )


@router.post("", response_model=ResponseModel[QuestionResponse])
async def create_question(
    question_data: QuestionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """创建题目"""
    # TODO: 实现创建题目
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="功能开发中"
    )


@router.get("/{question_id}", response_model=ResponseModel[QuestionDetailResponse])
async def get_question(
    question_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取题目详情"""
    # TODO: 实现获取题目详情
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="功能开发中"
    )


@router.put("/{question_id}", response_model=ResponseModel[QuestionResponse])
async def update_question(
    question_id: str,
    question_data: QuestionUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """更新题目"""
    # TODO: 实现更新题目
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="功能开发中"
    )


@router.delete("/{question_id}", response_model=ResponseModel)
async def delete_question(
    question_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """删除题目"""
    # TODO: 实现删除题目
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="功能开发中"
    )


@router.post("/next", response_model=ResponseModel[QuestionResponse])
async def get_next_question(
    session_id: str,
    context: Optional[dict] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取下一个面试题目（供AI数字人微服务调用）"""
    # TODO: 实现智能选题
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="功能开发中"
    )
