from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from loguru import logger

from app.core.security import get_current_user_id
from app.db.supabase_client import SupabaseClientError
from app.models.workflow import (
    WorkflowCreate,
    WorkflowOut,
    WorkflowRunRequest,
    WorkflowRunResult,
    WorkflowUpdate,
)
from app.services.workflow_service import WorkflowService, WorkflowServiceError

# Placeholder for user dependency (replace with real auth/user extraction)
# def get_current_user():
#     # TODO: Replace with actual authentication/authorization logic
#     # Should return a user object or dict with at least 'id'
#     return {"id": "test-user-id"}

router = APIRouter(prefix="/api/v1/workflows", tags=["workflows"])

@router.post("/", response_model=WorkflowOut, status_code=status.HTTP_201_CREATED)
async def create_workflow(
    workflow: WorkflowCreate,
    user_id: str = Depends(get_current_user_id)
):
    try:
        created = await WorkflowService.create_workflow(user_id, workflow)
        return created
    except (WorkflowServiceError, SupabaseClientError) as e:
        logger.error(f"Workflow creation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[WorkflowOut])
async def list_workflows(user_id: str = Depends(get_current_user_id)):
    try:
        return await WorkflowService.list_workflows(user_id)
    except (WorkflowServiceError, SupabaseClientError) as e:
        logger.error(f"Workflow listing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{workflow_id}", response_model=WorkflowOut)
async def get_workflow(workflow_id: str, user_id: str = Depends(get_current_user_id)):
    try:
        workflow = await WorkflowService.get_workflow(workflow_id, user_id)
        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")
        return workflow
    except (WorkflowServiceError, SupabaseClientError) as e:
        logger.error(f"Workflow fetch failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{workflow_id}", response_model=WorkflowOut)
async def update_workflow(
    workflow_id: str,
    workflow: WorkflowUpdate,
    user_id: str = Depends(get_current_user_id)
):
    try:
        updated = await WorkflowService.update_workflow(workflow_id, user_id, workflow)
        if not updated:
            raise HTTPException(status_code=404, detail="Workflow not found")
        return updated
    except (WorkflowServiceError, SupabaseClientError) as e:
        logger.error(f"Workflow update failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{workflow_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_workflow(workflow_id: str, user_id: str = Depends(get_current_user_id)):
    try:
        deleted = await WorkflowService.delete_workflow(workflow_id, user_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Workflow not found")
        return None
    except (WorkflowServiceError, SupabaseClientError) as e:
        logger.error(f"Workflow deletion failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{workflow_id}/run", response_model=WorkflowRunResult, status_code=200)
async def run_workflow(
    workflow_id: str,
    run_request: WorkflowRunRequest,
    user_id: str = Depends(get_current_user_id)
):
    try:
        result = await WorkflowService.run_workflow(workflow_id, user_id, run_request)
        return result
    except (WorkflowServiceError, SupabaseClientError) as e:
        logger.error(f"Workflow run failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
