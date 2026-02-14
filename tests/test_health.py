"""
健康检查测试
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    """测试健康检查端点"""
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


@pytest.mark.asyncio
async def test_root(client: AsyncClient):
    """测试根路径"""
    response = await client.get("/api/v1/")
    assert response.status_code == 200
    data = response.json()
    assert "version" in data
