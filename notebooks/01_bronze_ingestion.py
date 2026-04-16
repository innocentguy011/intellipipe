import dlt
from pyspark.sql.functions import current_timestamp

# Define the source path - matching the output from 00_generate_data.py
SOURCE_DIR = "dbfs:/FileStore/intellipipe/raw/orders/"

@dlt.table(
    name="raw_orders",
    comment="Bronze layer: Raw ingestion of synthetic e-commerce orders files with schema inference.",
    table_properties={
        "quality": "bronze",
        "pipelines.autoOptimize.managed": "true"
    }
)
def ingest_raw_orders():
    """
    Ingests JSON events from cloud storage using Auto Loader (cloudFiles).
    Stores malformed data in '_rescue_data' column automatically.
    """
    return (
        spark.readStream.format("cloudFiles")
        .option("cloudFiles.format", "json")
        .option("cloudFiles.inferColumnTypes", "true") # Infer column data types automatically
        .option("cloudFiles.schemaEvolutionMode", "addNewColumns") 
        .load(SOURCE_DIR)
        .withColumn("ingestion_timestamp", current_timestamp())
    )
