"""
Tool: get_anomaly_prediction
Calls the deployed ML model serving endpoint to return anomaly prediction.
"""
import requests
import os

def get_anomaly_prediction(features: dict) -> dict:
    """
    Sends feature data to the MLflow model serving endpoint and returns
    the expected volume and anomaly probability for the next hour.

    Args:
        features: A dict of feature values matching the model's input schema.
                  Keys: hour_sin, hour_cos, is_weekend, lag_1h, lag_2h, lag_3h,
                        rolling_mean_3h, rolling_mean_6h, rolling_std_6h

    Returns:
        A dict with expected_volume, anomaly_score, and is_anomaly flag.

    Example:
        get_anomaly_prediction({"hour_sin": 0.5, "hour_cos": 0.8, ...})
    """
    endpoint_url = os.getenv("MODEL_SERVING_ENDPOINT_URL", "")
    token = os.getenv("DATABRICKS_TOKEN", "")

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    payload = {
        "dataframe_records": [features]
    }

    try:
        resp = requests.post(endpoint_url, headers=headers, json=payload, timeout=10)
        resp.raise_for_status()
        predictions = resp.json().get("predictions", [{}])[0]
        return {
            "expected_volume": predictions.get("expected_volume"),
            "anomaly_score": predictions.get("anomaly_score"),
            "is_anomaly": predictions.get("is_anomaly", False)
        }
    except Exception as e:
        return {"error": str(e)}
