# AI数字人面试微服务设计

## 1. 微服务概述

### 1.1 服务定位
AI数字人面试微服务是平台的核心交互模块,基于开源项目 OpenAvatarChat 框架构建,负责:
- 实时语音/文字对话交互
- 数字人形象渲染与展示
- 面试流程控制
- 题目推送与答案收集
- 多模态分析接口预留

### 1.2 技术基础
- **基础框架**: OpenAvatarChat (数字人对话框架)
- **开发语言**: Python 3.10+
- **通信协议**: WebSocket (实时对话) + HTTP (控制指令)
- **消息队列**: Redis Pub/Sub (与主服务通信)
- **AI模型**: 支持多种LLM (OpenAI GPT-4, Claude, 国产大模型)
- **语音处理**: ASR (语音识别) + TTS (语音合成)

### 1.3 服务边界

**微服务职责:**
- 管理面试对话流程
- 实时语音/文字交互
- 数字人形象渲染
- 上下文管理
- 情感分析预留接口

**不负责的职责 (由主服务处理):**
- 题库管理与选题逻辑
- 答案评估与打分
- 报告生成
- 用户数据管理
- 知识库检索

## 2. 基于OpenAvatarChat的架构设计

### 2.1 OpenAvatarChat框架概述

OpenAvatarChat提供的核心能力:
- 数字人渲染引擎
- 语音识别(ASR)与合成(TTS)
- 对话管理框架
- WebSocket通信
- 插件化扩展机制

### 2.2 定制化架构

```
┌─────────────────────────────────────────────────────────────┐
│           AI数字人面试微服务架构                              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌────────────────────────────────────────────────────┐    │
│  │         OpenAvatarChat 核心框架                     │    │
│  │  ┌──────────────┐  ┌──────────────┐               │    │
│  │  │ 数字人渲染    │  │ 语音处理      │               │    │
│  │  │ (Avatar)     │  │ (ASR/TTS)    │               │    │
│  │  └──────────────┘  └──────────────┘               │    │
│  │  ┌──────────────────────────────────────┐         │    │
│  │  │      对话管理引擎                     │         │    │
│  │  │  - 会话状态管理                       │         │    │
│  │  │  - 上下文维护                         │         │    │
│  │  │  - 多轮对话控制                       │         │    │
│  │  └──────────────────────────────────────┘         │    │
│  └────────────────────────────────────────────────────┘    │
│                          ▲                                  │
│                          │ 插件化扩展                       │
│                          ▼                                  │
│  ┌────────────────────────────────────────────────────┐    │
│  │         自定义Handler层 (面试业务逻辑)              │    │
│  ├────────────────────────────────────────────────────┤    │
│  │  ┌──────────────────┐  ┌──────────────────┐       │    │
│  │  │InterviewFlowHandler│ │QuestionHandler   │       │    │
│  │  │ 面试流程控制      │  │ 题目推送管理      │       │    │
│  │  └──────────────────┘  └──────────────────┘       │    │
│  │  ┌──────────────────┐  ┌──────────────────┐       │    │
│  │  │AnswerHandler     │  │ContextHandler    │       │    │
│  │  │ 答案收集处理      │  │ 上下文增强        │       │    │
│  │  └──────────────────┘  └──────────────────┘       │    │
│  │  ┌──────────────────┐  ┌──────────────────┐       │    │
│  │  │EvaluationTrigger │  │EmotionPlugin     │       │    │
│  │  │ 评估触发器        │  │ 情感分析(预留)    │       │    │
│  │  └──────────────────┘  └──────────────────┘       │    │
│  └────────────────────────────────────────────────────┘    │
│                          ▲                                  │
│                          │                                  │
│                          ▼                                  │
│  ┌────────────────────────────────────────────────────┐    │
│  │         通信层 (与主服务交互)                       │    │
│  ├────────────────────────────────────────────────────┤    │
│  │  ┌──────────────┐  ┌──────────────┐               │    │
│  │  │ HTTP Client  │  │ Redis Pub/Sub│               │    │
│  │  │ (RESTful API)│  │ (消息队列)    │               │    │
│  │  └──────────────┘  └──────────────┘               │    │
│  │  ┌──────────────────────────────────────┐         │    │
│  │  │      WebSocket Server                │         │    │
│  │  │  (与前端实时通信)                     │         │    │
│  │  └──────────────────────────────────────┘         │    │
│  └────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

## 3. 自定义Handler设计

### 3.1 InterviewFlowHandler (面试流程控制)

**职责:**
- 管理面试的开始、进行、结束流程
- 控制面试节奏
- 处理异常中断

**核心方法:**
```python
class InterviewFlowHandler(BaseHandler):
    """面试流程控制Handler"""
    
    async def on_interview_start(self, session_data: dict):
        """
        面试开始
        - 初始化会话状态
        - 发送欢迎语
        - 请求第一个问题
        """
        pass
    
    async def on_question_completed(self, qa_data: dict):
        """
        单个问题完成
        - 判断是否需要追问
        - 决定下一个问题
        - 检查面试是否结束
        """
        pass
    
    async def on_interview_end(self, session_id: str):
        """
        面试结束
        - 发送结束语
        - 通知主服务生成报告
        - 清理会话状态
        """
        pass
    
    async def handle_interruption(self, reason: str):
        """处理面试中断"""
        pass
```

### 3.2 QuestionHandler (题目推送管理)

**职责:**
- 从主服务获取题目
- 将题目转换为自然对话
- 管理题目队列

**核心方法:**
```python
class QuestionHandler(BaseHandler):
    """题目推送Handler"""
    
    async def fetch_next_question(self, session_id: str, context: dict):
        """
        从主服务获取下一个问题
        
        Args:
            session_id: 面试会话ID
            context: 当前上下文(已回答的题目、用户表现等)
        
        Returns:
            Question对象
        """
        # 调用主服务API
        response = await self.http_client.post(
            f"{MAIN_SERVICE_URL}/api/v1/questions/next",
            json={
                "session_id": session_id,
                "context": context
            }
        )
        return response.json()
    
    async def present_question(self, question: dict):
        """
        以自然对话方式呈现问题
        - 将题目内容转换为口语化表达
        - 通过TTS播放
        - 显示在界面上
        """
        # 使用LLM优化问题表达
        natural_question = await self.llm.optimize_question(question["content"])
        
        # 发送给数字人
        await self.avatar.speak(natural_question)
        
        # 通知前端显示
        await self.websocket.send_json({
            "type": "question",
            "data": {
                "question_id": question["id"],
                "content": natural_question,
                "original_content": question["content"]
            }
        })
    
    async def handle_follow_up(self, previous_answer: dict):
        """
        处理追问逻辑
        - 基于用户回答生成追问
        - 或从题库获取预设追问
        """
        pass
```

### 3.3 AnswerHandler (答案收集处理)

**职责:**
- 收集用户语音/文字回答
- 答案预处理
- 回传主服务进行评估

**核心方法:**
```python
class AnswerHandler(BaseHandler):
    """答案收集Handler"""
    
    async def on_user_speech(self, audio_data: bytes):
        """
        处理用户语音输入
        - ASR识别为文字
        - 存储音频文件
        - 记录回答时间
        """
        # ASR识别
        text = await self.asr.recognize(audio_data)
        
        # 保存音频
        audio_url = await self.storage.save_audio(audio_data)
        
        return {
            "text": text,
            "audio_url": audio_url,
            "timestamp": datetime.now().isoformat()
        }
    
    async def on_user_text(self, text: str):
        """处理用户文字输入"""
        return {
            "text": text,
            "timestamp": datetime.now().isoformat()
        }
    
    async def submit_answer(self, session_id: str, question_id: str, answer: dict):
        """
        提交答案到主服务
        
        触发评估流程
        """
        await self.redis.publish(
            "interview:answer_submitted",
            json.dumps({
                "session_id": session_id,
                "question_id": question_id,
                "answer": answer
            })
        )
        
        # 同时调用HTTP接口确保可靠性
        await self.http_client.post(
            f"{MAIN_SERVICE_URL}/api/v1/interviews/answers",
            json={
                "session_id": session_id,
                "question_id": question_id,
                "answer": answer
            }
        )
    
    async def provide_instant_feedback(self, answer: dict):
        """
        提供即时反馈
        - 简单的鼓励语
        - 不涉及具体评分
        """
        feedback = await self.llm.generate_encouragement(answer["text"])
        await self.avatar.speak(feedback)
```

### 3.4 ContextHandler (上下文增强)

**职责:**
- 维护面试上下文
- 管理对话历史
- 提供上下文给LLM

**核心方法:**
```python
class ContextHandler(BaseHandler):
    """上下文管理Handler"""
    
    def __init__(self):
        self.context_window = 10  # 保留最近10轮对话
        self.contexts = {}  # {session_id: context}
    
    async def add_interaction(self, session_id: str, interaction: dict):
        """
        添加一轮交互到上下文
        
        Args:
            interaction: {
                "type": "question" | "answer",
                "content": "...",
                "timestamp": "..."
            }
        """
        if session_id not in self.contexts:
            self.contexts[session_id] = []
        
        self.contexts[session_id].append(interaction)
        
        # 保持窗口大小
        if len(self.contexts[session_id]) > self.context_window:
            self.contexts[session_id] = self.contexts[session_id][-self.context_window:]
    
    async def get_context(self, session_id: str) -> list:
        """获取会话上下文"""
        return self.contexts.get(session_id, [])
    
    async def build_llm_context(self, session_id: str) -> str:
        """
        构建LLM提示词上下文
        
        Returns:
            格式化的上下文字符串
        """
        context = await self.get_context(session_id)
        
        formatted = "面试对话历史:\n"
        for item in context:
            if item["type"] == "question":
                formatted += f"面试官: {item['content']}\n"
            else:
                formatted += f"应聘者: {item['content']}\n"
        
        return formatted
    
    async def clear_context(self, session_id: str):
        """清理会话上下文"""
        if session_id in self.contexts:
            del self.contexts[session_id]
```

### 3.5 EvaluationTriggerHandler (评估触发器)

**职责:**
- 监听答案提交事件
- 触发主服务评估
- 接收评估结果

**核心方法:**
```python
class EvaluationTriggerHandler(BaseHandler):
    """评估触发Handler"""
    
    async def trigger_evaluation(self, qa_data: dict):
        """
        触发评估
        
        通过消息队列通知主服务进行评估
        """
        await self.redis.publish(
            "evaluation:trigger",
            json.dumps({
                "session_id": qa_data["session_id"],
                "question_id": qa_data["question_id"],
                "answer": qa_data["answer"],
                "priority": "normal"
            })
        )
    
    async def on_evaluation_result(self, result: dict):
        """
        接收评估结果
        
        订阅评估结果频道
        """
        # 可选: 根据评估结果调整后续问题难度
        if result["score"] < 60:
            # 降低难度
            await self.adjust_difficulty("easier")
        elif result["score"] > 85:
            # 提高难度
            await self.adjust_difficulty("harder")
```

### 3.6 EmotionAnalysisPlugin (情感分析插件 - 预留)

**职责:**
- 分析用户语音情感
- 分析面部表情(如果有视频)
- 提供情感数据给评估模块

**接口预留:**
```python
class EmotionAnalysisPlugin(BasePlugin):
    """情感分析插件(未来扩展)"""
    
    async def analyze_voice_emotion(self, audio_data: bytes) -> dict:
        """
        分析语音情感
        
        Returns:
            {
                "emotion": "confident" | "nervous" | "calm",
                "confidence": 0.85,
                "energy_level": 0.7
            }
        """
        # TODO: 集成语音情感分析模型
        pass
    
    async def analyze_facial_expression(self, video_frame: bytes) -> dict:
        """
        分析面部表情
        
        Returns:
            {
                "expression": "smile" | "serious" | "confused",
                "confidence": 0.9
            }
        """
        # TODO: 集成面部表情识别模型
        pass
    
    async def get_emotion_summary(self, session_id: str) -> dict:
        """
        获取整场面试的情感摘要
        
        Returns:
            {
                "overall_confidence": 0.75,
                "stress_level": 0.4,
                "engagement": 0.85
            }
        """
        pass
```

## 4. 与主服务的通信协议

### 4.1 HTTP RESTful API

**微服务提供的API (供主服务调用):**

```
POST   /api/interview/start          # 启动面试
POST   /api/interview/stop           # 停止面试
GET    /api/interview/status/{id}    # 查询面试状态
POST   /api/interview/inject-question # 注入题目
```

**调用主服务的API:**

```
POST   /api/v1/questions/next        # 获取下一个问题
POST   /api/v1/interviews/answers    # 提交答案
GET    /api/v1/knowledge/search      # RAG知识检索
POST   /api/v1/evaluation/trigger    # 触发评估
```

### 4.2 Redis Pub/Sub消息队列

**频道设计:**

```python
# 消息频道定义
CHANNELS = {
    # 微服务发布
    "interview:started": "面试开始事件",
    "interview:answer_submitted": "答案提交事件",
    "interview:completed": "面试完成事件",
    "interview:error": "面试异常事件",
    
    # 微服务订阅
    "evaluation:result": "评估结果",
    "question:push": "主服务推送题目",
    "interview:control": "面试控制指令"
}

# 消息格式示例
{
    "event": "interview:answer_submitted",
    "timestamp": "2026-02-13T10:30:00Z",
    "data": {
        "session_id": "uuid",
        "question_id": "uuid",
        "answer": {
            "text": "用户回答内容",
            "audio_url": "oss://path/to/audio",
            "duration_seconds": 45
        }
    }
}
```

### 4.3 WebSocket协议 (与前端通信)

**消息类型:**
```json
// 客户端 -> 微服务
{
  "type": "user_message",
  "data": {
    "session_id": "uuid",
    "content": "用户输入的文字",
    "mode": "text"
  }
}

{
  "type": "user_audio",
  "data": {
    "session_id": "uuid",
    "audio": "base64_encoded_audio",
    "format": "wav"
  }
}

// 微服务 -> 客户端
{
  "type": "avatar_message",
  "data": {
    "text": "面试官说的话",
    "audio_url": "https://cdn.../audio.mp3",
    "animation": "talking"
  }
}

{
  "type": "question",
  "data": {
    "question_id": "uuid",
    "content": "请介绍一下Java的多态性",
    "type": "technical"
  }
}

{
  "type": "interview_status",
  "data": {
    "status": "in_progress",
    "current_question": 3,
    "total_questions": 10,
    "elapsed_time": 600
  }
}
```

## 5. 面试流程完整示例

### 5.1 面试启动流程

```
1. 用户在前端点击"开始面试"
    ↓
2. 前端调用主服务API创建面试会话
   POST /api/v1/interviews/sessions
    ↓
3. 主服务创建会话记录,返回session_id
    ↓
4. 主服务调用AI数字人微服务启动面试
   POST /interview/start
   {
     "session_id": "uuid",
     "user_id": "uuid",
     "position_id": "uuid",
     "config": {...}
   }
    ↓
5. 微服务初始化会话状态
   - 创建WebSocket连接
   - 初始化上下文
   - 加载数字人形象
    ↓
6. 微服务发送欢迎语
   "你好,欢迎参加Java后端工程师面试,我是你的面试官..."
    ↓
7. InterviewFlowHandler请求第一个问题
   调用QuestionHandler.fetch_next_question()
    ↓
8. QuestionHandler从主服务获取题目
   POST /api/v1/questions/next
    ↓
9. 主服务基于岗位+用户画像+RAG返回题目
    ↓
10. QuestionHandler呈现问题
    数字人说出问题 + 前端显示文字
    ↓
11. 等待用户回答...
```

### 5.2 答题与评估流程

```
1. 用户开始回答(语音或文字)
    ↓
2. AnswerHandler收集答案
   - 语音: ASR识别 + 保存音频
   - 文字: 直接收集
    ↓
3. ContextHandler更新上下文
    ↓
4. AnswerHandler提交答案到主服务
   - Redis Pub/Sub发布消息
   - HTTP POST备份
    ↓
5. 主服务评估模块接收答案
    ↓
6. 评估模块分析答案
   - 技术准确性
   - 表达清晰度
   - 深度与广度
   - RAG检索相关知识点对比
    ↓
7. 评估结果存储到数据库
    ↓
8. 评估结果通过Redis发布给微服务
   Channel: evaluation:result
    ↓
9. EvaluationTriggerHandler接收结果
   - 可选: 调整后续难度
    ↓
10. 微服务提供简单反馈
    "好的,我明白了。接下来..."
    ↓
11. InterviewFlowHandler决定下一步
    - 是否追问
    - 下一个问题
    - 或结束面试
```

### 5.3 面试结束流程

```
1. 达到结束条件
   - 题目全部完成
   - 时间到达
   - 用户主动结束
    ↓
2. InterviewFlowHandler.on_interview_end()
    ↓
3. 数字人说结束语
   "感谢你参加本次面试,我们会尽快给你反馈..."
    ↓
4. 发布面试完成事件
   Redis Pub/Sub: interview:completed
    ↓
5. 主服务接收完成事件
    ↓
6. 更新会话状态为completed
    ↓
7. 触发报告生成(异步任务)
    ↓
8. 微服务清理资源
   - 清理上下文
   - 关闭WebSocket
   - 释放数字人资源
    ↓
9. 前端跳转到报告页面
```

## 6. 配置与部署

### 6.1 微服务配置文件

```yaml
# config/interview_service.yaml

service:
  name: interview-avatar-service
  port: 8001
  host: 0.0.0.0

main_service:
  url: http://main-service:8000
  api_key: ${MAIN_SERVICE_API_KEY}

redis:
  host: redis
  port: 6379
  db: 1
  password: ${REDIS_PASSWORD}

openavatar:
  avatar_model: default_interviewer
  voice_model: zh-CN-XiaoxiaoNeural
  asr_provider: azure  # azure, google, whisper
  tts_provider: azure

llm:
  provider: openai
  model: gpt-4
  api_key: ${OPENAI_API_KEY}
  temperature: 0.7
  max_tokens: 500

storage:
  provider: minio
  endpoint: http://minio:9000
  access_key: ${MINIO_ACCESS_KEY}
  secret_key: ${MINIO_SECRET_KEY}
  bucket: interview-audio

interview:
  max_duration_minutes: 60
  max_questions: 20
  default_difficulty: medium
  enable_follow_up: true
```

### 6.2 Docker部署

```dockerfile
# Dockerfile

FROM python:3.10-slim

WORKDIR /app

# 安装OpenAvatarChat依赖
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsm6 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制代码
COPY . .

# 暴露端口
EXPOSE 8001

# 启动命令
CMD ["python", "main.py"]
```

```yaml
# docker-compose.yml (微服务部分)

services:
  interview-avatar-service:
    build: ./interview_avatar_service
    ports:
      - "8001:8001"
    environment:
      - MAIN_SERVICE_URL=http://main-service:8000
      - REDIS_HOST=redis
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    depends_on:
      - redis
      - main-service
    volumes:
      - ./interview_avatar_service:/app
    networks:
      - app-network
```

## 7. 监控与日志

### 7.1 关键指标监控

```python
# 监控指标
METRICS = {
    "active_interviews": "当前活跃面试数",
    "avg_response_time": "平均响应时间",
    "asr_accuracy": "语音识别准确率",
    "websocket_connections": "WebSocket连接数",
    "error_rate": "错误率",
    "question_fetch_latency": "题目获取延迟",
    "avatar_render_fps": "数字人渲染帧率"
}
```

### 7.2 日志规范

```python
# 日志格式
{
    "timestamp": "2026-02-13T10:30:00Z",
    "level": "INFO",
    "service": "interview-avatar-service",
    "session_id": "uuid",
    "event": "question_presented",
    "data": {
        "question_id": "uuid",
        "latency_ms": 150
    }
}
```

## 8. 扩展性设计

### 8.1 多模态扩展接口

```python
# 预留的多模态分析接口
class MultiModalAnalyzer:
    """多模态分析器(未来扩展)"""
    
    async def analyze_interview_session(self, session_id: str) -> dict:
        """
        综合分析面试会话
        
        Returns:
            {
                "voice_analysis": {...},
                "facial_analysis": {...},
                "gesture_analysis": {...},
                "overall_confidence": 0.85
            }
        """
        pass
```

### 8.2 自定义面试官人设

```python
# 面试官人设配置
INTERVIEWER_PERSONAS = {
    "friendly": {
        "name": "小智",
        "style": "友好、鼓励型",
        "avatar": "friendly_avatar.glb",
        "voice": "warm_voice"
    },
    "professional": {
        "name": "李工",
        "style": "专业、严谨型",
        "avatar": "professional_avatar.glb",
        "voice": "professional_voice"
    },
    "challenging": {
        "name": "王总",
        "style": "挑战、压力型",
        "avatar": "challenging_avatar.glb",
        "voice": "serious_voice"
    }
}
```

## 9. 测试策略

### 9.1 单元测试

```python
# tests/test_handlers.py

async def test_question_handler():
    """测试题目推送Handler"""
    handler = QuestionHandler()
    question = await handler.fetch_next_question("session_id", {})
    assert question is not None
    assert "id" in question
    assert "content" in question

async def test_answer_handler():
    """测试答案收集Handler"""
    handler = AnswerHandler()
    answer = await handler.on_user_text("这是测试回答")
    assert answer["text"] == "这是测试回答"
    assert "timestamp" in answer
```

### 9.2 集成测试

```python
# tests/test_integration.py

async def test_full_interview_flow():
    """测试完整面试流程"""
    # 1. 启动面试
    session = await start_interview(user_id, position_id)
    
    # 2. 获取问题
    question = await get_next_question(session.id)
    assert question is not None
    
    # 3. 提交答案
    answer = await submit_answer(session.id, question.id, "测试答案")
    assert answer.submitted
    
    # 4. 结束面试
    result = await end_interview(session.id)
    assert result.status == "completed"
```

## 10. 性能优化建议

### 10.1 并发处理
- 使用异步IO处理多个面试会话
- WebSocket连接池管理
- 限制单服务器最大并发面试数

### 10.2 资源优化
- 数字人模型懒加载
- 音频流式传输
- 缓存常用问题的TTS结果

### 10.3 网络优化
- 使用CDN分发音频资源
- WebSocket心跳保活
- 断线重连机制

## 11. 安全考虑

### 11.1 认证授权
- 验证主服务调用的API Key
- WebSocket连接需要JWT Token
- 限制单用户并发面试数

### 11.2 数据安全
- 音频数据加密传输
- 敏感信息脱敏
- 定期清理临时文件

### 11.3 防滥用
- 请求频率限制
- 面试时长限制
- 异常行为检测
