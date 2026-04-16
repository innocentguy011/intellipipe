"""
UDF: normalize_category
Standardises free-text category values to a known lookup dictionary.
"""
from pyspark.sql.functions import udf
from pyspark.sql.types import StringType

def _normalize_category_impl(category_str: str) -> str:
    """
    Core python logic for normalizing categories.
    """
    if not category_str:
        return "UNKNOWN"
    
    # Clean string: upper case, strip whitespace
    clean_str = category_str.strip().upper()
    
    # Lookup mappings
    mapping = {
        "ELECT.": "ELECTRONICS",
        "ELECTRONICS": "ELECTRONICS",
        "APPAREL": "APPAREL",
        "HOME": "HOME",
        "TOYS": "TOYS"
    }
    
    return mapping.get(clean_str, "OTHER")

# Define the PySpark UDF
normalize_category_udf = udf(_normalize_category_impl, StringType())
