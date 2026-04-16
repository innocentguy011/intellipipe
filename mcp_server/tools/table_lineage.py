"""
Tool: get_table_lineage
Calls the Unity Catalog Lineage API to return upstream/downstream table dependencies.
"""
from databricks.sdk import WorkspaceClient

def get_table_lineage(table_full_name: str) -> dict:
    """
    Returns upstream and downstream lineage for a given Unity Catalog table.

    Args:
        table_full_name: Full table name in format catalog.schema.table

    Returns:
        A dict with upstream_tables and downstream_tables lists.

    Example:
        get_table_lineage("intellipipe.silver.clean_orders")
    """
    w = WorkspaceClient()
    try:
        result = w.lineage_tracking.table_lineage(table_name=table_full_name)
        upstreams = [t.name for t in (result.upstreams or [])]
        downstreams = [t.name for t in (result.downstreams or [])]
        return {
            "table": table_full_name,
            "upstream_tables": upstreams,
            "downstream_tables": downstreams
        }
    except Exception as e:
        return {"error": str(e), "table": table_full_name}
