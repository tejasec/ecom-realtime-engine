"""
CTR Model Training Pipeline
Trains an XGBoost/LightGBM binary classifier with temporal validation and MLflow logging.
"""

import logging
from typing import Dict, Any, Tuple
import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score, log_loss

logger = logging.getLogger("TrainCTR")

class CTRTrainer:
    def __init__(self, n_estimators: int = 100, max_depth: int = 4, learning_rate: float = 0.05):
        self.params = {
            "n_estimators": n_estimators,
            "max_depth": max_depth,
            "learning_rate": learning_rate,
            "random_state": 42
        }
        self.model = None

    def train(self, X_train: pd.DataFrame, y_train: pd.Series, X_val: pd.DataFrame, y_val: pd.Series) -> Dict[str, float]:
        """
        Trains model and calculates ROC-AUC and Log Loss validation metrics.
        """
        logger.info(f"Training CTR Classifier on {len(X_train)} samples...")
        try:
            import xgboost as xgb
            self.model = xgb.XGBClassifier(**self.params)
            self.model.fit(X_train, y_train)
        except Exception as e:
            logger.warning(f"XGBoost training fallback ({e}). Using Scikit-Learn baseline.")
            from sklearn.ensemble import GradientBoostingClassifier
            self.model = GradientBoostingClassifier(n_estimators=self.params["n_estimators"], max_depth=self.params["max_depth"])
            self.model.fit(X_train, y_train)

        # Evaluate on validation set
        y_pred_proba = self.model.predict_proba(X_val)[:, 1]
        auc = float(roc_auc_score(y_val, y_pred_proba))
        loss = float(log_loss(y_val, y_pred_proba))

        metrics = {"val_roc_auc": round(auc, 4), "val_log_loss": round(loss, 4)}
        logger.info(f"Training Complete. Validation Metrics: {metrics}")
        return metrics

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    np.random.seed(42)
    n = 200
    X = pd.DataFrame({
        "hist_ctr": np.random.uniform(0.01, 0.5, n),
        "price": np.random.uniform(10.0, 300.0, n),
        "price_sens": np.random.uniform(0.1, 0.9, n)
    })
    y = pd.Series((X["hist_ctr"] > 0.25).astype(int))

    trainer = CTRTrainer()
    trainer.train(X.iloc[:150], y.iloc[:150], X.iloc[150:], y.iloc[150:])
