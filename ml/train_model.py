from sklearn.ensemble import GradientBoostingRegressor, IsolationForest
from typing import Tuple, Any

def train_volume_predictor(X_train, y_train) -> Any:
    """
    Trains a Gradient Boosting Regressor to predict the expected total_orders.
    """
    model = GradientBoostingRegressor(n_estimators=100, learning_rate=0.1, max_depth=3, random_state=42)
    model.fit(X_train, y_train)
    return model

def train_anomaly_detector(X_train) -> Any:
    """
    Trains an Isolation Forest to detect anomalous order volume patterns.
    It fits on the feature space (which includes lags and expected patterns).
    """
    # contamination defines the expected proportion of outliers (anomalies) in the dataset
    model = IsolationForest(contamination=0.05, random_state=42)
    model.fit(X_train)
    return model
