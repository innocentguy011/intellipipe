"""
IntelliPipe MCP Server
Author: IntelliPipe Participant
Purpose: FastAPI application exposing 6 pipeline observability tools via the MCP protocol.
Dependencies: fastapi, mcp[server], databricks-sdk
"""

from mcp.server.fastmcp import FastMCP
from tools.pipeline_health import get_pipeline_health
from tools.data_quality import get_data_quality_report
from tools.hourly_metrics import get_hourly_metrics
from tools.trigger_pipeline import trigger_pipeline_run
from tools.anomaly_prediction import get_anomaly_prediction
from tools.table_lineage import get_table_lineage

# Initialize the MCP server with a descriptive name
mcp = FastMCP("IntelliPipe MCP Server")


@mcp.tool()
def pipeline_health(pipeline_id: str) -> dict:
    """
    Returns the current health of the specified DLT pipeline.
    Includes state, last run status, and last update time.
    Call this when a user asks if the pipeline is running or healthy.
    """
    return get_pipeline_health(pipeline_id)


@mcp.tool()
def data_quality_report(catalog: str, schema: str, table: str) -> dict:
    """
    Returns a data quality report for a given Unity Catalog table.
    Surfaces DLT expectation violations (failed_records per constraint).
    Call this when a user asks about data quality issues.
    """
    return get_data_quality_report(catalog, schema, table)


@mcp.tool()
def hourly_metrics(catalog: str, n_hours: int = 24) -> dict:
    """
    Returns the last N hours of aggregated order metrics from the Gold layer.
    Includes total_orders, total_revenue, avg_discount per hour.
    Call this for recent business performance questions.
    """
    return get_hourly_metrics(catalog, n_hours)


@mcp.tool()
def trigger_pipeline(pipeline_id: str) -> dict:
    """
    Triggers a DLT pipeline run for the given pipeline_id.
    Use this when the agent determines a pipeline needs to be re-run.
    WARNING: This is a write operation — confirm intent before calling.
    """
    return trigger_pipeline_run(pipeline_id)


@mcp.tool()
def anomaly_prediction(features: dict) -> dict:
    """
    Calls the ML model serving endpoint to get the anomaly prediction
    for the next hour based on the provided feature values.
    Returns expected_volume, anomaly_score, and is_anomaly flag.
    Call this hourly for proactive anomaly alerting.
    """
    return get_anomaly_prediction(features)


@mcp.tool()
def table_lineage(table_full_name: str) -> dict:
    """
    Returns the upstream and downstream table lineage for a Unity Catalog table.
    Useful for impact analysis: 'What tables depend on silver.clean_orders?'
    """
    return get_table_lineage(table_full_name)


if __name__ == "__main__":
    # Run as an MCP Streamable HTTP server — required for Databricks Apps deployment
    mcp.run(transport="streamable-http")
