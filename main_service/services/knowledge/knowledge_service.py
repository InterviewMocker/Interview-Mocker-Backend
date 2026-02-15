"""
知识文档管理服务
"""
from typing import Optional, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from shared.models import KnowledgeDocument


class KnowledgeDocumentService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, data: dict, created_by: Optional[str] = None) -> KnowledgeDocument:
        """创建知识文档"""
        doc = KnowledgeDocument(**data, created_by=created_by)
        self.db.add(doc)
        await self.db.commit()
        await self.db.refresh(doc)
        return doc
    
    async def get_by_id(self, doc_id: str) -> Optional[KnowledgeDocument]:
        """根据ID获取知识文档"""
        result = await self.db.execute(
            select(KnowledgeDocument).where(
                KnowledgeDocument.id == doc_id,
                KnowledgeDocument.deleted_at == None
            )
        )
        return result.scalar_one_or_none()
    
    async def list(
        self,
        page: int = 1,
        page_size: int = 20,
        category: Optional[str] = None,
        doc_type: Optional[str] = None,
        status: Optional[str] = None
    ) -> Tuple[List[KnowledgeDocument], int]:
        """获取知识文档列表"""
        query = select(KnowledgeDocument).where(KnowledgeDocument.deleted_at == None)
        
        if category:
            query = query.where(KnowledgeDocument.category == category)
        if doc_type:
            query = query.where(KnowledgeDocument.doc_type == doc_type)
        if status:
            query = query.where(KnowledgeDocument.status == status)
        
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        query = query.order_by(KnowledgeDocument.created_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)
        
        result = await self.db.execute(query)
        docs = result.scalars().all()
        
        return list(docs), total
    
    async def update(self, doc_id: str, data: dict) -> Optional[KnowledgeDocument]:
        """更新知识文档"""
        doc = await self.get_by_id(doc_id)
        if not doc:
            return None
        
        for key, value in data.items():
            if value is not None:
                setattr(doc, key, value)
        
        await self.db.commit()
        await self.db.refresh(doc)
        return doc
    
    async def delete(self, doc_id: str) -> bool:
        """软删除知识文档"""
        from datetime import datetime
        doc = await self.get_by_id(doc_id)
        if not doc:
            return False
        
        doc.deleted_at = datetime.utcnow()
        await self.db.commit()
        return True
    
    async def increment_view_count(self, doc_id: str) -> None:
        """增加浏览次数"""
        doc = await self.get_by_id(doc_id)
        if doc:
            doc.view_count += 1
            await self.db.commit()
