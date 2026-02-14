"""
岗位管理API
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.database import get_db
from ...core.dependencies import get_current_user
from ...schemas.position import PositionCreate, PositionUpdate, PositionResponse
from ...schemas.common import ResponseModel, PaginatedResponse
from shared.models import User

router = APIRouter()


@router.get("", response_model=ResponseModel[PaginatedResponse[PositionResponse]])
async def list_positions(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    category: Optional[str] = None,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """获取岗位列表"""
    # TODO: 实现岗位列表查询
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="功能开发中"
    )


@router.post("", response_model=ResponseModel[PositionResponse])
async def create_position(
    position_data: PositionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """创建岗位"""
    # TODO: 实现创建岗位
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="功能开发中"
    )


@router.get("/{position_id}", response_model=ResponseModel[PositionResponse])
async def get_position(
    position_id: str,
    db: AsyncSession = Depends(get_db)
):
    """获取岗位详情"""
    # TODO: 实现获取岗位详情
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="功能开发中"
    )


@router.put("/{position_id}", response_model=ResponseModel[PositionResponse])
async def update_position(
    position_id: str,
    position_data: PositionUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """更新岗位"""
    # TODO: 实现更新岗位
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="功能开发中"
    )


@router.delete("/{position_id}", response_model=ResponseModel)
async def delete_position(
    position_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """删除岗位"""
    # TODO: 实现删除岗位
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="功能开发中"
    )
