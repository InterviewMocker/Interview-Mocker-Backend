"""
数据模型模块 - 从共享模块导入
"""
from shared.models import (
    # Base
    Base,
    TimestampMixin,
    SoftDeleteMixin,
    generate_uuid,
    # User
    User,
    UserProfile,
    UserLoginLog,
    # Position
    Position,
    PositionKnowledgePoint,
    # Question
    Question,
    PositionQuestion,
    # Interview
    InterviewSession,
    InterviewQARecord,
    # Evaluation
    EvaluationReport,
    ImprovementPlan,
    # Knowledge
    KnowledgeDocument,
    DocumentChunk,
    # System
    SystemConfig,
)
