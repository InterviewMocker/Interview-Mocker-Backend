"""
共享数据模型 - 两个服务共同使用
"""
from .base import Base, TimestampMixin, SoftDeleteMixin, generate_uuid
from .user import User, UserProfile, UserLoginLog
from .position import Position, PositionKnowledgePoint
from .question import Question, PositionQuestion
from .interview import InterviewSession, InterviewQARecord
from .evaluation import EvaluationReport, ImprovementPlan
from .knowledge import KnowledgeDocument, DocumentChunk
from .system import SystemConfig

__all__ = [
    # Base
    "Base",
    "TimestampMixin",
    "SoftDeleteMixin",
    "generate_uuid",
    # User
    "User",
    "UserProfile",
    "UserLoginLog",
    # Position
    "Position",
    "PositionKnowledgePoint",
    # Question
    "Question",
    "PositionQuestion",
    # Interview
    "InterviewSession",
    "InterviewQARecord",
    # Evaluation
    "EvaluationReport",
    "ImprovementPlan",
    # Knowledge
    "KnowledgeDocument",
    "DocumentChunk",
    # System
    "SystemConfig",
]
