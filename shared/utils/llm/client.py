"""
LLM 客户端 - 支持 OpenAI 兼容 API（OpenAI / DeepSeek / Qwen / 本地模型等）

使用方式:
    from shared.utils.llm import LLMClient, ChatMessage

    # 基本调用
    client = LLMClient()
    response = await client.chat("你好，请介绍一下你自己")

    # 带系统提示词
    response = await client.chat(
        "分析这段代码",
        system_prompt="你是一位资深的代码审查专家"
    )

    # 多轮对话
    messages = [
        ChatMessage.system("你是面试官"),
        ChatMessage.user("请开始面试"),
        ChatMessage.assistant("好的，请先自我介绍一下"),
        ChatMessage.user("我叫张三，有3年Python开发经验"),
    ]
    response = await client.chat_with_messages(messages)

    # 流式输出
    async for chunk in client.chat_stream("写一篇关于AI的文章"):
        print(chunk.content, end="", flush=True)

    # JSON 模式
    response = await client.chat_json(
        "列出3种编程语言及其特点",
        system_prompt="返回JSON数组格式"
    )
"""
import asyncio
import json
import logging
from typing import AsyncGenerator, Dict, List, Optional, Union

import httpx

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
)

logger = logging.getLogger(__name__)


class LLMClient:
    """
    通用 LLM 客户端，支持所有 OpenAI 兼容 API。

    支持的服务商（通过配置 base_url）：
    - OpenAI:     https://api.openai.com/v1
    - DeepSeek:   https://api.deepseek.com/v1
    - 通义千问:    https://dashscope.aliyuncs.com/compatible-mode/v1
    - Moonshot:   https://api.moonshot.cn/v1
    - 本地 Ollama: http://localhost:11434/v1
    """

    DEFAULT_BASE_URL = "https://api.openai.com/v1"

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        timeout: Optional[int] = None,
        max_retries: Optional[int] = None,
    ):
        """
        初始化 LLM 客户端。
        
        未提供的参数将从应用配置（Settings）中读取。
        
        Args:
            api_key: API 密钥
            base_url: API 基础地址（用于支持不同服务商）
            model: 默认模型名称
            temperature: 默认温度参数
            max_tokens: 默认最大 token 数
            timeout: 请求超时时间（秒）
            max_retries: 最大重试次数
        """
        config = self._load_config()

        self.api_key = api_key or config.get("api_key", "")
        self.base_url = (base_url or config.get("base_url", "") or self.DEFAULT_BASE_URL).rstrip("/")
        self.default_model = model or config.get("model", "gpt-4")
        self.default_temperature = temperature if temperature is not None else config.get("temperature", 0.7)
        self.default_max_tokens = max_tokens or config.get("max_tokens", 2048)
        self.timeout = timeout or config.get("timeout", 120)
        self.max_retries = max_retries if max_retries is not None else config.get("max_retries", 3)

        self._client: Optional[httpx.AsyncClient] = None

    @staticmethod
    def _load_config() -> Dict:
        """从应用配置中加载 LLM 设置"""
        try:
            from main_service.core.config import settings
            return {
                "api_key": settings.openai_api_key or "",
                "base_url": settings.openai_base_url or "",
                "model": settings.llm_model,
                "temperature": settings.llm_temperature,
                "max_tokens": settings.llm_max_tokens,
                "timeout": settings.llm_timeout,
                "max_retries": settings.llm_max_retries,
            }
        except Exception:
            return {}

    @property
    def client(self) -> httpx.AsyncClient:
        """懒加载 HTTP 客户端"""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                timeout=httpx.Timeout(self.timeout, connect=10.0),
            )
        return self._client

    async def close(self):
        """关闭 HTTP 客户端"""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    # ======================== 核心 API ========================

    async def chat(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        options: Optional[LLMRequestOptions] = None,
    ) -> LLMResponse:
        """
        最简单的聊天接口 - 单轮对话。

        Args:
            prompt: 用户输入
            system_prompt: 系统提示词（可选）
            options: 请求参数覆盖（可选）

        Returns:
            LLMResponse
        """
        messages = []
        if system_prompt:
            messages.append(ChatMessage.system(system_prompt))
        messages.append(ChatMessage.user(prompt))
        return await self.chat_with_messages(messages, options=options)

    async def chat_with_messages(
        self,
        messages: List[ChatMessage],
        options: Optional[LLMRequestOptions] = None,
    ) -> LLMResponse:
        """
        多轮对话接口。

        Args:
            messages: 消息列表
            options: 请求参数覆盖（可选）

        Returns:
            LLMResponse
        """
        payload = self._build_payload(messages, stream=False, options=options)
        data = await self._request_with_retry(payload)
        return self._parse_response(data)

    async def chat_stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        options: Optional[LLMRequestOptions] = None,
    ) -> AsyncGenerator[LLMStreamChunk, None]:
        """
        流式单轮对话。

        Args:
            prompt: 用户输入
            system_prompt: 系统提示词（可选）
            options: 请求参数覆盖（可选）

        Yields:
            LLMStreamChunk
        """
        messages = []
        if system_prompt:
            messages.append(ChatMessage.system(system_prompt))
        messages.append(ChatMessage.user(prompt))
        async for chunk in self.chat_stream_with_messages(messages, options=options):
            yield chunk

    async def chat_stream_with_messages(
        self,
        messages: List[ChatMessage],
        options: Optional[LLMRequestOptions] = None,
    ) -> AsyncGenerator[LLMStreamChunk, None]:
        """
        流式多轮对话。

        Args:
            messages: 消息列表
            options: 请求参数覆盖（可选）

        Yields:
            LLMStreamChunk
        """
        payload = self._build_payload(messages, stream=True, options=options)

        try:
            async with self.client.stream(
                "POST",
                "/chat/completions",
                json=payload,
            ) as response:
                if response.status_code != 200:
                    body = await response.aread()
                    self._handle_error_status(response.status_code, body)

                line_count = 0
                async for line in response.aiter_lines():
                    line_count += 1
                    # 调试：打印原始行（前几行）
                    if line_count <= 5:
                        logger.info(f"[Stream] 原始行 {line_count}: {line[:200]}")
                    
                    if not line.startswith("data: "):
                        continue
                    data_str = line[6:].strip()
                    if data_str == "[DONE]":
                        logger.debug(f"[Stream] 收到 [DONE]，共 {line_count} 行")
                        return
                    try:
                        data = json.loads(data_str)
                        chunk = self._parse_stream_chunk(data)
                        if chunk.content or chunk.is_final:
                            yield chunk
                    except json.JSONDecodeError as e:
                        logger.warning(f"[Stream] JSON 解析失败: {e}, 数据: {data_str[:100]}")
                        continue
                
                logger.debug(f"[Stream] 流结束，共 {line_count} 行")

        except httpx.TimeoutException as e:
            raise LLMTimeoutError(f"流式请求超时: {e}", model=self.default_model)
        except httpx.ConnectError as e:
            raise LLMConnectionError(f"连接失败: {e}", model=self.default_model)
        except httpx.HTTPStatusError as e:
            raise LLMError(f"HTTP 状态错误: {e.response.status_code} - {e}", model=self.default_model)
        except httpx.ReadError as e:
            import traceback
            logger.error(f"[Stream] ReadError 详情: {e}")
            logger.error(f"[Stream] 堆栈:\n{traceback.format_exc()}")
            raise LLMConnectionError(f"读取响应失败: {type(e).__name__} - {e}", model=self.default_model)
        except Exception as e:
            # 捕获所有其他异常并提供详细信息
            import traceback
            error_type = type(e).__name__
            logger.error(f"[Stream] 未知异常: {error_type} - {e}")
            logger.error(f"[Stream] 堆栈:\n{traceback.format_exc()}")
            raise LLMError(f"流式请求异常 ({error_type}): {e}", model=self.default_model)

    async def chat_json(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        options: Optional[LLMRequestOptions] = None,
    ) -> Union[Dict, List]:
        """
        JSON 模式对话 - 强制返回 JSON 格式。

        Args:
            prompt: 用户输入
            system_prompt: 系统提示词（可选）
            options: 请求参数覆盖（可选）

        Returns:
            解析后的 JSON 对象
        """
        opts = options or LLMRequestOptions()
        opts.response_format = {"type": "json_object"}

        suffix = "\n请以JSON格式返回结果。"
        if system_prompt:
            system_prompt = system_prompt + suffix
        else:
            system_prompt = "你是一个有帮助的助手。" + suffix

        response = await self.chat(prompt, system_prompt=system_prompt, options=opts)
        content = self._strip_markdown_fences(response.content)

        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            raise LLMResponseError(
                f"LLM 返回的内容不是有效 JSON: {e}\n原始内容: {response.content[:500]}",
                model=response.model,
            )

    async def chat_with_template(
        self,
        template: str,
        variables: Dict[str, str],
        system_prompt: Optional[str] = None,
        options: Optional[LLMRequestOptions] = None,
    ) -> LLMResponse:
        """
        模板化调用 - 使用变量填充提示词模板。

        Args:
            template: 提示词模板，使用 {variable_name} 占位符
            variables: 变量字典
            system_prompt: 系统提示词（可选）
            options: 请求参数覆盖（可选）

        Returns:
            LLMResponse

        Example:
            response = await client.chat_with_template(
                template="请分析以下{language}代码:\n```\n{code}\n```",
                variables={"language": "Python", "code": "print('hello')"},
                system_prompt="你是代码审查专家"
            )
        """
        try:
            prompt = template.format(**variables)
        except KeyError as e:
            raise LLMInvalidRequestError(f"模板变量缺失: {e}")
        return await self.chat(prompt, system_prompt=system_prompt, options=options)

    # ======================== 内部方法 ========================

    def _build_payload(
        self,
        messages: List[ChatMessage],
        stream: bool = False,
        options: Optional[LLMRequestOptions] = None,
    ) -> Dict:
        """构建请求体"""
        opts = options or LLMRequestOptions()

        payload = {
            "model": opts.model or self.default_model,
            "messages": [m.to_dict() for m in messages],
            "temperature": opts.temperature if opts.temperature is not None else self.default_temperature,
            "max_tokens": opts.max_tokens or self.default_max_tokens,
            "stream": stream,
        }

        if opts.top_p is not None:
            payload["top_p"] = opts.top_p
        if opts.frequency_penalty is not None:
            payload["frequency_penalty"] = opts.frequency_penalty
        if opts.presence_penalty is not None:
            payload["presence_penalty"] = opts.presence_penalty
        if opts.stop:
            payload["stop"] = opts.stop
        if opts.response_format:
            payload["response_format"] = opts.response_format

        return payload

    async def _request_with_retry(self, payload: Dict) -> Dict:
        """带重试的请求"""
        last_error: Optional[Exception] = None

        for attempt in range(1, self.max_retries + 1):
            try:
                response = await self.client.post(
                    "/chat/completions",
                    json=payload,
                )

                if response.status_code == 200:
                    return response.json()

                self._handle_error_status(response.status_code, response.content)

            except (LLMAuthenticationError, LLMInvalidRequestError):
                raise  # 不重试认证和参数错误
            except LLMRateLimitError as e:
                last_error = e
                wait = min(2 ** attempt, 30)
                logger.warning(f"触发速率限制，{wait}s 后重试 (第{attempt}次)")
                await asyncio.sleep(wait)
            except (LLMConnectionError, LLMTimeoutError) as e:
                last_error = e
                wait = min(2 ** attempt, 15)
                logger.warning(f"请求失败: {e}，{wait}s 后重试 (第{attempt}次)")
                await asyncio.sleep(wait)
            except httpx.TimeoutException as e:
                last_error = LLMTimeoutError(f"请求超时: {e}", model=payload.get("model", ""))
                wait = min(2 ** attempt, 15)
                logger.warning(f"请求超时，{wait}s 后重试 (第{attempt}次)")
                await asyncio.sleep(wait)
            except httpx.ConnectError as e:
                last_error = LLMConnectionError(f"连接失败: {e}", model=payload.get("model", ""))
                wait = min(2 ** attempt, 15)
                logger.warning(f"连接失败，{wait}s 后重试 (第{attempt}次)")
                await asyncio.sleep(wait)
            except Exception as e:
                last_error = LLMError(f"未知错误: {e}", model=payload.get("model", ""))
                logger.error(f"LLM 调用未知错误: {e}")
                if attempt == self.max_retries:
                    raise last_error
                await asyncio.sleep(2)

        raise last_error or LLMError("所有重试均失败")

    def _handle_error_status(self, status_code: int, body: bytes):
        """处理 HTTP 错误状态码"""
        try:
            error_data = json.loads(body)
            error_msg = error_data.get("error", {}).get("message", str(body[:500]))
        except (json.JSONDecodeError, AttributeError):
            error_msg = body.decode("utf-8", errors="replace")[:500]

        if status_code == 401:
            raise LLMAuthenticationError(f"认证失败: {error_msg}")
        elif status_code == 403:
            # 地区限制或访问被拒绝
            if "Country" in error_msg or "region" in error_msg or "territory" in error_msg:
                raise LLMAuthenticationError(
                    f"LLM API 地区限制: {error_msg}。请检查 .env 配置，确保 OPENAI_BASE_URL 设置为可用的 API 地址（如国内中转服务）"
                )
            raise LLMAuthenticationError(f"访问被拒绝 (403): {error_msg}")
        elif status_code == 429:
            raise LLMRateLimitError(f"速率限制: {error_msg}")
        elif status_code == 400:
            raise LLMInvalidRequestError(f"请求无效: {error_msg}")
        elif status_code >= 500:
            raise LLMConnectionError(f"服务端错误 ({status_code}): {error_msg}")
        else:
            raise LLMError(f"HTTP {status_code}: {error_msg}")

    @staticmethod
    def _strip_markdown_fences(text: str) -> str:
        """去除 LLM 返回内容中的 markdown 代码块标记（```json ... ```），支持截断响应"""
        import re
        stripped = text.strip()
        # 完整代码块: ```json ... ```
        match = re.search(r"```(?:json)?\s*\n?(.*?)\n?\s*```", stripped, re.DOTALL)
        if match:
            return match.group(1).strip()
        # 截断响应: 只有开头 ```json 没有结尾 ```
        match = re.match(r"```(?:json)?\s*\n?(.*)", stripped, re.DOTALL)
        if match:
            return match.group(1).strip()
        return stripped

    @staticmethod
    def _parse_response(data: Dict) -> LLMResponse:
        """解析非流式响应"""
        try:
            choice = data["choices"][0]
            usage_data = data.get("usage", {})

            return LLMResponse(
                content=choice["message"]["content"],
                model=data.get("model", ""),
                usage=LLMUsage(
                    prompt_tokens=usage_data.get("prompt_tokens", 0),
                    completion_tokens=usage_data.get("completion_tokens", 0),
                    total_tokens=usage_data.get("total_tokens", 0),
                ),
                finish_reason=choice.get("finish_reason", ""),
                raw_response=data,
            )
        except (KeyError, IndexError) as e:
            raise LLMResponseError(f"响应格式异常: {e}\n原始数据: {str(data)[:500]}")

    @staticmethod
    def _parse_stream_chunk(data: Dict) -> LLMStreamChunk:
        """解析流式响应块"""
        try:
            choice = data["choices"][0]
            delta = choice.get("delta", {})
            return LLMStreamChunk(
                content=delta.get("content", ""),
                finish_reason=choice.get("finish_reason"),
                model=data.get("model", ""),
            )
        except (KeyError, IndexError):
            return LLMStreamChunk()


# ======================== 便捷函数 ========================

_default_client: Optional[LLMClient] = None


def get_llm_client() -> LLMClient:
    """
    获取全局 LLM 客户端单例。
    
    适合在 FastAPI 依赖注入或服务层中使用。
    """
    global _default_client
    if _default_client is None:
        _default_client = LLMClient()
    return _default_client


async def quick_chat(
    prompt: str,
    system_prompt: Optional[str] = None,
    options: Optional[LLMRequestOptions] = None,
) -> str:
    """
    快速调用 - 直接返回文本内容。

    Args:
        prompt: 用户输入
        system_prompt: 系统提示词（可选）
        options: 请求参数覆盖（可选）

    Returns:
        LLM 生成的文本
    """
    client = get_llm_client()
    response = await client.chat(prompt, system_prompt=system_prompt, options=options)
    return response.content
