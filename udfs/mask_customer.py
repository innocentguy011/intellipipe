"""
UDF: mask_customer_id
Applies SHA-256 hashing to customer_id to pseudonymise PII.
"""
from pyspark.sql.functions import udf
from pyspark.sql.types import StringType
import hashlib

def _mask_customer_id_impl(customer_id: str) -> str:
    """
    Hashes the customer ID using SHA-256.
    """
    if not customer_id:
        return None
        
    return hashlib.sha256(customer_id.encode('utf-8')).hexdigest()

mask_customer_udf = udf(_mask_customer_id_impl, StringType())
