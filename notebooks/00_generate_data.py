"""
Author: IntelliPipe Participant
Date: 2025
Purpose: Generate 90 days of synthetic e-commerce data (approx 5M rows) for the Capstone pipeline
Dependencies: pyspark.sql

This script mocks e-commerce transactions and saves them to a dbfs/cloud storage path
as JSON files, simulating a continuous landing zone for the Bronze Auto Loader pipeline.
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import expr, round, col, row_number, rand
from pyspark.sql.window import Window
import uuid

# Initialize Spark session (In Databricks, 'spark' is already available, 
# but this allows local testing if environment is configured)
spark = SparkSession.builder.appName("IntelliPipe-DataGen").getOrCreate()

# Configuration
NUM_RECORDS = 5000000
DAYS_OF_HISTORY = 90
OUTPUT_DIR = "/mnt/raw/orders/"

print(f"Generating {NUM_RECORDS} synthetic records spanning {DAYS_OF_HISTORY} days...")

# Create a base dataframe of numbers
df = spark.range(0, NUM_RECORDS)

# Generate synthetic columns using SQL expressions
# random timestamps within the last 90 days
expr_timestamp = f"current_timestamp() - interval (rand() * {DAYS_OF_HISTORY}) days"

# Random categories with some intentional typos/variants for Silver cleansing
expr_category = """
    mask(
        element_at(array('ELECTRONICS', 'electronics ', 'Elect.', 'APPAREL', 'Apparel', 'HOME', 'HOME ', 'TOYS'), 
        cast(rand() * 8 + 1 as int)
    )
"""
expr_category = "element_at(array('ELECTRONICS', 'electronics ', 'Elect.', 'APPAREL', 'Apparel', 'HOME', 'HOME ', 'TOYS'), cast(rand() * 8 + 1 as int))"


synthetic_df = df \
    .withColumn("order_id", expr("uuid()")) \
    .withColumn("customer_id", expr("concat('CUST_', cast(cast(rand() * 100000 as int) as string))")) \
    .withColumn("product_id", expr("concat('PROD_', cast(cast(rand() * 5000 as int) as string))")) \
    .withColumn("category", expr(expr_category)) \
    .withColumn("quantity", expr("cast(rand() * 5 + 1 as int)")) \
    .withColumn("unit_price", round(expr("rand() * 200 + 10"), 2)) \
    .withColumn("discount", round(expr("rand() * 0.30"), 2)) \
    .withColumn("payment_method", expr("element_at(array('CREDIT_CARD', 'PAYPAL', 'APPLE_PAY', 'DEBIT', NULL), cast(rand() * 5 + 1 as int))")) \
    .withColumn("event_timestamp", expr(expr_timestamp)) \
    .withColumn("device_type", expr("element_at(array('iOS', 'Android', 'Web', 'MobileWeb'), cast(rand() * 4 + 1 as int))"))

# Add some intentional nulls to order_id and duplicates for the pipeline to handle
# E.g., make ~1% of order_ids null
synthetic_df = synthetic_df.withColumn(
    "order_id", 
    expr("case when rand() < 0.01 then null else order_id end")
)

print(f"Writing data to JSON format at {OUTPUT_DIR}")
# Write out as json, partitioned by date to simulate daily drops
# In Databricks we would typically write to DBFS or an S3/ADLS mount.
# Local execution will just write to a local folder.
synthetic_df.write \
    .mode("overwrite") \
    .json(OUTPUT_DIR)

print("Data generation complete!")
