"""
LLM 调用异常定义
"""


class LLMError(Exception):
    """LLM 调用基础异常"""

    def __init__(self, message: str, provider: str = "", model: str = ""):
        self.provider = provider
        self.model = model
        super().__init__(message)


class LLMAuthenticationError(LLMError):
    """API Key 无效或缺失"""
    pass


class LLMRateLimitError(LLMError):
    """触发速率限制"""
    pass


class LLMConnectionError(LLMError):
    """网络连接错误"""
    pass


class LLMTimeoutError(LLMError):
    """请求超时"""
    pass


class LLMResponseError(LLMError):
    """响应解析或内容错误"""
    pass


class LLMInvalidRequestError(LLMError):
    """请求参数无效"""
    pass
