# Databricks notebook source
# MAGIC %md
# MAGIC # Phase 4: Machine Learning Model Training 
# MAGIC **Author:** IntelliPipe Participant  
# MAGIC **Purpose:** Trains a time-series predictor using Gold layer metrics, logs to MLflow, and registers in Unity Catalog.

import sys
import os
import mlflow
import pandas as pd
from mlflow.models.signature import infer_signature
import numpy as np

# Add repo root to path to import our custom mllibs
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ml.feature_engineering import create_features
from ml.train_model import train_volume_predictor, train_anomaly_detector
from ml.evaluate_model import evaluate_predictions, simulate_anomaly_f1

# ────────────────────────────────────────────────────────
# 0. Configuration
# CHANGES MADE: Updated to use your custom catalog 'intellipipe'
CATALOG_NAME = "intellipipe"  
# ────────────────────────────────────────────────────────

# 1. Load Data from Gold Layer
try:
    # We read from the Gold layer tables inside your specified catalog
    df_spark = spark.table(f"{CATALOG_NAME}.gold.hourly_order_metrics")
    df_pandas = df_spark.toPandas()
except Exception as e:
    print(f"Warning: Could not read from {CATALOG_NAME}.gold.hourly_order_metrics. Proceeding with dummy data for local testing.")
    # Local fallback for testing the script's logic without Databricks
    date_rng = pd.date_range(start='1/1/2025', end='1/31/2025', freq='h')
    df_pandas = pd.DataFrame(date_rng, columns=['hour_start'])
    df_pandas['total_orders'] = np.random.randint(100, 500, size=(len(date_rng)))
    df_pandas['total_revenue'] = df_pandas['total_orders'] * 15.0
    df_pandas['avg_discount'] = np.random.uniform(0.05, 0.20, size=(len(date_rng)))

# 2. Feature Engineering
print(f"Applying feature engineering to {len(df_pandas)} rows...")
featured_df = create_features(df_pandas)

# 3. Train/Test Split (Time-based, no leakage)
split_idx = int(len(featured_df) * 0.8)
train_df = featured_df.iloc[:split_idx]
test_df = featured_df.iloc[split_idx:]

# Define feature columns
feature_cols = ['hour_sin', 'hour_cos', 'is_weekend', 'lag_1h', 'lag_2h', 'lag_3h', 'rolling_mean_3h', 'rolling_mean_6h', 'rolling_std_6h']
target_col = 'total_orders'

X_train, y_train = train_df[feature_cols], train_df[target_col]
X_test, y_test = test_df[feature_cols], test_df[target_col]

# 4. MLflow Experiment Tracking
class AnomalyPredictorModel(mlflow.pyfunc.PythonModel):
    def load_context(self, context):
        import joblib
        self.vol_model = joblib.load(context.artifacts["vol_model"])
        self.anom_model = joblib.load(context.artifacts["anom_model"])
        
    def predict(self, context, model_input):
        vol_pred = self.vol_model.predict(model_input)
        anom_score = self.anom_model.score_samples(model_input)
        anom_label = self.anom_model.predict(model_input)
        
        return pd.DataFrame({
            "expected_volume": vol_pred,
            "anomaly_score": anom_score,
            "is_anomaly": anom_label == -1
        })

print("Starting MLflow Run...")
mlflow.set_experiment(f"/Shared/IntelliPipe_ML")

with mlflow.start_run(run_name="volume_anomaly_predictor") as run:
    # Train Models
    vol_model = train_volume_predictor(X_train, y_train)
    anom_model = train_anomaly_detector(X_train)
    
    # Evaluate
    vol_preds = vol_model.predict(X_test)
    metrics = evaluate_predictions(y_test, vol_preds)
    mlflow.log_metrics(metrics)
    
    print(f"Test RMSE: {metrics['rmse']:.2f}")
    
    import joblib
    joblib.dump(vol_model, "vol_model.pkl")
    joblib.dump(anom_model, "anom_model.pkl")
    
    artifacts = {
        "vol_model": "vol_model.pkl",
        "anom_model": "anom_model.pkl"
    }

    signature = infer_signature(X_test, pd.DataFrame({"expected_volume": [1.0], "anomaly_score": [0.5], "is_anomaly": [False]}))

    # Log Custom Model to Unity Catalog
    mlflow.pyfunc.log_model(
        artifact_path="model",
        python_model=AnomalyPredictorModel(),
        artifacts=artifacts,
        signature=signature,
        # Registred in the 'ml' schema of your catalog
        registered_model_name=f"{CATALOG_NAME}.ml.volume_predictor"
    )
    
print(f"Phase 4 Complete: Model Trained and Registered to {CATALOG_NAME}.ml.volume_predictor")
