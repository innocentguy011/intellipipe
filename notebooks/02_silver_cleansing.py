# Databricks notebook source
# CHANGES MADE: This table will be published to the 'intellipipe' catalog 
#              as configured in your DLT Pipeline settings.
# ────────────────────────────────────────────────────────
import dlt
from pyspark.sql.functions import col, expr
import sys
import os

# Ensure the udfs module can be imported by adding the repo root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the UDFs we just wrote
from udfs.normalize_category import normalize_category_udf
from udfs.mask_customer import mask_customer_udf
from udfs.quality_score import quality_score_udf

@dlt.table(
    name="clean_orders",
    comment="Silver layer: Cleansed, deduplicated, and enriched e-commerce orders.",
    table_properties={
        "quality": "silver"
    }
)
@dlt.expect_or_drop("valid_order_id", "order_id IS NOT NULL")
def cleanse_orders():
    """
    Reads from the Bronze 'raw_orders' table.
    Filters out null order_ids, deduplicates, and applies UDFs.
    """
    # 1. Read from Bronze
    df = dlt.read("raw_orders")
    
    # 2. Deduplicate on order_id and event_timestamp
    df = df.dropDuplicates(["order_id", "event_timestamp"])
    
    # 3. Apply UDFs for cleansing and enrichment
    df = df.withColumn("category_clean", normalize_category_udf(col("category"))) \
           .withColumn("customer_id_masked", mask_customer_udf(col("customer_id"))) \
           .withColumn("dq_score", quality_score_udf(col("order_id"), col("customer_id"), col("unit_price"), col("quantity")))
    
    return df
