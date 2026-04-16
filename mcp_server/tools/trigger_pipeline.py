"""
Tool: trigger_pipeline_run
Triggers a DLT pipeline via the Databricks Jobs/Pipelines API.
"""
from databricks.sdk import WorkspaceClient

def trigger_pipeline_run(pipeline_id: str) -> dict:
    """
    Triggers a full refresh run of the specified DLT pipeline.

    Args:
        pipeline_id: The Databricks DLT Pipeline ID to trigger.

    Returns:
        A dict with the new update_id and pipeline state.

    Example:
        trigger_pipeline_run("abc-123-def")
    """
    w = WorkspaceClient()
    try:
        response = w.pipelines.start_update(pipeline_id=pipeline_id, full_refresh=False)
        return {
            "pipeline_id": pipeline_id,
            "update_id": response.update_id,
            "message": "Pipeline run triggered successfully."
        }
    except Exception as e:
        return {"error": str(e), "pipeline_id": pipeline_id}
