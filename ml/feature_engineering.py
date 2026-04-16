import pandas as pd
import numpy as np

def create_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Given a pandas DataFrame with 'hour_start' (datetime) and 'total_orders', 
    creates time-series features for anomaly prediction.
    """
    df = df.copy()
    
    # Ensure hour_start is datetime and sorted
    df['hour_start'] = pd.to_datetime(df['hour_start'])
    df = df.sort_values('hour_start').reset_index(drop=True)
    
    # Time-based categorical features
    df['hour_of_day'] = df['hour_start'].dt.hour
    df['day_of_week'] = df['hour_start'].dt.dayofweek
    df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
    
    # Cyclical encoding for hour (0-23)
    df['hour_sin'] = np.sin(2 * np.pi * df['hour_of_day']/24.0)
    df['hour_cos'] = np.cos(2 * np.pi * df['hour_of_day']/24.0)
    
    # Lag features (past values)
    df['lag_1h'] = df['total_orders'].shift(1)
    df['lag_2h'] = df['total_orders'].shift(2)
    df['lag_3h'] = df['total_orders'].shift(3)
    
    # Rolling window features
    df['rolling_mean_3h'] = df['lag_1h'].rolling(window=3).mean()
    df['rolling_mean_6h'] = df['lag_1h'].rolling(window=6).mean()
    df['rolling_std_6h'] =  df['lag_1h'].rolling(window=6).std()
    
    # Drop rows with NaN resulting from lags
    df = df.dropna().reset_index(drop=True)
    
    return df
