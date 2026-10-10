"""
Temporal Data Splitter
Implements an expanding-window time-series split to prevent temporal data leakage.
"""

from typing import Generator, Tuple
import pandas as pd
import numpy as np

class TimeSeriesSplitter:
    def __init__(self, n_splits: int = 3, test_size_ratio: float = 0.2):
        self.n_splits = n_splits
        self.test_size_ratio = test_size_ratio

    def split(self, df: pd.DataFrame, time_column: str) -> Generator[Tuple[pd.DataFrame, pd.DataFrame], None, None]:
        """
        Generates expanding-window train and test splits strictly ordered by time.
        """
        # Sort chronologically
        df_sorted = df.sort_values(by=time_column).reset_index(drop=True)
        total_rows = len(df_sorted)
        test_size = int(total_rows * self.test_size_ratio)

        for i in range(1, self.n_splits + 1):
            train_end = total_rows - (self.n_splits - i + 1) * test_size
            test_end = train_end + test_size

            train_df = df_sorted.iloc[:train_end]
            test_df = df_sorted.iloc[train_end:test_end]

            yield train_df, test_df
