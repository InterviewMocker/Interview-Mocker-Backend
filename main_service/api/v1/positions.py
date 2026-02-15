"""
岗位管理API
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.database import get_db
from ...core.dependencies import get_current_user
from ...schemas.position import PositionCreate, PositionUpdate, PositionResponse
from ...schemas.common import ResponseModel, PaginatedResponse
from ...services.position import PositionService
from shared.models import User

router = APIRouter()


@router.get("", response_model=ResponseModel[PaginatedResponse[PositionResponse]])
async def list_positions(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    category: Optional[str] = None,
    status_filter: Optional[str] = Query(None, alias="status"),
    db: AsyncSession = Depends(get_db)
):
    """获取岗位列表"""
    service = PositionService(db)
    positions, total = await service.list(
        page=page,
        page_size=page_size,
        category=category,
        status=status_filter
    )
    
    return ResponseModel(
        message="获取成功",
        data=PaginatedResponse(
            items=[PositionResponse.model_validate(p) for p in positions],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=(total + page_size - 1) // page_size
        )
    )


@router.post("", response_model=ResponseModel[PositionResponse])
async def create_position(
    position_data: PositionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """创建岗位"""
    service = PositionService(db)
    
    # 检查编码是否已存在
    existing = await service.get_by_code(position_data.code)
    if existing:
        raise HTTPException(status_code=400, detail="岗位编码已存在")
    
    position = await service.create(
        data=position_data.model_dump(),
        created_by=current_user.id
    )
    
    return ResponseModel(
        message="创建成功",
        data=PositionResponse.model_validate(position)
    )


@router.get("/{position_id}", response_model=ResponseModel[PositionResponse])
async def get_position(
    position_id: str,
    db: AsyncSession = Depends(get_db)
):
    """获取岗位详情"""
    service = PositionService(db)
    position = await service.get_by_id(position_id)
    
    if not position:
        raise HTTPException(status_code=404, detail="岗位不存在")
    
    return ResponseModel(
        message="获取成功",
        data=PositionResponse.model_validate(position)
    )


@router.put("/{position_id}", response_model=ResponseModel[PositionResponse])
async def update_position(
    position_id: str,
    position_data: PositionUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """更新岗位"""
    service = PositionService(db)
    position = await service.update(
        position_id=position_id,
        data=position_data.model_dump(exclude_unset=True)
    )
    
    if not position:
        raise HTTPException(status_code=404, detail="岗位不存在")
    
    return ResponseModel(
        message="更新成功",
        data=PositionResponse.model_validate(position)
    )


@router.delete("/{position_id}", response_model=ResponseModel)
async def delete_position(
    position_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """删除岗位"""
    service = PositionService(db)
    success = await service.delete(position_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="岗位不存在")
    
    return ResponseModel(message="删除成功")
