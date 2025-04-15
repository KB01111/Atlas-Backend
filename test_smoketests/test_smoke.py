import pytest
import pytest_asyncio
from httpx import AsyncClient

from app.main import app


@pytest_asyncio.fixture(scope="function")
async def async_client():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.mark.asyncio
async def test_smoke(async_client):
    response = await async_client.get("/api/v1/agents/")
    assert response.status_code in (200, 400, 401, 403)
