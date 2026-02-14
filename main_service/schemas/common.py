"""
通用响应模型
"""
from typing import Generic, TypeVar, Optional, List, Any
from pydantic import BaseModel

T = TypeVar("T")


class ResponseModel(BaseModel, Generic[T]):
    """统一响应格式"""
    code: int = 200
    message: str = "success"
    data: Optional[T] = None


class PaginatedResponse(BaseModel, Generic[T]):
    """分页响应格式"""
    items: List[T]
    total: int
    page: int
    page_size: int
    total_pages: int


class ErrorResponse(BaseModel):
    """错误响应"""
    code: int
    message: str
    detail: Optional[Any] = None
