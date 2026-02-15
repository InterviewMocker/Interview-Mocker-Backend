"""
题库和题目管理API
"""
import json
from typing import List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.database import get_db
from ...core.dependencies import get_current_user, get_current_admin
from ...schemas.question import (
    QuestionBankCreate, QuestionBankUpdate, QuestionBankResponse,
    CommunityReviewRequest,
    QuestionCreate, QuestionBatchCreate, QuestionBatchCreateResponse,
    QuestionUpdate, QuestionResponse, QuestionDetailResponse,
    ExtractionTaskResponse, ExtractionTaskListItem, BatchImportRequest,
)
from ...schemas.common import ResponseModel, PaginatedResponse
from ...services.question import QuestionBankService, QuestionService, QuestionExtractionService
from shared.models import User

router = APIRouter()


# ==================== 个人题库 API ====================

@router.get("/banks", response_model=ResponseModel[PaginatedResponse[QuestionBankResponse]])
async def list_my_question_banks(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    category: Optional[str] = None,
    status_filter: Optional[str] = Query(None, alias="status"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取当前用户的题库列表"""
    service = QuestionBankService(db)
    banks, total = await service.list_my_banks(
        user_id=current_user.id,
        page=page,
        page_size=page_size,
        category=category,
        status=status_filter
    )
    
    return ResponseModel(
        message="获取成功",
        data=PaginatedResponse(
            items=[QuestionBankResponse.model_validate(b) for b in banks],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=(total + page_size - 1) // page_size
        )
    )


@router.post("/banks", response_model=ResponseModel[QuestionBankResponse])
async def create_question_bank(
    bank_data: QuestionBankCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """创建题库"""
    service = QuestionBankService(db)
    
    bank = await service.create(
        data=bank_data.model_dump(),
        created_by=current_user.id
    )
    
    return ResponseModel(
        message="创建成功",
        data=QuestionBankResponse.model_validate(bank)
    )


@router.get("/banks/{bank_id}", response_model=ResponseModel[QuestionBankResponse])
async def get_question_bank(
    bank_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取题库详情（仅限自己拥有的题库）"""
    service = QuestionBankService(db)
    bank = await service.get_own_bank(bank_id, current_user.id)
    
    if not bank:
        raise HTTPException(status_code=404, detail="题库不存在")
    
    return ResponseModel(
        message="获取成功",
        data=QuestionBankResponse.model_validate(bank)
    )


@router.put("/banks/{bank_id}", response_model=ResponseModel[QuestionBankResponse])
async def update_question_bank(
    bank_id: str,
    bank_data: QuestionBankUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """更新题库（校验归属，若已上架社区则自动下架）"""
    service = QuestionBankService(db)
    bank = await service.update(
        bank_id=bank_id,
        user_id=current_user.id,
        data=bank_data.model_dump(exclude_unset=True)
    )
    
    if not bank:
        raise HTTPException(status_code=404, detail="题库不存在")
    
    return ResponseModel(
        message="更新成功",
        data=QuestionBankResponse.model_validate(bank)
    )


@router.delete("/banks/{bank_id}", response_model=ResponseModel)
async def delete_question_bank(
    bank_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """删除题库（校验归属）"""
    service = QuestionBankService(db)
    success = await service.delete(bank_id, current_user.id)
    
    if not success:
        raise HTTPException(status_code=404, detail="题库不存在")
    
    return ResponseModel(message="删除成功")


# ==================== 社区题库 API ====================

@router.get("/community/banks", response_model=ResponseModel[PaginatedResponse[QuestionBankResponse]])
async def list_community_banks(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    category: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """浏览社区题库（仅返回已上架的题库）"""
    service = QuestionBankService(db)
    banks, total = await service.list_community_banks(
        page=page,
        page_size=page_size,
        category=category,
    )
    
    return ResponseModel(
        message="获取成功",
        data=PaginatedResponse(
            items=[QuestionBankResponse.model_validate(b) for b in banks],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=(total + page_size - 1) // page_size
        )
    )


@router.post("/banks/{bank_id}/apply-community", response_model=ResponseModel[QuestionBankResponse])
async def apply_community(
    bank_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """申请将自己的题库上架社区"""
    service = QuestionBankService(db)
    bank = await service.apply_community(bank_id, current_user.id)
    
    if not bank:
        raise HTTPException(status_code=404, detail="题库不存在")
    
    return ResponseModel(
        message="申请已提交",
        data=QuestionBankResponse.model_validate(bank)
    )


@router.post("/banks/{bank_id}/review-community", response_model=ResponseModel[QuestionBankResponse])
async def review_community(
    bank_id: str,
    request: CommunityReviewRequest,
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """管理员审核社区题库申请（approve/reject/delist）"""
    if request.action not in ("approve", "reject", "delist"):
        raise HTTPException(status_code=400, detail="无效的操作，可选: approve/reject/delist")
    
    service = QuestionBankService(db)
    bank = await service.review_community(bank_id, request.action)
    
    if not bank:
        raise HTTPException(status_code=404, detail="题库不存在")
    
    return ResponseModel(
        message="审核完成",
        data=QuestionBankResponse.model_validate(bank)
    )


@router.get("/community/pending", response_model=ResponseModel[PaginatedResponse[QuestionBankResponse]])
async def list_pending_banks(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """管理员查看待审核题库列表"""
    service = QuestionBankService(db)
    banks, total = await service.list_pending_banks(page=page, page_size=page_size)
    
    return ResponseModel(
        message="获取成功",
        data=PaginatedResponse(
            items=[QuestionBankResponse.model_validate(b) for b in banks],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=(total + page_size - 1) // page_size
        )
    )


@router.post("/community/banks/{bank_id}/copy", response_model=ResponseModel[QuestionBankResponse])
async def copy_community_bank(
    bank_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """复制社区题库到我的题库（深拷贝，包含所有题目）"""
    service = QuestionBankService(db)
    new_bank = await service.copy_community_bank(bank_id, current_user.id)
    
    if not new_bank:
        raise HTTPException(status_code=404, detail="社区题库不存在")
    
    return ResponseModel(
        message="复制成功",
        data=QuestionBankResponse.model_validate(new_bank)
    )


# ==================== 题目 API ====================

@router.get("", response_model=ResponseModel[PaginatedResponse[QuestionResponse]])
async def list_questions(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    bank_id: str = Query(..., description="所属题库ID"),
    question_type: Optional[str] = Query(None, alias="type"),
    category: Optional[str] = None,
    difficulty: Optional[str] = None,
    status_filter: Optional[str] = Query(None, alias="status"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取题目列表（需指定 bank_id，校验访问权限）"""
    # 校验用户是否有权访问该题库
    bank_service = QuestionBankService(db)
    bank = await bank_service.get_accessible_bank(bank_id, current_user.id)
    if not bank:
        raise HTTPException(status_code=404, detail="题库不存在或无权访问")
    
    service = QuestionService(db)
    questions, total = await service.list(
        page=page,
        page_size=page_size,
        bank_id=bank_id,
        category=category,
        difficulty=difficulty,
        question_type=question_type,
        status=status_filter
    )
    
    return ResponseModel(
        message="获取成功",
        data=PaginatedResponse(
            items=[QuestionResponse.model_validate(q) for q in questions],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=(total + page_size - 1) // page_size
        )
    )


@router.post("", response_model=ResponseModel[QuestionResponse])
async def create_question(
    question_data: QuestionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """创建题目（校验题库归属）"""
    bank_service = QuestionBankService(db)
    bank = await bank_service.get_own_bank(question_data.bank_id, current_user.id)
    if not bank:
        raise HTTPException(status_code=400, detail="所属题库不存在或无权操作")
    
    service = QuestionService(db)
    question = await service.create(
        data=question_data.model_dump(),
        created_by=current_user.id
    )
    
    return ResponseModel(
        message="创建成功",
        data=QuestionResponse.model_validate(question)
    )


@router.post("/batch", response_model=ResponseModel[QuestionBatchCreateResponse])
async def batch_create_questions(
    batch_data: QuestionBatchCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """批量创建题目（1-100 条，校验题库归属）"""
    bank_service = QuestionBankService(db)
    bank = await bank_service.get_own_bank(batch_data.bank_id, current_user.id)
    if not bank:
        raise HTTPException(status_code=400, detail="所属题库不存在或无权操作")

    service = QuestionService(db)
    items = [q.model_dump() for q in batch_data.questions]
    questions = await service.batch_create(
        items=items,
        bank_id=batch_data.bank_id,
        created_by=current_user.id
    )

    result = [QuestionResponse.model_validate(q) for q in questions]
    return ResponseModel(
        message=f"成功创建 {len(result)} 道题目",
        data=QuestionBatchCreateResponse(total=len(result), questions=result)
    )


@router.get("/{question_id}", response_model=ResponseModel[QuestionDetailResponse])
async def get_question(
    question_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取题目详情（校验访问权限）"""
    service = QuestionService(db)
    question = await service.get_by_id(question_id)
    
    if not question:
        raise HTTPException(status_code=404, detail="题目不存在")
    
    # 校验用户是否有权访问该题目所属题库
    bank_service = QuestionBankService(db)
    bank = await bank_service.get_accessible_bank(question.bank_id, current_user.id)
    if not bank:
        raise HTTPException(status_code=404, detail="题目不存在或无权访问")
    
    return ResponseModel(
        message="获取成功",
        data=QuestionDetailResponse.model_validate(question)
    )


@router.put("/{question_id}", response_model=ResponseModel[QuestionResponse])
async def update_question(
    question_id: str,
    question_data: QuestionUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """更新题目（校验题库归属）"""
    service = QuestionService(db)
    question = await service.get_by_id(question_id)
    
    if not question:
        raise HTTPException(status_code=404, detail="题目不存在")
    
    # 校验题目所属题库是否为当前用户的
    bank_service = QuestionBankService(db)
    bank = await bank_service.get_own_bank(question.bank_id, current_user.id)
    if not bank:
        raise HTTPException(status_code=403, detail="无权操作该题目")
    
    question = await service.update(
        question_id=question_id,
        data=question_data.model_dump(exclude_unset=True)
    )
    
    return ResponseModel(
        message="更新成功",
        data=QuestionResponse.model_validate(question)
    )


@router.delete("/{question_id}", response_model=ResponseModel)
async def delete_question(
    question_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """删除题目（校验题库归属）"""
    service = QuestionService(db)
    question = await service.get_by_id(question_id)
    
    if not question:
        raise HTTPException(status_code=404, detail="题目不存在")
    
    # 校验题目所属题库是否为当前用户的
    bank_service = QuestionBankService(db)
    bank = await bank_service.get_own_bank(question.bank_id, current_user.id)
    if not bank:
        raise HTTPException(status_code=403, detail="无权操作该题目")
    
    success = await service.delete(question_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="题目不存在")
    
    return ResponseModel(message="删除成功")


# ==================== 文件提取题目 API ====================

@router.post("/extract")
async def extract_questions_from_file(
    file: UploadFile = File(..., description="上传的文件（支持 .txt, .md, .docx, .pdf）"),
    bank_id: str = Form(..., description="目标题库ID"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    从文件中提取面试题目（SSE 流式返回）
    
    上传一个包含面试题的文件，后端使用 LLM 提取题目并以 SSE 事件流逐步返回。
    同时在服务端缓存提取结果，前端刷新页面后可通过 task_id 恢复。
    
    **支持的文件类型**: .txt, .md, .docx, .pdf
    **最大文件大小**: 50MB
    
    **SSE 事件类型**:
    - `task_created`: 任务创建成功，返回 task_id
    - `chunk_progress`: 每处理完一个文本块，返回本批提取的题目
    - `completed`: 全部提取完成，返回所有题目
    - `error`: 出错
    """
    # 验证题库归属
    bank_service = QuestionBankService(db)
    bank = await bank_service.get_own_bank(bank_id, current_user.id)
    if not bank:
        raise HTTPException(status_code=400, detail="目标题库不存在或无权操作")

    # 读取文件内容
    file_content = await file.read()
    filename = file.filename or "unknown.txt"

    # 创建提取服务并返回 SSE 流
    extraction_service = QuestionExtractionService()

    async def event_generator():
        async for event in extraction_service.extract_from_file(
            file_content=file_content,
            filename=filename,
            bank_id=bank_id,
        ):
            event_type = event.get("event", "message")
            data = json.dumps(event.get("data", {}), ensure_ascii=False)
            yield f"event: {event_type}\ndata: {data}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/extract/tasks", response_model=ResponseModel[List[ExtractionTaskListItem]])
async def list_extraction_tasks(
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
):
    """获取提取任务列表"""
    service = QuestionExtractionService()
    tasks = service.list_tasks(limit=limit)
    
    items = []
    for t in tasks:
        items.append(ExtractionTaskListItem(
            task_id=t["task_id"],
            filename=t["filename"],
            bank_id=t["bank_id"],
            status=t["status"],
            total_chunks=t["total_chunks"],
            processed_chunks=t["processed_chunks"],
            progress=t.get("progress", 0),
            total_questions=len(t.get("questions", [])),
            error=t.get("error"),
            created_at=t["created_at"],
            updated_at=t["updated_at"],
        ))
    
    return ResponseModel(message="获取成功", data=items)


@router.get("/extract/tasks/{task_id}", response_model=ResponseModel[ExtractionTaskResponse])
async def get_extraction_task(
    task_id: str,
    current_user: User = Depends(get_current_user),
):
    """
    获取提取任务详情（含完整题目数据）
    
    前端刷新页面后可通过此接口恢复之前的提取结果。
    """
    service = QuestionExtractionService()
    task = service.get_task(task_id)
    
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    return ResponseModel(
        message="获取成功",
        data=ExtractionTaskResponse(
            task_id=task.task_id,
            filename=task.filename,
            bank_id=task.bank_id,
            status=task.status,
            total_chunks=task.total_chunks,
            processed_chunks=task.processed_chunks,
            progress=task.progress,
            questions=task.questions,
            error=task.error,
            created_at=task.created_at,
            updated_at=task.updated_at,
        )
    )


@router.post("/extract/import", response_model=ResponseModel[List[QuestionResponse]])
async def batch_import_extracted_questions(
    request: BatchImportRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    将提取的题目批量导入到题库
    
    从已完成的提取任务中选择题目，正式写入数据库。
    """
    extraction_service = QuestionExtractionService()
    task = extraction_service.get_task(request.task_id)
    
    if not task:
        raise HTTPException(status_code=404, detail="提取任务不存在")
    
    if not task.questions:
        raise HTTPException(status_code=400, detail="该任务没有提取到题目")
    
    # 验证题库归属
    bank_service = QuestionBankService(db)
    bank = await bank_service.get_own_bank(request.bank_id, current_user.id)
    if not bank:
        raise HTTPException(status_code=400, detail="目标题库不存在或无权操作")
    
    # 筛选要导入的题目
    if request.question_indices:
        questions_to_import = []
        for idx in request.question_indices:
            if 0 <= idx < len(task.questions):
                questions_to_import.append(task.questions[idx])
    else:
        questions_to_import = task.questions
    
    if not questions_to_import:
        raise HTTPException(status_code=400, detail="没有可导入的题目")
    
    # 批量写入数据库
    question_service = QuestionService(db)
    created_questions = []
    
    for q_data in questions_to_import:
        q_data["bank_id"] = request.bank_id
        question = await question_service.create(
            data=q_data,
            created_by=current_user.id
        )
        created_questions.append(QuestionResponse.model_validate(question))
    
    return ResponseModel(
        message=f"成功导入 {len(created_questions)} 道题目",
        data=created_questions
    )
