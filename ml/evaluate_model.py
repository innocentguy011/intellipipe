from sklearn.metrics import mean_squared_error, mean_absolute_error
import numpy as np

def evaluate_predictions(y_true, y_pred) -> dict:
    """
    Evaluates the volume predictor.
    """
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    mae = mean_absolute_error(y_true, y_pred)
    
    return {
        "rmse": rmse,
        "mae": mae
    }

def simulate_anomaly_f1(anomaly_preds):
    """
    In a real scenario with labeled anomalies, we'd calculate F1.
    For this unsupervised capstone, we just return the ratio of anomalies.
    """
    # Isolation forest predicts -1 for anomalies, 1 for normal
    anomaly_count = (anomaly_preds == -1).sum()
    total = len(anomaly_preds)
    anomaly_ratio = anomaly_count / total if total > 0 else 0
    return {"anomaly_ratio": anomaly_ratio}
