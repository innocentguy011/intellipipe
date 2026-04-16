"""
Unit Tests: Pipeline Logic
Validates the logic used within the DLT pipelines (transformation logic).
"""
import sys, os
import pytest
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, TimestampType, DoubleType, IntegerType

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

@pytest.fixture(scope="session")
def spark():
    return SparkSession.builder.master("local[1]").appName("PipelineTests").getOrCreate()

def test_deduplication_logic(spark):
    # Create sample data with duplicates
    schema = StructType([
        StructField("order_id", StringType(), True),
        StructField("event_timestamp", TimestampType(), True),
        StructField("data", StringType(), True)
    ])
    
    from datetime import datetime
    ts = datetime(2025, 1, 1, 12, 0, 0)
    data = [
        ("ORD1", ts, "first"),
        ("ORD1", ts, "duplicate"),
        ("ORD2", ts, "unique")
    ]
    
    df = spark.createDataFrame(data, schema)
    
    # Simulate the dropDuplicates call from 02_silver_cleansing.py
    dedup_df = df.dropDuplicates(["order_id", "event_timestamp"])
    
    assert dedup_df.count() == 2
    ids = [row.order_id for row in dedup_df.collect()]
    assert "ORD1" in ids
    assert "ORD2" in ids
