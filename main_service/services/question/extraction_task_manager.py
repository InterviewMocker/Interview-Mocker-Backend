"""
题目提取任务管理器 - 服务端缓存中间结果

将提取任务的状态和结果持久化到本地 JSON 文件，
确保前端刷新页面后仍可恢复之前的提取进度和结果。

存储路径: data/extraction_tasks/{task_id}.json
"""
import json
import logging
import os
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

TASKS_DIR = Path("data/extraction_tasks")


@dataclass
class ExtractionTask:
    """提取任务"""
    task_id: str
    filename: str
    bank_id: str
    status: str = "pending"  # pending | processing | completed | failed
    total_chunks: int = 0
    processed_chunks: int = 0
    questions: List[Dict[str, Any]] = field(default_factory=list)
    error: Optional[str] = None
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)

    @property
    def progress(self) -> float:
        if self.total_chunks == 0:
            return 0.0
        return round(self.processed_chunks / self.total_chunks * 100, 1)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["progress"] = self.progress
        return d


class ExtractionTaskManager:
    """任务持久化管理"""

    def __init__(self):
        TASKS_DIR.mkdir(parents=True, exist_ok=True)

    def _task_path(self, task_id: str) -> Path:
        return TASKS_DIR / f"{task_id}.json"

    def save(self, task: ExtractionTask) -> None:
        """保存任务到磁盘"""
        task.updated_at = time.time()
        path = self._task_path(task.task_id)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(task.to_dict(), f, ensure_ascii=False, indent=2)

    def load(self, task_id: str) -> Optional[ExtractionTask]:
        """从磁盘加载任务"""
        path = self._task_path(task_id)
        if not path.exists():
            return None
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            data.pop("progress", None)
            return ExtractionTask(**data)
        except Exception as e:
            logger.error(f"加载任务失败 ({task_id}): {e}")
            return None

    def add_questions(self, task: ExtractionTask, new_questions: List[Dict]) -> None:
        """追加提取到的题目并保存"""
        task.questions.extend(new_questions)
        task.processed_chunks += 1
        self.save(task)

    def mark_completed(self, task: ExtractionTask) -> None:
        """标记任务完成"""
        task.status = "completed"
        self.save(task)

    def mark_failed(self, task: ExtractionTask, error: str) -> None:
        """标记任务失败"""
        task.status = "failed"
        task.error = error
        self.save(task)

    def delete(self, task_id: str) -> bool:
        """删除任务文件"""
        path = self._task_path(task_id)
        if path.exists():
            os.remove(path)
            return True
        return False

    def list_tasks(self, limit: int = 50) -> List[Dict]:
        """列出最近的任务"""
        tasks = []
        for f in sorted(TASKS_DIR.glob("*.json"), key=os.path.getmtime, reverse=True)[:limit]:
            try:
                with open(f, "r", encoding="utf-8") as fp:
                    tasks.append(json.load(fp))
            except Exception:
                continue
        return tasks
