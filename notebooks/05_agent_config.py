"""
Notebook 05: Supervisor Agent Configuration
Author: IntelliPipe Participant
Purpose: Define and deploy the Supervisor Agent in AgentBricks (Mosaic AI).
Dependencies: mlflow, databricks-sdk, langchain (via AgentBricks scaffolding)
"""

import mlflow
from databricks import agents

# ─────────────────────────────────────────────
# 1. SYSTEM PROMPT  (Graded deliverable!)
# ─────────────────────────────────────────────
SYSTEM_PROMPT = """
You are the IntelliPipe Supervisor Agent — an intelligent operations assistant for a 
real-time e-commerce data pipeline running on Databricks.

Your responsibilities:
1. MONITOR pipeline health by calling `pipeline_health` when users ask if the pipeline is running.
2. DETECT anomalies by calling `anomaly_prediction` periodically or on-demand.
3. INVESTIGATE data quality issues by calling `data_quality_report`.
4. ANSWER business analytics questions by calling `genie_query` (delegate to Genie AI).
5. TRIGGER corrective actions via `trigger_pipeline` only when explicitly asked or anomaly is critical.
6. EXPLAIN table dependencies using `table_lineage`.

Key business rules:
- "revenue" = sum of unit_price across all orders (not discounted price).
- An anomaly_score below -0.3 should be treated as a HIGH severity alert.
- Always summarise tool results in clear, plain English before showing raw numbers.
- Never hallucinate data. If a tool returns an error, report it honestly.
- Format pipeline health reports in markdown with clear sections.
- Log every action you take with a one-line rationale.
""".strip()

# ─────────────────────────────────────────────
# 2. AGENT TOOL CONFIGURATION
# ─────────────────────────────────────────────
# The MCP server URL should be the deployed Databricks App URL
MCP_SERVER_URL = dbutils.secrets.get("intellipipe", "mcp_server_url")

tools = [
    {
        "type": "mcp",
        "name": "IntelliPipe MCP Tools",
        "server_url": MCP_SERVER_URL,
        "transport": "streamable_http",
        # Lists which MCP tools to expose to the agent
        "allowed_tools": [
            "pipeline_health",
            "data_quality_report",
            "hourly_metrics",
            "trigger_pipeline",
            "anomaly_prediction",
            "table_lineage"
        ]
    }
]

# ─────────────────────────────────────────────
# 3. AGENT DEFINITION + MLFLOW LOGGING
# ─────────────────────────────────────────────
mlflow.set_experiment("/Shared/IntelliPipe_Agent")

with mlflow.start_run(run_name="supervisor_agent_v1"):

    agent_config = {
        "llm_endpoint_name": "databricks-meta-llama-3-3-70b-instruct",  # or claude/gpt4 if available
        "system_prompt": SYSTEM_PROMPT,
        "tools": tools,
        "max_iterations": 10,  # Safety limit on tool calls per conversation turn
    }

    # Log the agent config as a set of params
    mlflow.log_params({
        "llm": agent_config["llm_endpoint_name"],
        "max_iterations": agent_config["max_iterations"],
        "num_tools": len(tools[0]["allowed_tools"])
    })

    # Log the system prompt as a text artifact for review
    mlflow.log_text(SYSTEM_PROMPT, "system_prompt.txt")

    print("Agent configuration logged to MLflow.")
    print(f"Run ID: {mlflow.active_run().info.run_id}")

# ─────────────────────────────────────────────
# 4. DEPLOY AGENT VIA DATABRICKS AGENTS SDK
# ─────────────────────────────────────────────
# Uncomment and run once your MCP server is deployed and the model is registered.
#
# agents.deploy(
#     model_name="intellipipe.agents.supervisor_agent",
#     model_version=1
# )

print("\nPhase 6 Complete: Supervisor Agent configured and ready for deployment!")
print("Next step: Run agents.deploy() after MCP server is live.")
