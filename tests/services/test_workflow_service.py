import pytest
from unittest.mock import AsyncMock, patch
from app.services.workflow_service import WorkflowService, WorkflowServiceError
from app.models.workflow import WorkflowRunRequest, WorkflowRunResult

@pytest.mark.asyncio
@patch("app.services.plugin_service.PluginService.execute", new_callable=AsyncMock)
@patch("app.services.workflow_service.WorkflowService.get_workflow", new_callable=AsyncMock)
async def test_run_workflow_plugin_step(mock_get_workflow, mock_plugin_execute):
    mock_get_workflow.return_value = {
        "steps": [
            {"id": "s1", "type": "plugin", "config_id": "cfg1", "parameters": {"param1": "foo"}}
        ]
    }
    mock_plugin_execute.return_value = {"result": "plugin success"}
    run_request = WorkflowRunRequest(inputs={"input1": "bar"})
    result: WorkflowRunResult = await WorkflowService.run_workflow("wf1", "user1", run_request)
    assert result.status == "success"
    assert result.output["s1"]["result"] == "plugin success"
    assert any("plugin result" in log for log in result.logs)

@pytest.mark.asyncio
@patch("app.services.workflow_service.WorkflowService.get_workflow", new_callable=AsyncMock)
async def test_run_workflow_agent_tool_stub(mock_get_workflow):
    mock_get_workflow.return_value = {
        "steps": [
            {"id": "s2", "type": "agent", "parameters": {"foo": "bar"}},
            {"id": "s3", "type": "tool", "parameters": {"baz": "qux"}}
        ]
    }
    run_request = WorkflowRunRequest(inputs={})
    result: WorkflowRunResult = await WorkflowService.run_workflow("wf2", "user2", run_request)
    assert result.status == "success"
    assert result.output["s2"]["message"] == "Agent execution not implemented"
    assert result.output["s3"]["message"] == "Tool execution not implemented"
    assert any("agent execution is a stub" in log for log in result.logs)
    assert any("tool execution is a stub" in log for log in result.logs)

@pytest.mark.asyncio
@patch("app.services.plugin_service.PluginService.execute", new_callable=AsyncMock)
@patch("app.services.workflow_service.WorkflowService.get_workflow", new_callable=AsyncMock)
async def test_run_workflow_plugin_error(mock_get_workflow, mock_plugin_execute):
    mock_get_workflow.return_value = {
        "steps": [
            {"id": "s4", "type": "plugin", "config_id": "cfg2", "parameters": {}}
        ]
    }
    mock_plugin_execute.side_effect = Exception("plugin failed")
    run_request = WorkflowRunRequest(inputs={})
    result: WorkflowRunResult = await WorkflowService.run_workflow("wf3", "user3", run_request)
    assert result.status == "error"
    assert "plugin failed" in result.output["s4"]["error"]
    assert any("Error in step s4" in log for log in result.logs)

@pytest.mark.asyncio
@patch("app.services.workflow_service.WorkflowService.get_workflow", new_callable=AsyncMock)
async def test_run_workflow_unknown_step_type(mock_get_workflow):
    mock_get_workflow.return_value = {
        "steps": [
            {"id": "s5", "type": "unknown_type", "parameters": {}}
        ]
    }
    run_request = WorkflowRunRequest(inputs={})
    result: WorkflowRunResult = await WorkflowService.run_workflow("wf4", "user4", run_request)
    assert result.status == "error"
    assert "Unknown step type" in result.output["s5"]["error"]
    assert any("has unknown type" in log for log in result.logs)

@pytest.mark.asyncio
@patch("app.services.workflow_service.WorkflowService.get_workflow", new_callable=AsyncMock)
async def test_run_workflow_not_found(mock_get_workflow):
    mock_get_workflow.return_value = None
    run_request = WorkflowRunRequest(inputs={})
    with pytest.raises(WorkflowServiceError) as excinfo:
        await WorkflowService.run_workflow("wf5", "user5", run_request)
    assert "Workflow not found" in str(excinfo.value)
