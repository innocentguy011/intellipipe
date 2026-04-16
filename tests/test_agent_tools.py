"""
Unit Tests: MCP Tools
Mocks the WorkspaceClient and tests the logic of MCP tool functions.
"""
import sys, os
from unittest.mock import MagicMock, patch
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from mcp_server.tools.pipeline_health import get_pipeline_health
from mcp_server.tools.hourly_metrics import get_hourly_metrics

@patch('mcp_server.tools.pipeline_health.WorkspaceClient')
def test_get_pipeline_health_success(mock_client_class):
    # Setup mock
    mock_client = mock_client_class.return_value
    mock_pipeline = MagicMock()
    mock_pipeline.name = "test_pipeline"
    mock_pipeline.state.value = "RUNNING"
    mock_pipeline.latest_updates = [MagicMock(state=MagicMock(value="COMPLETED"), creation_time="2025-01-01")]
    mock_client.pipelines.get.return_value = mock_pipeline

    # Call
    result = get_pipeline_health("test-id")

    # Assert
    assert result["pipeline_name"] == "test_pipeline"
    assert result["state"] == "RUNNING"
    assert result["last_update_state"] == "COMPLETED"

@patch('mcp_server.tools.hourly_metrics.WorkspaceClient')
@patch('os.getenv')
def test_get_hourly_metrics_success(mock_getenv, mock_client_class):
    # Setup mock
    mock_getenv.return_value = "warehouse-id"
    mock_client = mock_client_class.return_value
    mock_result = MagicMock()
    mock_result.result.data_array = [
        ["2025-01-01T00:00:00", "2025-01-01T01:00:00", 100, 1500.0, 0.1]
    ]
    mock_client.statement_execution.execute_statement.return_value = mock_result

    # Call
    result = get_hourly_metrics("catalog", n_hours=1)

    # Assert
    assert result["n_hours"] == 1
    assert len(result["records"]) == 1
    assert result["records"][0]["total_orders"] == 100
    assert result["records"][0]["total_revenue"] == 1500.0
