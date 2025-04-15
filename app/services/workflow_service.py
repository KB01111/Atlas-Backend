from typing import List, Optional

from langgraph.graph import StateGraph
from loguru import logger

from app.db.supabase_client import SupabaseClientError, get_supabase_client
from app.models.workflow import (
    WorkflowCreate,
    WorkflowRunRequest,
    WorkflowRunResult,
    WorkflowUpdate,
)

WORKFLOW_TABLE = "workflows"

class WorkflowServiceError(Exception):
    """Custom exception for WorkflowService errors."""
    pass

class WorkflowService:
    @staticmethod
    async def create_workflow(user_id: str, workflow: WorkflowCreate) -> dict:
        """
        Create a new workflow for a user.
        Raises WorkflowServiceError or SupabaseClientError on failure.
        """
        try:
            data = workflow.dict()
            data["user_id"] = user_id
            supabase = get_supabase_client()
            res = supabase.table(WORKFLOW_TABLE).insert(data).execute()
            if res.data:
                return res.data[0]
            logger.error(f"Supabase insert error: {res.error}")
            raise SupabaseClientError(res.error)
        except Exception as e:
            logger.error(f"Error creating workflow: {e}")
            raise WorkflowServiceError("Failed to create workflow")

    @staticmethod
    async def get_workflow(workflow_id: str, user_id: str) -> Optional[dict]:
        """
        Retrieve a workflow by ID for a user.
        Returns None if not found. Raises WorkflowServiceError on failure.
        """
        try:
            supabase = get_supabase_client()
            res = supabase.table(WORKFLOW_TABLE).select("*").eq("id", workflow_id).eq("user_id", user_id).single().execute()
            return res.data if res.data else None
        except Exception as e:
            logger.error(f"Error fetching workflow: {e}")
            raise WorkflowServiceError("Failed to fetch workflow")

    @staticmethod
    async def update_workflow(workflow_id: str, user_id: str, workflow: WorkflowUpdate) -> Optional[dict]:
        """
        Update a workflow for a user.
        Returns updated workflow or None. Raises WorkflowServiceError on failure.
        """
        try:
            data = workflow.dict(exclude_unset=True)
            supabase = get_supabase_client()
            res = supabase.table(WORKFLOW_TABLE).update(data).eq("id", workflow_id).eq("user_id", user_id).execute()
            return res.data[0] if res.data else None
        except Exception as e:
            logger.error(f"Error updating workflow: {e}")
            raise WorkflowServiceError("Failed to update workflow")

    @staticmethod
    async def delete_workflow(workflow_id: str, user_id: str) -> bool:
        """
        Delete a workflow for a user. Returns True if deleted.
        Raises WorkflowServiceError on failure.
        """
        try:
            supabase = get_supabase_client()
            res = supabase.table(WORKFLOW_TABLE).delete().eq("id", workflow_id).eq("user_id", user_id).execute()
            return bool(res.data)
        except Exception as e:
            logger.error(f"Error deleting workflow: {e}")
            raise WorkflowServiceError("Failed to delete workflow")

    @staticmethod
    async def list_workflows(user_id: str) -> List[dict]:
        """
        List all workflows for a user.
        Raises WorkflowServiceError on failure.
        """
        try:
            supabase = get_supabase_client()
            res = supabase.table(WORKFLOW_TABLE).select("*").eq("user_id", user_id).execute()
            return res.data or []
        except Exception as e:
            logger.error(f"Error listing workflows: {e}")
            raise WorkflowServiceError("Failed to list workflows")

    @staticmethod
    async def run_workflow(workflow_id: str, user_id: str, run_request: WorkflowRunRequest) -> WorkflowRunResult:
        """
        Run a workflow for a user. Executes steps in order, integrating with LangGraph and plugins.
        Returns WorkflowRunResult. Raises WorkflowServiceError on failure.
        """
        try:
            # Fetch workflow definition
            workflow = await WorkflowService.get_workflow(workflow_id, user_id)
            if not workflow:
                logger.error(f"Workflow not found: {workflow_id}")
                raise WorkflowServiceError("Workflow not found")

            # Integrate with LangGraph for execution
            graph = StateGraph.from_dict(workflow["definition"])
            try:
                result = await graph.run_async(run_request.input, context=run_request.context or {})
                logs = result.get("logs", [])
                output = result.get("output", {})
                status = "success"
            except Exception as exc:
                logs = getattr(exc, "logs", [])
                output = getattr(exc, "output", {})
                status = "error"
                logger.error(f"LangGraph execution error: {exc}")

            return WorkflowRunResult(status=status, output=output, logs=logs)
        except Exception as e:
            logger.error(f"Error running workflow: {e}")
            raise WorkflowServiceError("Failed to run workflow")

# TODO: Integrate plugin/agent/tool execution logic.
# TODO: Add more granular workflow error types if needed.
