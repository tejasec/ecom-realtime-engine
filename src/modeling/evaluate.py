"""
Model Evaluation Benchmarking Suite
Assesses CTR classification (ROC-AUC, Precision, Recall, F1)
and semantic search retrieval (Cosine Similarity, Context Precision).
"""

from typing import Dict, Any, List
import numpy as np
from sklearn.metrics import roc_auc_score, precision_score, recall_score, f1_score

class ModelEvaluator:
    @staticmethod
    def evaluate_classifier(y_true: List[int], y_pred_proba: List[float], threshold: float = 0.5) -> Dict[str, float]:
        """Calculates classification metrics for ranking / click prediction."""
        y_true_arr = np.array(y_true)
        y_prob_arr = np.array(y_pred_proba)
        y_pred = (y_prob_arr >= threshold).astype(int)

        return {
            "roc_auc": round(float(roc_auc_score(y_true_arr, y_prob_arr)), 4),
            "precision": round(float(precision_score(y_true_arr, y_pred, zero_division=0)), 4),
            "recall": round(float(recall_score(y_true_arr, y_pred, zero_division=0)), 4),
            "f1_score": round(float(f1_score(y_true_arr, y_pred, zero_division=0)), 4)
        }

    @staticmethod
    def evaluate_search_retrieval(query_vec: np.ndarray, doc_vecs: np.ndarray) -> float:
        """Computes mean cosine similarity for retrieved items."""
        norm_q = query_vec / np.linalg.norm(query_vec)
        norms_d = doc_vecs / np.linalg.norm(doc_vecs, axis=1, keepdims=True)
        similarities = np.dot(norms_d, norm_q)
        return float(np.mean(similarities))
