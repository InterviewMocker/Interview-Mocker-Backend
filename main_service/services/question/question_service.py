"""
题库和题目管理服务
"""
from datetime import datetime
from typing import Optional, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

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
        """根据ID获取题库（不做归属校验）"""
        result = await self.db.execute(
            select(QuestionBank).options(selectinload(QuestionBank.creator)).where(
                QuestionBank.id == bank_id,
                QuestionBank.deleted_at == None
            )
        )
        return result.scalar_one_or_none()
    
    async def get_own_bank(self, bank_id: str, user_id: str) -> Optional[QuestionBank]:
        """获取当前用户拥有的题库"""
        result = await self.db.execute(
            select(QuestionBank).options(selectinload(QuestionBank.creator)).where(
                QuestionBank.id == bank_id,
                QuestionBank.created_by == user_id,
                QuestionBank.deleted_at == None
            )
        )
        return result.scalar_one_or_none()
    
    async def get_accessible_bank(self, bank_id: str, user_id: str) -> Optional[QuestionBank]:
        """获取用户可访问的题库（自己的 或 社区已上架的）"""
        result = await self.db.execute(
            select(QuestionBank).options(selectinload(QuestionBank.creator)).where(
                QuestionBank.id == bank_id,
                QuestionBank.deleted_at == None
            )
        )
        bank = result.scalar_one_or_none()
        if not bank:
            return None
        if bank.created_by == user_id or bank.community_status == "approved":
            return bank
        return None
    
    async def list_my_banks(
        self,
        user_id: str,
        page: int = 1,
        page_size: int = 20,
        category: Optional[str] = None,
        status: Optional[str] = None
    ) -> Tuple[List[QuestionBank], int]:
        """获取当前用户的题库列表"""
        query = select(QuestionBank).options(selectinload(QuestionBank.creator)).where(
            QuestionBank.created_by == user_id,
            QuestionBank.deleted_at == None
        )
        
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
    
    async def list_community_banks(
        self,
        page: int = 1,
        page_size: int = 20,
        category: Optional[str] = None,
    ) -> Tuple[List[QuestionBank], int]:
        """获取社区题库列表（仅 approved）"""
        query = select(QuestionBank).options(selectinload(QuestionBank.creator)).where(
            QuestionBank.community_status == "approved",
            QuestionBank.deleted_at == None
        )
        
        if category:
            query = query.where(QuestionBank.category == category)
        
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        query = query.order_by(QuestionBank.created_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)
        
        result = await self.db.execute(query)
        banks = result.scalars().all()
        
        return list(banks), total
    
    async def list_pending_banks(
        self,
        page: int = 1,
        page_size: int = 20,
    ) -> Tuple[List[QuestionBank], int]:
        """管理员获取待审核题库列表"""
        query = select(QuestionBank).options(selectinload(QuestionBank.creator)).where(
            QuestionBank.community_status == "pending",
            QuestionBank.deleted_at == None
        )
        
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        query = query.order_by(QuestionBank.created_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)
        
        result = await self.db.execute(query)
        banks = result.scalars().all()
        
        return list(banks), total
    
    async def update(self, bank_id: str, user_id: str, data: dict) -> Optional[QuestionBank]:
        """更新题库（校验归属，若 approved 则自动下架）"""
        bank = await self.get_own_bank(bank_id, user_id)
        if not bank:
            return None
        
        for key, value in data.items():
            if value is not None:
                setattr(bank, key, value)
        
        # 修改已上架题库时自动下架
        if bank.community_status == "approved":
            bank.community_status = None
        
        await self.db.commit()
        await self.db.refresh(bank)
        return bank
    
    async def delete(self, bank_id: str, user_id: str) -> bool:
        """软删除题库（校验归属）"""
        bank = await self.get_own_bank(bank_id, user_id)
        if not bank:
            return False
        
        bank.deleted_at = datetime.utcnow()
        await self.db.commit()
        return True
    
    async def apply_community(self, bank_id: str, user_id: str) -> Optional[QuestionBank]:
        """申请上架社区（null/rejected → pending）"""
        bank = await self.get_own_bank(bank_id, user_id)
        if not bank:
            return None
        
        if bank.community_status in ("pending", "approved"):
            return bank
        
        bank.community_status = "pending"
        await self.db.commit()
        await self.db.refresh(bank)
        return bank
    
    async def review_community(self, bank_id: str, action: str) -> Optional[QuestionBank]:
        """管理员审核社区题库（approve/reject/delist）"""
        bank = await self.get_by_id(bank_id)
        if not bank:
            return None
        
        if action == "approve" and bank.community_status == "pending":
            bank.community_status = "approved"
        elif action == "reject" and bank.community_status == "pending":
            bank.community_status = "rejected"
        elif action == "delist" and bank.community_status == "approved":
            bank.community_status = None
        else:
            return bank
        
        await self.db.commit()
        await self.db.refresh(bank)
        return bank
    
    async def copy_community_bank(self, bank_id: str, user_id: str) -> Optional[QuestionBank]:
        """深拷贝社区题库到用户自己的题库"""
        # 加载题库及其题目
        result = await self.db.execute(
            select(QuestionBank)
            .options(selectinload(QuestionBank.questions))
            .where(
                QuestionBank.id == bank_id,
                QuestionBank.community_status == "approved",
                QuestionBank.deleted_at == None
            )
        )
        source_bank = result.scalar_one_or_none()
        if not source_bank:
            return None
        
        # 创建新题库
        new_bank = QuestionBank(
            name=source_bank.name,
            description=source_bank.description,
            category=source_bank.category,
            tags=source_bank.tags,
            status="active",
            community_status=None,
            created_by=user_id,
        )
        self.db.add(new_bank)
        await self.db.flush()
        
        # 深拷贝所有未删除的题目
        for q in source_bank.questions:
            if q.deleted_at is not None:
                continue
            new_q = Question(
                bank_id=new_bank.id,
                title=q.title,
                content=q.content,
                type=q.type,
                category=q.category,
                difficulty=q.difficulty,
                difficulty_score=q.difficulty_score,
                tags=q.tags,
                reference_answer=q.reference_answer,
                answer_key_points=q.answer_key_points,
                scoring_criteria=q.scoring_criteria,
                follow_up_questions=q.follow_up_questions,
                status="active",
                created_by=user_id,
            )
            self.db.add(new_q)
        
        await self.db.commit()
        await self.db.refresh(new_bank)
        return new_bank


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
        
        question.deleted_at = datetime.utcnow()
        await self.db.commit()
        return True
