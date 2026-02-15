"""
题目提取服务 - 使用 LLM 从文档中提取面试题

核心流程:
1. 接收文件 → 提取文本
2. 文本分块（避免超过 LLM 上下文窗口）
3. 逐块调用 LLM 提取题目（JSON 格式）
4. 每提取一批就通过 SSE 推送给前端 + 持久化到本地
5. 全部完成后标记任务完成
"""
import json
import logging
import re
import uuid
from typing import Any, AsyncGenerator, Dict, List, Optional, Tuple

from shared.utils.file_parser import extract_text_from_file, is_supported_file
from shared.utils.llm import LLMClient, LLMRequestOptions, get_llm_client
from shared.utils.text_chunker import split_text_into_chunks

from .extraction_task_manager import ExtractionTask, ExtractionTaskManager

from shared.utils.json_parser import StreamJsonParser

logger = logging.getLogger(__name__)

EXTRACTION_SYSTEM_PROMPT = """你是一个专业的面试题提取助手。你的任务是从给定的文本中识别并提取面试题目。

**提取规则：**
1. 识别文本中所有的面试题目（包括技术题、场景题、算法题、行为题等）
2. 为每道题推断合适的分类和难度
3. 每道题必须包含 reference_answer（参考答案）和 answer_key_points（答案要点）：
   - 如果文本中已有答案，直接提取并整理
   - 如果文本中没有答案，请根据你的专业知识为该题目生成一份简明的参考答案和 3-5 个答案要点
4. 如果没有明显的面试题，什么都不输出

**输出格式（JSON Lines）：**
请将每道题目输出为一个独立的 JSON 对象，不要包含 markdown 代码块标记，不要包含外层的数组或者是 "questions" 字段。直接连续输出 JSON 对象即可。

例如：
{"title": "题目1", "content": "...", "type": "technical", "difficulty": "medium", "reference_answer": "...", "answer_key_points": ["..."]}
{"title": "题目2", "content": "...", "type": "behavioral", "difficulty": "easy", "reference_answer": "...", "answer_key_points": ["..."]}

**字段说明：**
- type 只能是: technical, scenario, algorithm, behavioral
- difficulty 只能是: easy, medium, hard
- difficulty_score 范围: 1-10
- reference_answer 和 answer_key_points 是必填字段，不能省略
"""

CHUNK_PROMPT_TEMPLATE = """请从以下文本中提取面试题目：

---文本内容开始---
{text}
---文本内容结束---

请严格按照 JSON Lines 格式（每行一个 JSON 对象）返回提取结果。"""


class QuestionExtractionService:
    """题目提取服务"""

    def __init__(self, llm_client: Optional[LLMClient] = None):
        self.llm = llm_client or get_llm_client()
        self.task_manager = ExtractionTaskManager()

    async def extract_from_file(
        self,
        file_content: bytes,
        filename: str,
        bank_id: str,
        max_chunk_chars: int = 6000,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        从文件中提取题目，以 SSE 事件流形式逐步返回。
        """
        task_id = str(uuid.uuid4())

        if not is_supported_file(filename):
            yield {
                "event": "error",
                "data": {"message": f"不支持的文件类型: {filename}"}
            }
            return

        # 1. 提取文本
        try:
            text = await extract_text_from_file(file_content, filename)
        except (ValueError, RuntimeError) as e:
            yield {"event": "error", "data": {"message": str(e)}}
            return

        if not text.strip():
            yield {"event": "error", "data": {"message": "文件内容为空"}}
            return

        # 2. 分块
        chunks = split_text_into_chunks(text, max_chars=max_chunk_chars)

        # 3. 创建任务
        task = ExtractionTask(
            task_id=task_id,
            filename=filename,
            bank_id=bank_id,
            status="processing",
            total_chunks=len(chunks),
        )
        self.task_manager.save(task)

        yield {
            "event": "task_created",
            "data": {
                "task_id": task_id,
                "filename": filename,
                "total_chunks": len(chunks),
                "text_length": len(text),
            }
        }

        # 4. 逐块提取
        try:
            for i, chunk in enumerate(chunks):
                chunk_num = i + 1
                logger.info(f"[{task_id}] 提取第 {chunk_num}/{len(chunks)} 块")

                chunk_questions = []
                async for question in self._extract_questions_from_chunk_stream(chunk):
                    chunk_questions.append(question)
                    self.task_manager.add_questions(task, [question])
                    
                    # 实时推送每道题
                    yield {
                        "event": "chunk_progress",
                        "data": {
                            "task_id": task_id,
                            "chunk": chunk_num,
                            "total_chunks": len(chunks),
                            "progress": task.progress,
                            "new_questions": [question],
                            "total_questions_so_far": len(task.questions),
                        }
                    }

                if not chunk_questions:
                    logger.info(f"[{task_id}] 第 {chunk_num} 块未提取到题目")
                
                # 更新进度：本块处理完成
                self.task_manager.increment_processed_chunks(task)

            # 5. 标记完成
            self.task_manager.mark_completed(task)

            yield {
                "event": "completed",
                "data": {
                    "task_id": task_id,
                    "total_questions": len(task.questions),
                    "questions": task.questions,
                }
            }

        except Exception as e:
            error_msg = f"提取过程出错: {e}"
            logger.error(f"[{task_id}] {error_msg}")
            self.task_manager.mark_failed(task, error_msg)
            yield {
                "event": "error",
                "data": {
                    "task_id": task_id,
                    "message": error_msg,
                    "partial_questions": task.questions,
                }
            }

    async def _extract_questions_from_chunk_stream(self, text: str) -> AsyncGenerator[Dict[str, Any], None]:
        """
        从文本块中提取题目。
        注意：为了稳定性，目前使用非流式 LLM 调用，但在后端模拟流式输出给前端。
        """
        prompt = CHUNK_PROMPT_TEMPLATE.format(text=text)
        options = LLMRequestOptions(
            temperature=0.2,
            max_tokens=8192,
        )
        
        logger.info(f"========== 开始 LLM 提取 (非流式) ==========")
        logger.info(f"Prompt 长度: {len(prompt)} 字符")
        
        try:
            # 1. 非流式调用 LLM (获取完整响应)
            response = await self.llm.chat(
                prompt=prompt,
                system_prompt=EXTRACTION_SYSTEM_PROMPT,
                options=options,
            )
            
            full_response = response.content
            logger.info(f"========== LLM 响应接收完成 ==========")
            logger.info(f"响应长度: {len(full_response)} 字符")
            logger.info(f"LLM 响应内容:\n{full_response[:2000]}")
            
            # 2. 解析 JSON 并逐个推送
            parser = StreamJsonParser()
            new_objs = parser.feed(full_response)
            
            count = 0
            for obj in new_objs:
                count += 1
                logger.info(f"解析到题目 {count}: {obj.get('title', 'N/A')[:50]}")
                validated = self._validate_question(obj)
                yield validated
                
            if parser.buffer.strip():
                logger.warning(f"解析器剩余未处理内容: {parser.buffer[:500]}...")
                
        except Exception as e:
            import traceback
            error_type = type(e).__name__
            logger.error(f"LLM 提取出错 ({error_type}): {e}")
            logger.error(f"完整堆栈追踪:\n{traceback.format_exc()}")
            raise

    async def _extract_questions_from_chunk(self, text: str) -> Tuple[List[Dict[str, Any]], Optional[str]]:
        """保留旧方法用于兼容或测试 (非流式)"""
        # ... (implementation omitted as we are moving to stream)
        # 为保持兼容性，我们可以让它调用流式方法并收集结果
        questions = []
        async for q in self._extract_questions_from_chunk_stream(text):
            questions.append(q)
        return questions, None


    @staticmethod
    def _try_recover_truncated_json(error_text: str) -> List[Dict[str, Any]]:
        """尝试从 LLM 截断的 JSON 响应中恢复已完整的题目对象"""
        # 从错误信息中提取原始内容
        match = re.search(r"原始内容: (.+)", error_text, re.DOTALL)
        if not match:
            return []

        raw = match.group(1).strip()
        # 去除 markdown 代码块标记
        raw = re.sub(r"^```(?:json)?\s*\n?", "", raw)
        raw = re.sub(r"\n?\s*```$", "", raw)

        # 策略: 逐个查找完整的 JSON 对象 {...}
        questions = []
        depth = 0
        obj_start = -1

        for i, ch in enumerate(raw):
            if ch == "{":
                if depth == 0:
                    obj_start = i
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0 and obj_start >= 0:
                    candidate = raw[obj_start:i + 1]
                    try:
                        obj = json.loads(candidate)
                        # 只保留看起来像题目的对象（有 title 字段）
                        if isinstance(obj, dict) and "title" in obj:
                            questions.append(obj)
                    except json.JSONDecodeError:
                        pass
                    obj_start = -1

        return questions

    @staticmethod
    def _validate_question(q: Dict[str, Any]) -> Dict[str, Any]:
        """校验并规范化题目数据"""
        valid_types = {"technical", "scenario", "algorithm", "behavioral"}
        valid_difficulties = {"easy", "medium", "hard"}

        q_type = q.get("type", "technical")
        if q_type not in valid_types:
            q_type = "technical"

        difficulty = q.get("difficulty", "medium")
        if difficulty not in valid_difficulties:
            difficulty = "medium"

        score = q.get("difficulty_score")
        if score is not None:
            try:
                score = max(1, min(10, int(score)))
            except (ValueError, TypeError):
                score = 5

        return {
            "title": str(q.get("title", "未命名题目"))[:200],
            "content": str(q.get("content", q.get("title", ""))),
            "type": q_type,
            "category": q.get("category"),
            "difficulty": difficulty,
            "difficulty_score": score,
            "tags": q.get("tags") if isinstance(q.get("tags"), list) else None,
            "reference_answer": q.get("reference_answer"),
            "answer_key_points": q.get("answer_key_points") if isinstance(q.get("answer_key_points"), list) else None,
        }

    def get_task(self, task_id: str) -> Optional[ExtractionTask]:
        """获取任务状态和结果"""
        return self.task_manager.load(task_id)

    def list_tasks(self, limit: int = 50) -> List[Dict]:
        """列出最近的提取任务"""
        return self.task_manager.list_tasks(limit)
