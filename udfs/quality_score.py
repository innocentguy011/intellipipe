"""
UDF: compute_quality_score
Returns a numeric quality score (0.0-1.0) based on presence of nulls and value ranges.
"""
from pyspark.sql.functions import udf
from pyspark.sql.types import FloatType

def _compute_quality_score_impl(order_id, customer_id, unit_price, quantity) -> float:
    """
    Computes a simple data quality score.
    Subtracts points for missing critical fields or strange negative numbers.
    """
    score = 1.0
    
    if not order_id:
        score -= 0.4
    if not customer_id:
        score -= 0.3
        
    try:
        if float(unit_price) < 0:
            score -= 0.2
    except (ValueError, TypeError):
        score -= 0.2
        
    try:
        if int(quantity) <= 0:
            score -= 0.1
    except (ValueError, TypeError):
        score -= 0.1
        
    return max(0.0, score)

quality_score_udf = udf(_compute_quality_score_impl, FloatType())
