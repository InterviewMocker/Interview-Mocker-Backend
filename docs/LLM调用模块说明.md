# LLM 大模型调用模块说明

> 模块路径：`shared/utils/llm/`
> 
> 基于 OpenAI 兼容协议，支持 OpenAI / DeepSeek / 通义千问 / Moonshot / 本地 Ollama 等服务商。

---

## 1. 环境配置

在 `.env` 文件中配置以下参数：

```env
# 必填
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxx

# 可选（按需修改）
OPENAI_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-4
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=2048
LLM_TIMEOUT=120
LLM_MAX_RETRIES=3
```

### 常见服务商 Base URL

| 服务商 | `OPENAI_BASE_URL` | 示例模型 |
|--------|-------------------|----------|
| OpenAI | `https://api.openai.com/v1` | `gpt-4` / `gpt-3.5-turbo` |
| DeepSeek | `https://api.deepseek.com/v1` | `deepseek-chat` |
| 通义千问 | `https://dashscope.aliyuncs.com/compatible-mode/v1` | `qwen-turbo` |
| Moonshot | `https://api.moonshot.cn/v1` | `moonshot-v1-8k` |
| 本地 Ollama | `http://localhost:11434/v1` | `llama3` |

---

## 2. 快速开始

### 2.1 导入

```python
from shared.utils.llm import LLMClient, ChatMessage, quick_chat, get_llm_client
```

### 2.2 一行调用

```python
# 直接返回文本字符串
text = await quick_chat("你好，请介绍一下Python")
```

### 2.3 创建客户端

```python
# 方式1：使用默认配置（从 .env 读取）
client = LLMClient()

# 方式2：手动指定参数（覆盖 .env）
client = LLMClient(
    api_key="sk-xxx",
    base_url="https://api.deepseek.com/v1",
    model="deepseek-chat",
)

# 方式3：全局单例（推荐在服务层使用）
client = get_llm_client()
```

---

## 3. 核心 API

### 3.1 单轮对话 `chat()`

```python
client = LLMClient()

response = await client.chat(
    prompt="请解释什么是面向对象编程",
    system_prompt="你是一位资深软件工程师",  # 可选
)

print(response.content)       # 回答文本
print(response.model)         # 实际使用的模型名
print(response.usage)         # Token 用量
print(response.is_complete)   # 是否正常结束
```

### 3.2 多轮对话 `chat_with_messages()`

```python
messages = [
    ChatMessage.system("你是一位技术面试官，正在面试Python开发岗位"),
    ChatMessage.user("你好，我是来面试的"),
    ChatMessage.assistant("你好！请先做个自我介绍吧"),
    ChatMessage.user("我有3年Python后端开发经验，熟悉FastAPI和Django"),
]

response = await client.chat_with_messages(messages)
print(response.content)  # 面试官的下一个问题
```

### 3.3 流式输出 `chat_stream()`

```python
# 单轮流式
async for chunk in client.chat_stream("写一篇关于AI面试的文章"):
    print(chunk.content, end="", flush=True)

# 多轮流式
async for chunk in client.chat_stream_with_messages(messages):
    print(chunk.content, end="", flush=True)
    if chunk.is_final:
        print("\n--- 生成完毕 ---")
```

### 3.4 JSON 模式 `chat_json()`

```python
result = await client.chat_json(
    prompt="列出3道Python面试题，包含题目和难度",
    system_prompt="返回JSON数组，每项有 question 和 difficulty 字段",
)
# result 已自动解析为 dict 或 list
# [{"question": "...", "difficulty": "中等"}, ...]
```

### 3.5 模板调用 `chat_with_template()`

```python
response = await client.chat_with_template(
    template="请为{position}岗位生成一道关于{topic}的面试题",
    variables={"position": "Python后端", "topic": "异步编程"},
    system_prompt="你是面试题出题专家",
)
```

---

## 4. 参数覆盖

任何 API 调用都可以通过 `LLMRequestOptions` 临时覆盖默认参数：

```python
from shared.utils.llm import LLMRequestOptions

options = LLMRequestOptions(
    model="gpt-3.5-turbo",  # 临时切换模型
    temperature=0.2,         # 更精确的回答
    max_tokens=4096,         # 更长的输出
    top_p=0.9,
)

response = await client.chat("复杂问题...", options=options)
```

**`LLMRequestOptions` 可用字段：**

| 字段 | 类型 | 说明 |
|------|------|------|
| `model` | `str` | 模型名称 |
| `temperature` | `float` | 温度 (0-2) |
| `max_tokens` | `int` | 最大生成 token 数 |
| `top_p` | `float` | 核采样 (0-1) |
| `frequency_penalty` | `float` | 频率惩罚 (-2 到 2) |
| `presence_penalty` | `float` | 存在惩罚 (-2 到 2) |
| `stop` | `list[str]` | 停止词列表 |
| `response_format` | `dict` | 响应格式，如 `{"type": "json_object"}` |

---

## 5. 响应对象

### `LLMResponse`

| 属性 | 类型 | 说明 |
|------|------|------|
| `content` | `str` | 生成的文本内容 |
| `model` | `str` | 实际使用的模型名 |
| `usage` | `LLMUsage` | Token 使用统计 |
| `finish_reason` | `str` | 结束原因 (`stop` / `length`) |
| `is_complete` | `bool` | 是否正常完成 (`finish_reason == "stop"`) |
| `raw_response` | `dict` | 原始 API 响应（调试用） |

### `LLMUsage`

| 属性 | 类型 | 说明 |
|------|------|------|
| `prompt_tokens` | `int` | 输入 token 数 |
| `completion_tokens` | `int` | 输出 token 数 |
| `total_tokens` | `int` | 总 token 数 |

### `LLMStreamChunk`

| 属性 | 类型 | 说明 |
|------|------|------|
| `content` | `str` | 本次增量文本 |
| `finish_reason` | `str \| None` | 结束原因 |
| `is_final` | `bool` | 是否为最后一个块 |

---

## 6. 异常处理

所有异常继承自 `LLMError`：

```python
from shared.utils.llm import (
    LLMError,
    LLMAuthenticationError,
    LLMRateLimitError,
    LLMConnectionError,
    LLMTimeoutError,
    LLMResponseError,
    LLMInvalidRequestError,
)

try:
    response = await client.chat("你好")
except LLMAuthenticationError:
    # API Key 无效 → 不重试，立即抛出
    pass
except LLMRateLimitError:
    # 速率限制 → 自动重试（指数退避），重试耗尽后抛出
    pass
except LLMTimeoutError:
    # 请求超时 → 自动重试
    pass
except LLMConnectionError:
    # 网络/服务端错误 → 自动重试
    pass
except LLMResponseError:
    # 响应格式异常 / JSON 解析失败
    pass
except LLMInvalidRequestError:
    # 请求参数错误 → 不重试，立即抛出
    pass
except LLMError:
    # 其他未分类错误
    pass
```

**自动重试策略：**

| 异常类型 | 是否重试 | 退避策略 |
|----------|----------|----------|
| `LLMAuthenticationError` | 不重试 | - |
| `LLMInvalidRequestError` | 不重试 | - |
| `LLMRateLimitError` | 重试 | 2^n 秒，上限 30s |
| `LLMTimeoutError` | 重试 | 2^n 秒，上限 15s |
| `LLMConnectionError` | 重试 | 2^n 秒，上限 15s |

---

## 7. 在服务层集成示例

```python
# main_service/services/interview_service.py

from shared.utils.llm import get_llm_client, ChatMessage, LLMRequestOptions


class InterviewService:

    def __init__(self):
        self.llm = get_llm_client()

    async def generate_question(self, position: str, topic: str) -> str:
        """生成面试题"""
        response = await self.llm.chat_with_template(
            template="请为{position}岗位生成一道关于{topic}的面试题，包含参考答案",
            variables={"position": position, "topic": topic},
            system_prompt="你是专业的技术面试题出题专家",
            options=LLMRequestOptions(temperature=0.8),
        )
        return response.content

    async def evaluate_answer(self, question: str, answer: str) -> dict:
        """评估面试回答"""
        return await self.llm.chat_json(
            prompt=f"面试题：{question}\n\n候选人回答：{answer}",
            system_prompt="评估候选人的回答，返回JSON: {score: 1-10, feedback: 评语, suggestions: [改进建议]}",
        )
```

---

## 8. 文件结构

```
shared/utils/llm/
├── __init__.py      # 模块导出
├── client.py        # LLMClient 核心客户端 + get_llm_client() + quick_chat()
├── models.py        # ChatMessage / LLMResponse / LLMStreamChunk / LLMRequestOptions
└── exceptions.py    # LLMError 及其子类
```

**配置文件：**
- `main_service/core/config.py` — Settings 中的 LLM 相关字段
- `.env` / `.env.example` — 环境变量
