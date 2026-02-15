"""
LLM 大模型调用工具模块

提供统一的大模型 API 调用入口，支持 OpenAI 兼容协议的所有服务商。

快速开始:
    from shared.utils.llm import LLMClient, ChatMessage, quick_chat

    # 方式1: 快速调用
    result = await quick_chat("你好")

    # 方式2: 客户端实例
    client = LLMClient()
    response = await client.chat("你好", system_prompt="你是面试官")

    # 方式3: 依赖注入
    from shared.utils.llm import get_llm_client
    client = get_llm_client()
"""
from .client import LLMClient, get_llm_client, quick_chat
from .exceptions import (
    LLMAuthenticationError,
    LLMConnectionError,
    LLMError,
    LLMInvalidRequestError,
    LLMRateLimitError,
    LLMResponseError,
    LLMTimeoutError,
)
from .models import (
    ChatMessage,
    LLMRequestOptions,
    LLMResponse,
    LLMStreamChunk,
    LLMUsage,
    Role,
)

__all__ = [
    # 客户端
    "LLMClient",
    "get_llm_client",
    "quick_chat",
    # 数据模型
    "ChatMessage",
    "Role",
    "LLMResponse",
    "LLMStreamChunk",
    "LLMUsage",
    "LLMRequestOptions",
    # 异常
    "LLMError",
    "LLMAuthenticationError",
    "LLMRateLimitError",
    "LLMConnectionError",
    "LLMTimeoutError",
    "LLMResponseError",
    "LLMInvalidRequestError",
]
