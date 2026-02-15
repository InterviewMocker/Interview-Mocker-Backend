"""
LLM 数据模型定义
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class Role(str, Enum):
    """消息角色"""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


@dataclass
class ChatMessage:
    """聊天消息"""
    role: Role
    content: str

    def to_dict(self) -> Dict[str, str]:
        return {"role": self.role.value, "content": self.content}

    @classmethod
    def system(cls, content: str) -> "ChatMessage":
        return cls(role=Role.SYSTEM, content=content)

    @classmethod
    def user(cls, content: str) -> "ChatMessage":
        return cls(role=Role.USER, content=content)

    @classmethod
    def assistant(cls, content: str) -> "ChatMessage":
        return cls(role=Role.ASSISTANT, content=content)


@dataclass
class LLMUsage:
    """Token 使用量"""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


@dataclass
class LLMResponse:
    """LLM 响应结果"""
    content: str
    model: str = ""
    usage: LLMUsage = field(default_factory=LLMUsage)
    finish_reason: str = ""
    raw_response: Optional[Dict[str, Any]] = None

    @property
    def is_complete(self) -> bool:
        return self.finish_reason == "stop"


@dataclass
class LLMStreamChunk:
    """流式响应块"""
    content: str = ""
    finish_reason: Optional[str] = None
    model: str = ""

    @property
    def is_final(self) -> bool:
        return self.finish_reason is not None


@dataclass
class LLMRequestOptions:
    """LLM 请求参数（覆盖默认配置）"""
    model: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    top_p: Optional[float] = None
    frequency_penalty: Optional[float] = None
    presence_penalty: Optional[float] = None
    stop: Optional[List[str]] = None
    response_format: Optional[Dict[str, str]] = None
