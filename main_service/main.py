"""
FastAPI 应用入口
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from .core.config import settings
from .core.database import init_db, close_db, get_db
from .api import router as api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化数据库
    await init_db()
    yield
    # 关闭时清理资源
    await close_db()


def create_app() -> FastAPI:
    """创建FastAPI应用"""
    app = FastAPI(
        title=settings.app_name,
        description="AI模拟面试与能力提升平台 - 后端API服务",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan
    )
    
    # 配置CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # 生产环境应配置具体域名
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 注册路由
    app.include_router(api_router, prefix="/api")
    
    # 健康检查端点
    @app.get("/health")
    async def health_check():
        return {"status": "healthy", "service": "main-service"}
    
    # 验证错误处理器 - 返回中文错误消息
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        # 错误消息中英文映射
        error_messages = {
            "value_error": "数据格式错误",
            "string_too_short": "长度不足",
            "string_too_long": "长度超限",
            "missing": "必填字段",
        }
        field_names = {
            "username": "用户名",
            "password": "密码",
            "email": "邮箱",
            "real_name": "真实姓名",
            "school": "学校",
            "major": "专业",
        }
        
        errors = []
        for err in exc.errors():
            field = err["loc"][-1] if err["loc"] else "unknown"
            field_cn = field_names.get(field, field)
            err_type = err["type"]
            
            if "email" in str(err.get("msg", "")):
                msg = f"{field_cn}格式不正确"
            elif err_type == "string_too_short":
                msg = f"{field_cn}长度不足"
            elif err_type == "missing":
                msg = f"{field_cn}为必填项"
            else:
                msg = f"{field_cn}{error_messages.get(err_type, '验证失败')}"
            
            errors.append({"field": field, "message": msg})
        
        return JSONResponse(
            status_code=422,
            content={"code": 422, "message": errors[0]["message"] if errors else "参数验证失败", "errors": errors}
        )
    
    # HTTP 异常处理器 - 统一格式
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"code": exc.status_code, "message": exc.detail, "data": None}
        )
    
    # 全局异常处理器
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        print(f"[ERROR] 未处理异常: {type(exc).__name__}: {exc}")
        return JSONResponse(
            status_code=500,
            content={"code": 500, "message": "服务器内部错误", "data": None}
        )
    
    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main_service.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
