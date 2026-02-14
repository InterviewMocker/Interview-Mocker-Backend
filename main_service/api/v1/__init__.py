"""
API v1 路由
"""
from fastapi import APIRouter

from .auth import router as auth_router
from .users import router as users_router
from .positions import router as positions_router
from .questions import router as questions_router
from .interviews import router as interviews_router
from .knowledge import router as knowledge_router
from .health import router as health_router

router = APIRouter()

router.include_router(health_router, tags=["健康检查"])
router.include_router(auth_router, prefix="/auth", tags=["认证授权"])
router.include_router(users_router, prefix="/users", tags=["用户管理"])
router.include_router(positions_router, prefix="/positions", tags=["岗位管理"])
router.include_router(questions_router, prefix="/questions", tags=["题库管理"])
router.include_router(interviews_router, prefix="/interviews", tags=["面试会话"])
router.include_router(knowledge_router, prefix="/knowledge", tags=["知识库"])
