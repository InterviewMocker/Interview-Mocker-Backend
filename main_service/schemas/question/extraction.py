"""
题目提取相关 Pydantic 模型
"""
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ExtractionTaskResponse(BaseModel):
    """提取任务状态响应"""
    task_id: str
    filename: str
    bank_id: str
    status: str = Field(..., description="pending | processing | completed | failed")
    total_chunks: int
    processed_chunks: int
    progress: float = Field(..., description="进度百分比 0-100")
    questions: List[Dict[str, Any]] = []
    error: Optional[str] = None
    created_at: float
    updated_at: float


class ExtractionTaskListItem(BaseModel):
    """任务列表项（不包含完整题目数据）"""
    task_id: str
    filename: str
    bank_id: str
    status: str
    total_chunks: int
    processed_chunks: int
    progress: float
    total_questions: int = 0
    error: Optional[str] = None
    created_at: float
    updated_at: float


class ExtractedQuestionItem(BaseModel):
    """提取出的单道题目"""
    title: str = Field(..., max_length=200)
    content: str
    type: str = Field(..., description="technical|scenario|algorithm|behavioral")
    category: Optional[str] = None
    difficulty: str = Field(..., description="easy|medium|hard")
    difficulty_score: Optional[int] = Field(None, ge=1, le=10)
    tags: Optional[List[str]] = None
    reference_answer: Optional[str] = None
    answer_key_points: Optional[List[str]] = None


class BatchImportRequest(BaseModel):
    """批量导入题目到题库请求"""
    task_id: str = Field(..., description="提取任务ID")
    bank_id: str = Field(..., description="目标题库ID")
    question_indices: Optional[List[int]] = Field(
        None, description="要导入的题目索引列表，为空则导入全部"
    )
