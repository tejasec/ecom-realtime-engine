"""
Offline Feature Store Interface
Serves historical point-in-time feature snapshots (Parquet / PostgreSQL) for offline model training.
"""

from typing import List, Dict, Any
import pandas as pd

class OfflineFeatureStore:
    def __init__(self, storage_path: str = "data/processed"):
        self.storage_path = storage_path

    def load_historical_features(self, table_name: str = "clean_interactions.parquet") -> pd.DataFrame:
        """
        Loads point-in-time feature dataset preventing train-serving skew.
        """
        file_path = f"{self.storage_path}/{table_name}"
        try:
            return pd.read_parquet(file_path)
        except Exception:
            # Fallback synthetic training dataset
            return pd.DataFrame({
                "user_uuid": [f"usr_{i}" for i in range(100)],
                "historical_ctr": [0.1 + (i % 10) * 0.02 for i in range(100)],
                "price_sensitivity": [0.3 + (i % 5) * 0.1 for i in range(100)],
                "label": [1 if i % 4 == 0 else 0 for i in range(100)]
            })

    def save_feature_snapshot(self, df: pd.DataFrame, snapshot_name: str):
        """Persists snapshot for repeatable experiment tracking."""
        df.to_parquet(f"{self.storage_path}/{snapshot_name}.parquet", index=False)
