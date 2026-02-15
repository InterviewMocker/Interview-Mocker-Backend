"""
岗位管理服务
"""
from typing import Optional, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from shared.models import Position, User


class PositionService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, data: dict, created_by: Optional[str] = None) -> Position:
        """创建岗位"""
        position = Position(**data, created_by=created_by)
        self.db.add(position)
        await self.db.commit()
        await self.db.refresh(position)
        return position
    
    async def get_by_id(self, position_id: str) -> Optional[Position]:
        """根据ID获取岗位"""
        result = await self.db.execute(
            select(Position).where(
                Position.id == position_id,
                Position.deleted_at == None
            )
        )
        return result.scalar_one_or_none()
    
    async def get_by_code(self, code: str) -> Optional[Position]:
        """根据编码获取岗位"""
        result = await self.db.execute(
            select(Position).where(
                Position.code == code,
                Position.deleted_at == None
            )
        )
        return result.scalar_one_or_none()
    
    async def list(
        self,
        page: int = 1,
        page_size: int = 20,
        category: Optional[str] = None,
        status: Optional[str] = None
    ) -> Tuple[List[Position], int]:
        """获取岗位列表"""
        query = select(Position).where(Position.deleted_at == None)
        
        if category:
            query = query.where(Position.category == category)
        if status:
            query = query.where(Position.status == status)
        
        # 统计总数
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        # 分页查询
        query = query.order_by(Position.created_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)
        
        result = await self.db.execute(query)
        positions = result.scalars().all()
        
        return list(positions), total
    
    async def update(self, position_id: str, data: dict) -> Optional[Position]:
        """更新岗位"""
        position = await self.get_by_id(position_id)
        if not position:
            return None
        
        for key, value in data.items():
            if value is not None:
                setattr(position, key, value)
        
        await self.db.commit()
        await self.db.refresh(position)
        return position
    
    async def delete(self, position_id: str) -> bool:
        """软删除岗位"""
        position = await self.get_by_id(position_id)
        if not position:
            return False
        
        from datetime import datetime
        position.deleted_at = datetime.utcnow()
        await self.db.commit()
        return True
