# AI模拟面试与能力提升平台 - 后端服务

面向计算机专业学生的AI模拟面试平台，提供针对特定技术岗位的智能面试训练、多维度评估反馈和个性化能力提升建议。

## 架构概述

本项目包含**两个独立的 FastAPI 服务**，由两个团队分别开发：

| 服务 | 端口 | 团队 | 说明 |
|------|------|------|------|
| **主服务** | 8000 | 团队A | 用户认证、题库、知识库、评估等核心功能 |
| **数字人面试服务** | 8001 | 团队B | 面试交互、语音处理、数字人渲染 |

两个服务**共享同一套数据模型和数据库**，通过 HTTP 通信。

```
┌─────────────────────┐         HTTP         ┌─────────────────────┐
│   主服务 (8000)      │  ◄──────────────────►│  数字人服务 (8001)   │
└──────────┬──────────┘                      └──────────┬──────────┘
           │              共享数据库                     │
           ▼                                            ▼
    ┌──────────────────────────────────────────────────────┐
    │              SQLite / PostgreSQL                      │
    │         data/interview_mocker.db (开发)              │
    └──────────────────────────────────────────────────────┘
```

## 技术栈

- **开发语言**: Python 3.11+
- **Web框架**: FastAPI
- **数据库**: SQLite (开发) / PostgreSQL (生产)
- **向量数据库**: ChromaDB
- **认证**: JWT
- **服务通信**: HTTP RESTful

## 项目结构

```
Interview-Mocker-Backend/
├── shared/                        # 【共享包】两个服务都依赖
│   ├── models/                    # 共享数据模型 (SQLAlchemy)
│   │   ├── base.py               # 模型基类、Mixin
│   │   ├── user.py               # User, UserProfile, UserLoginLog
│   │   ├── position.py           # Position, PositionKnowledgePoint
│   │   ├── question.py           # Question, PositionQuestion
│   │   ├── interview.py          # InterviewSession, InterviewQARecord
│   │   ├── evaluation.py         # EvaluationReport, ImprovementPlan
│   │   ├── knowledge.py          # KnowledgeDocument, DocumentChunk
│   │   └── system.py             # SystemConfig
│   ├── database/                  # 数据库连接配置
│   │   └── connection.py         # 异步引擎、会话工厂
│   ├── config/                    # 共享配置
│   │   └── settings.py           # SharedSettings
│   └── utils/                     # 共享工具函数
│
├── main_service/                  # 【主服务】团队A开发 - 端口 8000
│   ├── api/v1/                    # API 路由
│   │   ├── auth.py               # 认证授权
│   │   ├── users.py              # 用户管理
│   │   ├── positions.py          # 岗位管理
│   │   ├── questions.py          # 题库管理
│   │   ├── interviews.py         # 面试会话
│   │   └── knowledge.py          # 知识库
│   ├── core/                      # 核心配置
│   │   ├── config.py             # 服务配置
│   │   ├── database.py           # 数据库（重导出共享）
│   │   ├── dependencies.py       # 依赖注入
│   │   └── security.py           # JWT/密码处理
│   ├── models/                    # 重导出共享模型
│   ├── schemas/                   # Pydantic 模型
│   ├── services/                  # 业务逻辑
│   └── main.py                    # 入口文件
│
├── interview_avatar_service/      # 【数字人服务】团队B开发 - 端口 8001
│   ├── clients/                   # HTTP 客户端 (调用主服务)
│   │   └── main_service.py       # MainServiceClient
│   └── main.py                    # 入口文件
│
├── scripts/                       # 开发脚本
│   ├── migrate.py                # 数据库迁移管理
│   └── start_services.py         # 多服务启动脚本
├── data/                          # 数据目录 (SQLite, ChromaDB)
├── docker/                        # Docker 配置
├── tests/                         # 测试代码
├── docs/                          # 设计文档
└── run.py                         # 快速启动脚本
```

## 快速开始

### 1. 环境准备

```bash
# 安装 uv (如未安装)
# Windows: powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
# Linux/Mac: curl -LsSf https://astral.sh/uv/install.sh | sh

# 克隆项目并安装依赖
git clone <repo_url>
cd Interview-Mocker-Backend
uv sync
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件配置必要的环境变量
```

### 3. 初始化数据库

```bash
# 方式一：直接创建表
uv run python scripts/migrate.py init

# 方式二：使用 Alembic 迁移
uv run alembic upgrade head
```

### 4. 启动服务

#### 方式一：使用 run.py（推荐）

```bash
# 同时启动两个服务
uv run python run.py

# 仅启动主服务
uv run python run.py main

# 仅启动数字人服务
uv run python run.py avatar
```

#### 方式二：分别启动（调试时使用）

**终端 1 - 启动主服务：**
```bash
uv run uvicorn main_service.main:app --reload --port 8000
```

**终端 2 - 启动数字人服务：**
```bash
uv run uvicorn interview_avatar_service.main:app --reload --port 8001
```

#### 方式三：使用启动脚本

```bash
uv run python scripts/start_services.py
```

### 5. 访问 API 文档

| 服务 | Swagger UI | ReDoc |
|------|-----------|-------|
| 主服务 | http://localhost:8000/docs | http://localhost:8000/redoc |
| 数字人服务 | http://localhost:8001/docs | http://localhost:8001/redoc |

## 数据库迁移

两个团队共享数据库模型，迁移脚本统一管理。

```bash
# 查看当前版本
uv run python scripts/migrate.py current

# 应用迁移
uv run python scripts/migrate.py upgrade

# 生成新迁移 (修改 shared/models 后)
uv run python scripts/migrate.py generate "add user avatar field"

# 回滚迁移
uv run python scripts/migrate.py downgrade
```

**模型变更流程：**
1. 在 `shared/models/` 中修改模型
2. 生成迁移脚本
3. 提交代码（包含 models 和 migrations）
4. 另一个团队拉取后执行 `migrate.py upgrade`

## 服务间通信

数字人服务通过 HTTP 调用主服务：

```python
# interview_avatar_service/clients/main_service.py
from interview_avatar_service.clients import MainServiceClient

client = MainServiceClient()

# 获取下一个问题
question = await client.get_next_question(session_id, context)

# 提交用户答案
result = await client.submit_answer(session_id, question_id, answer)

# 触发评估
evaluation = await client.trigger_evaluation(session_id, qa_record_id)
```

## API 模块

### 主服务 (8000)

| 模块 | 路径 | 说明 |
|------|------|------|
| 认证授权 | `/api/v1/auth` | 注册、登录、Token管理 |
| 用户管理 | `/api/v1/users` | 用户信息、画像 |
| 岗位管理 | `/api/v1/positions` | 岗位CRUD |
| 题库管理 | `/api/v1/questions` | 题目CRUD、智能选题 |
| 面试会话 | `/api/v1/interviews` | 面试流程管理 |
| 知识库 | `/api/v1/knowledge` | 文档管理、RAG检索 |
| 评估分析 | `/api/v1/evaluations` | 答案评估、报告生成 |

### 数字人服务 (8001)

| 模块 | 路径 | 说明 |
|------|------|------|
| 会话控制 | `/api/v1/sessions` | 面试会话生命周期 |
| 对话交互 | `/api/v1/dialogue` | 实时对话 |
| 数字人 | `/api/v1/avatar` | 数字人状态控制 |

## Docker 部署

```bash
cd docker
docker-compose up -d
```

## 开发规范

### 数据库规范
- 主键统一使用 UUID
- 时间字段: `created_at`, `updated_at`
- 软删除: `deleted_at`

### API 规范
- RESTful 风格
- 统一响应格式: `{"code": 200, "message": "success", "data": {...}}`
- 版本控制: `/api/v1/`

### 服务间通信规范
- 使用 `X-Service-Token` Header 进行服务间认证
- 超时设置: 30秒
- 错误处理: 返回标准 HTTP 状态码

## 测试

```bash
# 运行所有测试
uv run pytest

# 运行主服务测试
uv run pytest tests/test_main_service/

# 运行数字人服务测试
uv run pytest tests/test_avatar_service/

# 带覆盖率
uv run pytest --cov=main_service --cov=interview_avatar_service
```

## 文档

详细设计文档位于 `docs/` 目录：

- `团队开发指南.md` - **两个团队的开发协作指南**
- `独立服务架构与数据库同步方案.md` - 服务独立开发方案
- `数字人面试服务架构设计V2.md` - 数字人服务详细设计
- `数据表设计.md` - 数据库表设计
- `知识库设计.md` - RAG 知识库设计
- `身份认证设计.md` - JWT 认证设计

## 许可证

MIT License
