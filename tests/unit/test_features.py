"""
Unit Test: Feature Transformation Pipeline
"""

import pandas as pd
import numpy as np
import pytest
from src.feature_store.transformer import FeatureTransformer

def test_missing_indicator_and_zscore():
    data = pd.DataFrame({
        "price": [10.0, 20.0, np.nan, 40.0, 50.0],
        "category": ["Electronics", "Books", "Electronics", "Apparel", "Books"]
    })

    transformer = FeatureTransformer(n_hash_features=4)
    transformed = transformer.fit_transform(data, numerical_cols=["price"], categorical_cols=["category"])

    # Check indicator flag
    assert "price_is_missing" in transformed.columns
    assert transformed["price_is_missing"].tolist() == [0, 0, 1, 0, 0]

    # Check Z-score standardization
    assert "price_zscore" in transformed.columns
    # Check categorical hash columns
    for i in range(4):
        assert f"category_hash_{i}" in transformed.columns

    # Verify each row has exactly one hash bucket activated
    hash_sums = transformed[[f"category_hash_{i}" for i in range(4)]].sum(axis=1)
    assert all(s == 1 for s in hash_sums)
