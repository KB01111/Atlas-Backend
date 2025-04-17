from typing import Optional

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
    """Service for workflow CRUD and execution."""

    @staticmethod
    async def create_workflow(user_id: str, workflow: WorkflowCreate) -> dict:
        """Create a new workflow for a user."""
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
            raise WorkflowServiceError("Failed to create workflow") from e

    @staticmethod
    async def list_workflows(user_id: str) -> list[dict]:
        """List all workflows for a user."""
        try:
            supabase = get_supabase_client()
            res = (
                supabase.table(WORKFLOW_TABLE)
                .select("*")
                .eq("user_id", user_id)
                .execute()
            )
            return res.data or []
        except Exception as e:
            logger.error(f"Error listing workflows: {e}")
            raise WorkflowServiceError("Failed to list workflows") from e

    @staticmethod
    async def delete_workflow(workflow_id: str, user_id: str) -> bool:
        """Delete a workflow for a user. Returns True if deleted."""
        try:
            supabase = get_supabase_client()
            res = (
                supabase.table(WORKFLOW_TABLE)
                .delete()
                .eq("id", workflow_id)
                .eq("user_id", user_id)
                .execute()
            )
            return bool(res.data)
        except Exception as e:
            logger.error(f"Error deleting workflow: {e}")
            raise WorkflowServiceError("Failed to delete workflow") from e

    @staticmethod
    async def update_workflow(
        workflow_id: str, user_id: str, workflow: WorkflowUpdate
    ) -> Optional[dict]:
        """Update a workflow for a user. Returns updated workflow or None."""
        try:
            data = workflow.dict(exclude_unset=True)
            supabase = get_supabase_client()
            res = (
                supabase.table(WORKFLOW_TABLE)
                .update(data)
                .eq("id", workflow_id)
                .eq("user_id", user_id)
                .execute()
            )
            return res.data[0] if res.data else None
        except Exception as e:
            logger.error(f"Error updating workflow: {e}")
            raise WorkflowServiceError("Failed to update workflow") from e

    @staticmethod
    async def get_workflow(workflow_id: str, user_id: str) -> Optional[dict]:
        """Retrieve a workflow by ID for a user. Returns None if not found."""
        try:
            supabase = get_supabase_client()
            res = (
                supabase.table(WORKFLOW_TABLE)
                .select("*")
                .eq("id", workflow_id)
                .eq("user_id", user_id)
                .single()
                .execute()
            )
            return res.data if res.data else None
        except Exception as e:
            logger.error(f"Error fetching workflow: {e}")
            raise WorkflowServiceError("Failed to fetch workflow") from e

    @staticmethod
    async def run_workflow(
        workflow_id: str, user_id: str, run_request: WorkflowRunRequest
    ) -> WorkflowRunResult:
        """Run a workflow for a user. Executes steps in order, integrating with plugins and agents."""
        try:
            workflow = await WorkflowService.get_workflow(workflow_id, user_id)
            if not workflow:
                logger.error(f"Workflow not found: {workflow_id}")
                raise WorkflowServiceError("Workflow not found")

            steps = workflow.get("steps", [])
            context = run_request.inputs.copy() if hasattr(run_request, "inputs") else {}
            logs = []
            output = {}
            status = "success"

            for idx, step in enumerate(steps):
                step_type = step.get("type")
                config_id = step.get("config_id")
                parameters = step.get("parameters", {})
                step_id = step.get("id", f"step_{idx}")
                logs.append(f"Running step {step_id} of type {step_type}")
                try:
                    if step_type == "plugin":
                        from app.services.plugin_service import PluginService
                        result = await PluginService.execute(config_id, {**parameters, **context, "user_id": user_id})
                        output[step_id] = result
                        logs.append(f"Step {step_id} plugin result: {result}")
                    elif step_type == "agent":
                        logs.append(f"Step {step_id} agent execution is a stub.")
                        output[step_id] = {"message": "Agent execution not implemented", "parameters": parameters}
                    elif step_type == "tool":
                        logs.append(f"Step {step_id} tool execution is a stub.")
                        output[step_id] = {"message": "Tool execution not implemented", "parameters": parameters}
                    else:
                        logs.append(f"Step {step_id} has unknown type: {step_type}")
                        output[step_id] = {"error": f"Unknown step type: {step_type}"}
                        status = "error"
                except Exception as exc:
                    logs.append(f"Error in step {step_id}: {exc}")
                    output[step_id] = {"error": str(exc)}
                    status = "error"
            return WorkflowRunResult(status=status, output=output, logs=logs)
        except Exception as e:
            logger.error(f"Error running workflow: {e}")
            raise WorkflowServiceError("Failed to run workflow") from e
