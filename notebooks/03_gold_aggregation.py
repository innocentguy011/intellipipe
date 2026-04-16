import dlt
from pyspark.sql.functions import col, window, count, sum, avg

@dlt.table(
    name="hourly_order_metrics",
    comment="Gold layer: Hourly aggregated metrics across all orders for Genie AI and ML predictions.",
    table_properties={
        "quality": "gold"
    }
)
def hourly_order_metrics():
    """
    Aggregates Silver data into an hourly time-series table.
    """
    df = dlt.read("clean_orders")
    
    # Create hourly windows
    hourly_df = df.groupBy(window(col("event_timestamp"), "1 hour")) \
        .agg(
            count("order_id").alias("total_orders"),
            sum("unit_price").alias("total_revenue"),
            avg("discount").alias("avg_discount")
        ) \
        .select(
            col("window.start").alias("hour_start"),
            col("window.end").alias("hour_end"),
            "total_orders",
            "total_revenue",
            "avg_discount"
        )
        
    return hourly_df

@dlt.table(
    name="category_summary",
    comment="Gold layer: Summary table for order categories. Acts as a dimension table.",
    table_properties={
        "quality": "gold"
    }
)
def category_summary():
    """
    Aggregates Silver data to provide a summary by product category.
    This functions as our SCD Type 1 dimension table in the Data Model.
    """
    df = dlt.read("clean_orders")
    
    # Note: category_clean is the output of our normalize_category UDF
    category_df = df.groupBy("category_clean") \
        .agg(
            count("order_id").alias("lifetime_orders"),
            sum("unit_price").alias("lifetime_revenue"),
            avg("dq_score").alias("avg_data_quality")
        )
        
    return category_df
