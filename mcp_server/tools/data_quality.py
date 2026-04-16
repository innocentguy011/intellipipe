"""
Tool: get_data_quality_report
Queries DLT event log for constraint violations and returns a quality summary.
"""
from databricks.sdk import WorkspaceClient

def get_data_quality_report(catalog: str, schema: str, table: str) -> dict:
    """
    Reads the DLT event log to surface data quality constraint violations.

    Args:
        catalog: Unity Catalog name (e.g. 'intellipipe').
        schema:  Schema name (e.g. 'silver').
        table:   Table name (e.g. 'clean_orders').

    Returns:
        A dictionary with violation counts and expectation names.

    Example:
        get_data_quality_report("intellipipe", "silver", "clean_orders")
    """
    w = WorkspaceClient()

    # Query the DLT event log stored alongside the pipeline's storage location
    # In Databricks, the event_log is queryable via SQL
    sql = f"""
        SELECT
            expectations.name AS expectation,
            SUM(expectations.failed_records) AS failed_records,
            SUM(expectations.passed_records) AS passed_records
        FROM (
            SELECT explode(details:flow_progress:data_quality:dropped_records) AS expectations
            FROM event_log(TABLE({catalog}.{schema}.{table}))
            WHERE event_type = 'flow_progress'
        )
        GROUP BY 1
        ORDER BY 2 DESC
    """
    try:
        rows = w.statement_execution.execute_statement(
            warehouse_id=os.getenv("DATABRICKS_WAREHOUSE_ID", ""),
            statement=sql
        )
        results = [{"expectation": r[0], "failed": r[1], "passed": r[2]}
                   for r in (rows.result.data_array or [])]
        return {"table": f"{catalog}.{schema}.{table}", "quality_checks": results}
    except Exception as e:
        return {"error": str(e)}
