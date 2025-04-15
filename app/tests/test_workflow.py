from unittest.mock import AsyncMock, patch

import pytest
import pytest_asyncio
from httpx import AsyncClient

# Patch get_current_user_id to always return a test user
from app.core.security import get_current_user_id
from app.main import app

app.dependency_overrides[get_current_user_id] = lambda: "test-user-id"

# Patch get_supabase_client to return a mock (avoid real DB calls)
from app.db.supabase_client import get_supabase_client

app.dependency_overrides[get_supabase_client] = lambda: AsyncMock()


@pytest_asyncio.fixture
def async_client():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


def workflow_payload():
    return {
        "name": "Test Workflow",
        "description": "A test workflow",
        "steps": [
            {"id": "step1", "type": "plugin", "config_id": "plugin-1", "parameters": {}}
        ],
    }


@patch(
    "app.services.workflow_service.WorkflowService.create_workflow",
    new_callable=AsyncMock,
    return_value={
        "id": "wf-1",
        "name": "Test Workflow",
        "user_id": "test-user-id",
        "description": "A test workflow",
        "steps": [],
        "created_at": None,
        "updated_at": None,
    },
)
@pytest.mark.asyncio
async def test_create_workflow(mock_create, async_client):
    response = await async_client.post("/api/v1/workflows/", json=workflow_payload())
    assert response.status_code in (201, 401, 403)


@patch(
    "app.services.workflow_service.WorkflowService.list_workflows",
    new_callable=AsyncMock,
    return_value=[],
)
@pytest.mark.asyncio
async def test_list_workflows(mock_list, async_client):
    response = await async_client.get("/api/v1/workflows/")
    assert response.status_code in (200, 401, 403)


@patch(
    "app.services.workflow_service.WorkflowService.get_workflow",
    new_callable=AsyncMock,
    return_value=None,
)
@pytest.mark.asyncio
async def test_get_workflow_not_found(mock_get, async_client):
    response = await async_client.get("/api/v1/workflows/nonexistent-id")
    assert response.status_code in (404, 401, 403)


@patch(
    "app.services.workflow_service.WorkflowService.update_workflow",
    new_callable=AsyncMock,
    return_value=None,
)
@pytest.mark.asyncio
async def test_update_workflow_not_found(mock_update, async_client):
    payload = {"name": "Updated Name"}
    response = await async_client.put("/api/v1/workflows/nonexistent-id", json=payload)
    assert response.status_code in (404, 401, 403)


@patch(
    "app.services.workflow_service.WorkflowService.delete_workflow",
    new_callable=AsyncMock,
    return_value=None,
)
@pytest.mark.asyncio
async def test_delete_workflow_not_found(mock_delete, async_client):
    response = await async_client.delete("/api/v1/workflows/nonexistent-id")
    assert response.status_code in (404, 401, 403)


@patch(
    "app.services.workflow_service.WorkflowService.run_workflow",
    new_callable=AsyncMock,
    return_value={"status": "success", "output": {"message": "ok"}, "logs": []},
)
@pytest.mark.asyncio
async def test_run_workflow(mock_run, async_client):
    payload = {"inputs": {"x": 1}}
    response = await async_client.post("/api/v1/workflows/test-id/run", json=payload)
    assert response.status_code in (200, 401, 403)


@patch(
    "app.services.workflow_service.WorkflowService.run_workflow",
    new_callable=AsyncMock,
    side_effect=Exception("Run failed"),
)
@pytest.mark.asyncio
async def test_run_workflow_error(mock_run, async_client):
    payload = {"inputs": {"x": 1}}
    response = await async_client.post("/api/v1/workflows/test-id/run", json=payload)
    assert response.status_code in (500, 401, 403)
