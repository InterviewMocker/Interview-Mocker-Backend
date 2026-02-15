"""
题库和题目管理服务
"""
from typing import Optional, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from shared.models import QuestionBank, Question


class QuestionBankService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, data: dict, created_by: Optional[str] = None) -> QuestionBank:
        """创建题库"""
        bank = QuestionBank(**data, created_by=created_by)
        self.db.add(bank)
        await self.db.commit()
        await self.db.refresh(bank)
        return bank
    
    async def get_by_id(self, bank_id: str) -> Optional[QuestionBank]:
        """根据ID获取题库"""
        result = await self.db.execute(
            select(QuestionBank).where(
                QuestionBank.id == bank_id,
                QuestionBank.deleted_at == None
            )
        )
        return result.scalar_one_or_none()
    
    async def list(
        self,
        page: int = 1,
        page_size: int = 20,
        category: Optional[str] = None,
        status: Optional[str] = None
    ) -> Tuple[List[QuestionBank], int]:
        """获取题库列表"""
        query = select(QuestionBank).where(QuestionBank.deleted_at == None)
        
        if category:
            query = query.where(QuestionBank.category == category)
        if status:
            query = query.where(QuestionBank.status == status)
        
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        query = query.order_by(QuestionBank.created_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)
        
        result = await self.db.execute(query)
        banks = result.scalars().all()
        
        return list(banks), total
    
    async def update(self, bank_id: str, data: dict) -> Optional[QuestionBank]:
        """更新题库"""
        bank = await self.get_by_id(bank_id)
        if not bank:
            return None
        
        for key, value in data.items():
            if value is not None:
                setattr(bank, key, value)
        
        await self.db.commit()
        await self.db.refresh(bank)
        return bank
    
    async def delete(self, bank_id: str) -> bool:
        """软删除题库"""
        bank = await self.get_by_id(bank_id)
        if not bank:
            return False
        
        from datetime import datetime
        bank.deleted_at = datetime.utcnow()
        await self.db.commit()
        return True


class QuestionService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, data: dict, created_by: Optional[str] = None) -> Question:
        """创建题目"""
        question = Question(**data, created_by=created_by)
        self.db.add(question)
        await self.db.commit()
        await self.db.refresh(question)
        return question
    
    async def batch_create(self, items: list, bank_id: str, created_by: Optional[str] = None) -> List[Question]:
        """批量创建题目"""
        questions = []
        for item in items:
            data = {**item, "bank_id": bank_id}
            question = Question(**data, created_by=created_by)
            self.db.add(question)
            questions.append(question)
        await self.db.commit()
        for q in questions:
            await self.db.refresh(q)
        return questions

    async def get_by_id(self, question_id: str) -> Optional[Question]:
        """根据ID获取题目"""
        result = await self.db.execute(
            select(Question).where(
                Question.id == question_id,
                Question.deleted_at == None
            )
        )
        return result.scalar_one_or_none()
    
    async def list(
        self,
        page: int = 1,
        page_size: int = 20,
        bank_id: Optional[str] = None,
        category: Optional[str] = None,
        difficulty: Optional[str] = None,
        question_type: Optional[str] = None,
        status: Optional[str] = None
    ) -> Tuple[List[Question], int]:
        """获取题目列表"""
        query = select(Question).where(Question.deleted_at == None)
        
        if bank_id:
            query = query.where(Question.bank_id == bank_id)
        if category:
            query = query.where(Question.category == category)
        if difficulty:
            query = query.where(Question.difficulty == difficulty)
        if question_type:
            query = query.where(Question.type == question_type)
        if status:
            query = query.where(Question.status == status)
        
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        query = query.order_by(Question.created_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)
        
        result = await self.db.execute(query)
        questions = result.scalars().all()
        
        return list(questions), total
    
    async def update(self, question_id: str, data: dict) -> Optional[Question]:
        """更新题目"""
        question = await self.get_by_id(question_id)
        if not question:
            return None
        
        for key, value in data.items():
            if value is not None:
                setattr(question, key, value)
        
        await self.db.commit()
        await self.db.refresh(question)
        return question
    
    async def delete(self, question_id: str) -> bool:
        """软删除题目"""
        question = await self.get_by_id(question_id)
        if not question:
            return False
        
        from datetime import datetime
        question.deleted_at = datetime.utcnow()
        await self.db.commit()
        return True
