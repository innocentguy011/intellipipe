# IntelliPipe: Intelligent Data Engineering Pipeline

> **Capstone Project** — Databricks Data Engineering & AI Track  
> Version 1.0 | Python 3.10+ | PySpark | MLflow | MCP | AgentBricks

---

## 🏗️ Architecture

```
Raw JSON (Volume) ──► Bronze DLT ──► Silver DLT (UDFs) ──► Gold DLT ──► Genie AI
                                                        │
                                               ┌────────▼────────┐
                                               │   ML Model      │
                                               │  (MLflow)       │
                                               └────────┬────────┘
                                                        │
                                               ┌────────▼────────┐
                                               │   MCP Server    │
                                               │ (Databricks App)│
                                               └────────┬────────┘
                                                        │
                                               ┌────────▼────────┐
                                               │ Supervisor Agent│
                                               │  (AgentBricks)  │
                                               └─────────────────┘
```

## 📁 Repository Structure

```
intellipipe/
├── notebooks/
│   ├── 00_generate_data.py       # Outputs to /Volumes/intellipipe/default/intellipipe_volume/raw/
│   ├── 01_bronze_ingestion.py    # Reads from /Volumes/intellipipe/default/intellipipe_volume/raw/
│   ├── 02_silver_cleansing.py    # DLT Cleansing + UDFs → Silver
│   ├── 03_gold_aggregation.py    # DLT Aggregation → Gold
│   ├── 04_ml_training.py         # MLflow model training + registration
│   └── 05_agent_config.py        # AgentBricks Supervisor Agent setup
├── udfs/
│   ├── normalize_category.py     # Category standardisation UDF
│   ├── mask_customer.py          # SHA-256 PII masking UDF
│   └── quality_score.py          # Row-level data quality score UDF
├── ml/
│   ├── feature_engineering.py    # Time-series feature creation
│   ├── train_model.py            # GBT + IsolationForest training
│   └── evaluate_model.py         # RMSE, MAE, anomaly ratio metrics
├── mcp_server/
│   ├── app.py                    # FastMCP server entry point
│   └── tools/
│       ├── pipeline_health.py    # Tool: get_pipeline_health
│       ├── data_quality.py       # Tool: get_data_quality_report
│       ├── hourly_metrics.py     # Tool: get_hourly_metrics
│       ├── trigger_pipeline.py   # Tool: trigger_pipeline_run
│       ├── anomaly_prediction.py # Tool: get_anomaly_prediction
│       └── table_lineage.py      # Tool: get_table_lineage
├── tests/
│   ├── test_udfs.py              # UDF unit tests (>80% coverage)
│   ├── test_pipeline.py          # Pipeline logic tests
│   └── test_agent_tools.py       # MCP tool parameter/output tests
└── docs/                         # ADR documents and architecture diagrams
```

## 🚀 Quick Start (Databricks)

### Step 1 — Clone this repo into Databricks
```
Workspace → Create → Git folder → paste this repo URL
```

### Step 2 — Run notebooks in order
```
00_generate_data     → creates 5M rows of synthetic data in dbfs:/FileStore/intellipipe/raw/orders/
01_bronze_ingestion  → create DLT pipeline pointing to this notebook
02_silver_cleansing  → add to same DLT pipeline (runs after Bronze)
03_gold_aggregation  → add to same DLT pipeline (runs after Silver)
04_ml_training       → run as a regular notebook on ML cluster
05_agent_config      → run after MCP server is deployed
```

### Step 3 — Deploy MCP Server as a Databricks App
```bash
cd mcp_server/
# From Databricks CLI:
databricks apps deploy intellipipe-mcp --source-code-path ./mcp_server
```

### Step 4 — Set Required Secrets
```python
# In a Databricks notebook:
# databricks secrets create-scope --scope intellipipe
# databricks secrets put --scope intellipipe --key mcp_server_url
# databricks secrets put --scope intellipipe --key MODEL_SERVING_ENDPOINT_URL
```

## 🧪 Running Tests
```bash
pip install pytest
pytest tests/test_udfs.py -v --tb=short
```

## 📦 Dependencies
```
databricks-sdk>=0.20.0
mcp[server]>=1.0.0
fastapi>=0.110.0
scikit-learn>=1.4.0
mlflow>=2.12.0
delta-spark>=3.1.0
pytest>=8.0.0
```

## 📊 Evaluation Rubric Summary

| Component | Marks |
|---|---|
| Delta Pipeline (Bronze/Silver/Gold) | 20 |
| UDFs (3 × registered + tested) | 15 |
| Genie Setup (10 benchmark Q&A) | 10 |
| ML Model (trained + served) | 15 |
| MCP Server (6 tools deployed) | 20 |
| Supervisor Agent (eval dataset ≥20) | 15 |
| Code Quality (PEP8 + docs + ADRs) | 5 |
| **TOTAL** | **100** |

**Pass threshold: ≥ 70**

---

*IntelliPipe Capstone — Internal L&D / Databricks CoE Team — v1.0*
