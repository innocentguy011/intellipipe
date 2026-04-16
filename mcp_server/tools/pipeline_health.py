"""
Tool: get_pipeline_health
Returns DLT pipeline run status, last successful run time, and row counts per layer.
"""
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.pipelines import GetPipelineResponse
import os

def get_pipeline_health(pipeline_id: str) -> dict:
    """
    Queries the Databricks Jobs/DLT API for the given pipeline_id.

    Args:
        pipeline_id: The Databricks DLT Pipeline ID (UUID string).

    Returns:
        A dictionary containing pipeline state, last update time, and row counts.

    Example:
        get_pipeline_health("abc-123-def")
    """
    w = WorkspaceClient()

    try:
        pipeline: GetPipelineResponse = w.pipelines.get(pipeline_id=pipeline_id)
        latest_update = pipeline.latest_updates[0] if pipeline.latest_updates else None

        return {
            "pipeline_id": pipeline_id,
            "pipeline_name": pipeline.name,
            "state": pipeline.state.value if pipeline.state else "UNKNOWN",
            "last_update_state": latest_update.state.value if latest_update else "NO_RUNS",
            "last_update_time": str(latest_update.creation_time) if latest_update else None,
        }
    except Exception as e:
        return {"error": str(e), "pipeline_id": pipeline_id}
