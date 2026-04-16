"""
Tool: get_hourly_metrics
Returns the last N hours of gold.hourly_order_metrics as JSON.
"""
from databricks.sdk import WorkspaceClient
import os

def get_hourly_metrics(catalog: str, n_hours: int = 24) -> dict:
    """
    Fetches the last N hours of aggregated order metrics from the Gold layer.

    Args:
        catalog:  Unity Catalog name (e.g. 'intellipipe').
        n_hours:  Number of past hours to return (default 24).

    Returns:
        A list of hourly metric records.

    Example:
        get_hourly_metrics("intellipipe", 12)
    """
    w = WorkspaceClient()
    sql = f"""
        SELECT hour_start, hour_end, total_orders, total_revenue, avg_discount
        FROM {catalog}.gold.hourly_order_metrics
        WHERE hour_start >= CURRENT_TIMESTAMP() - INTERVAL {n_hours} HOURS
        ORDER BY hour_start DESC
    """
    try:
        result = w.statement_execution.execute_statement(
            warehouse_id=os.getenv("DATABRICKS_WAREHOUSE_ID", ""),
            statement=sql
        )
        rows = result.result.data_array or []
        return {
            "n_hours": n_hours,
            "records": [
                {
                    "hour_start": r[0], "hour_end": r[1],
                    "total_orders": r[2], "total_revenue": r[3], "avg_discount": r[4]
                }
                for r in rows
            ]
        }
    except Exception as e:
        return {"error": str(e)}
