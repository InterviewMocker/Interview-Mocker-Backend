"""
认证授权测试
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register(client: AsyncClient):
    """测试用户注册"""
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "TestPass123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["data"]["username"] == "testuser"


@pytest.mark.asyncio
async def test_register_duplicate_username(client: AsyncClient):
    """测试重复用户名注册"""
    # 首次注册
    await client.post(
        "/api/v1/auth/register",
        json={
            "username": "testuser",
            "email": "test1@example.com",
            "password": "TestPass123"
        }
    )
    
    # 重复注册
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "username": "testuser",
            "email": "test2@example.com",
            "password": "TestPass123"
        }
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_login(client: AsyncClient):
    """测试用户登录"""
    # 先注册
    await client.post(
        "/api/v1/auth/register",
        json={
            "username": "logintest",
            "email": "login@example.com",
            "password": "TestPass123"
        }
    )
    
    # 登录
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "username": "logintest",
            "password": "TestPass123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data["data"]
    assert "refresh_token" in data["data"]


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient):
    """测试错误密码登录"""
    # 先注册
    await client.post(
        "/api/v1/auth/register",
        json={
            "username": "wrongpasstest",
            "email": "wrong@example.com",
            "password": "TestPass123"
        }
    )
    
    # 登录（错误密码）
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "username": "wrongpasstest",
            "password": "WrongPass123"
        }
    )
    assert response.status_code == 401
