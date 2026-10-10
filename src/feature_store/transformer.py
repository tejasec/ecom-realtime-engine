"""
Feature Engineering & Transformation Pipeline
Implements:
1. Missing value imputation with statistical indicator flags for MNAR/MAR variables.
2. Z-score numerical standardization.
3. Feature hashing for high-cardinality categorical variables.
"""

from typing import Dict, List, Any, Optional
import numpy as np
import pandas as pd

class FeatureTransformer:
    def __init__(self, n_hash_features: int = 8):
        self.n_hash_features = n_hash_features
        self.mean_stats: Dict[str, float] = {}
        self.std_stats: Dict[str, float] = {}

    def fit(self, df: pd.DataFrame, numerical_cols: List[str]):
        """Calculates mean and standard deviation for Z-score normalization."""
        for col in numerical_cols:
            if col in df.columns:
                series = df[col].dropna()
                self.mean_stats[col] = float(series.mean()) if not series.empty else 0.0
                std_val = float(series.std()) if not series.empty else 1.0
                self.std_stats[col] = std_val if std_val > 1e-6 else 1.0
        return self

    def transform(self, df: pd.DataFrame, numerical_cols: List[str], categorical_cols: List[str]) -> pd.DataFrame:
        """
        Applies missingness indicators, standardization, and hashing trick.
        """
        transformed = pd.DataFrame(index=df.index)

        # 1. Numerical Missingness Indicators (MNAR/MAR) & Z-score Scaling
        for col in numerical_cols:
            if col in df.columns:
                # Add indicator flag for missing value
                transformed[f"{col}_is_missing"] = df[col].isna().astype(int)
                
                # Impute with mean
                mean = self.mean_stats.get(col, 0.0)
                std = self.std_stats.get(col, 1.0)
                imputed = df[col].fillna(mean)
                
                # Z-score standardization
                transformed[f"{col}_zscore"] = (imputed - mean) / std

        # 2. Categorical Feature Hashing (Hashing Trick for high-cardinality values)
        for col in categorical_cols:
            if col in df.columns:
                for i in range(self.n_hash_features):
                    transformed[f"{col}_hash_{i}"] = 0

                for idx, val in df[col].items():
                    if pd.notna(val):
                        # Murmur-like hash bucket assignment
                        hash_bucket = abs(hash(str(val))) % self.n_hash_features
                        transformed.loc[idx, f"{col}_hash_{hash_bucket}"] = 1

        return transformed

    def fit_transform(self, df: pd.DataFrame, numerical_cols: List[str], categorical_cols: List[str]) -> pd.DataFrame:
        self.fit(df, numerical_cols)
        return self.transform(df, numerical_cols, categorical_cols)
