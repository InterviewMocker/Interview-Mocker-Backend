"""
主服务 HTTP 客户端 - 数字人服务调用主服务的接口
"""
from typing import Optional, Dict, Any

import httpx

from shared.config.settings import get_shared_settings

settings = get_shared_settings()


class MainServiceClient:
    """调用主服务的 HTTP 客户端"""
    
    def __init__(self):
        self.base_url = settings.MAIN_SERVICE_URL
        self.timeout = httpx.Timeout(30.0)
        self.headers = {
            "X-Service-Token": settings.INTERNAL_SERVICE_TOKEN,
            "Content-Type": "application/json"
        }
    
    async def _request(
        self,
        method: str,
        endpoint: str,
        json: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """发送 HTTP 请求"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.request(
                method=method,
                url=f"{self.base_url}{endpoint}",
                headers=self.headers,
                json=json,
                params=params
            )
            response.raise_for_status()
            return response.json()
    
    # ==================== 面试会话相关 ====================
    
    async def start_interview_session(
        self,
        user_id: str,
        position_id: str,
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """在主服务创建面试会话"""
        return await self._request(
            "POST",
            "/api/v1/interviews/sessions/start",
            json={
                "user_id": user_id,
                "position_id": position_id,
                "config": config
            }
        )
    
    async def update_session_status(
        self,
        session_id: str,
        status: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """更新面试会话状态"""
        return await self._request(
            "PATCH",
            f"/api/v1/interviews/sessions/{session_id}/status",
            json={
                "status": status,
                "metadata": metadata or {}
            }
        )
    
    async def complete_interview(
        self,
        session_id: str,
        summary: Dict[str, Any]
    ) -> Dict[str, Any]:
        """完成面试"""
        return await self._request(
            "POST",
            f"/api/v1/interviews/sessions/{session_id}/complete",
            json={"summary": summary}
        )
    
    # ==================== 题目相关 ====================
    
    async def get_next_question(
        self,
        session_id: str,
        context: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """获取下一个问题"""
        try:
            result = await self._request(
                "POST",
                "/api/v1/questions/next",
                json={
                    "session_id": session_id,
                    "context": context
                }
            )
            return result.get("data")
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return None  # 没有更多问题
            raise
    
    async def get_follow_up_question(
        self,
        session_id: str,
        parent_question_id: str,
        user_answer_summary: str
    ) -> Optional[Dict[str, Any]]:
        """获取追问题目"""
        try:
            result = await self._request(
                "POST",
                "/api/v1/questions/follow-up",
                json={
                    "session_id": session_id,
                    "parent_question_id": parent_question_id,
                    "user_answer_summary": user_answer_summary
                }
            )
            return result.get("data")
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return None
            raise
    
    # ==================== 答案相关 ====================
    
    async def submit_answer(
        self,
        session_id: str,
        question_id: str,
        answer: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """提交用户答案"""
        result = await self._request(
            "POST",
            "/api/v1/interviews/answers",
            json={
                "session_id": session_id,
                "question_id": question_id,
                "answer": answer,
                "metadata": metadata or {}
            }
        )
        return result.get("data", {})
    
    async def trigger_evaluation(
        self,
        session_id: str,
        qa_record_id: str,
        require_feedback: bool = True
    ) -> Dict[str, Any]:
        """触发实时评估"""
        result = await self._request(
            "POST",
            "/api/v1/evaluations/realtime",
            json={
                "session_id": session_id,
                "qa_record_id": qa_record_id,
                "require_feedback": require_feedback
            }
        )
        return result.get("data", {})
    
    # ==================== 知识库相关 ====================
    
    async def search_knowledge(
        self,
        query: str,
        position_id: str,
        top_k: int = 5
    ) -> list:
        """RAG 知识检索"""
        result = await self._request(
            "POST",
            "/api/v1/knowledge/search",
            json={
                "query": query,
                "position_id": position_id,
                "top_k": top_k
            }
        )
        return result.get("data", {}).get("results", [])
