# System Requirements & Non-Functional Requirements (NFRs)

---

## 1. Business Problem Formulation & ML Mapping

| Dimension | Description |
| :--- | :--- |
| **Business Objective** | Maximize user engagement, reduce search exit rates, and increase Click-Through Rate (CTR) and conversion. |
| **ML Task 1 (Search)** | Dense Vector Semantic Search: Query-to-Product semantic embedding similarity (Cosine distance over 384-d vectors). |
| **ML Task 2 (Ranking)** | Binary Classification / Pointwise Ranking: Predict $P(\text{click} = 1 \mid \text{user}, \text{item}, \text{context})$. |
| **Supervision Strategy**| Primary live user clickstream capture combined with programmatic weak supervision (Snorkel heuristics for intent tagging). |

---

## 2. Non-Functional Requirements (NFRs) & Latency Budgets

```
Total Budget: P99 < 100 ms
├── Network & Ingress:          ~10 ms
├── Redis Feature Fetch:         ~2-5 ms
├── Model Inference (XGBoost):  ~15-25 ms
├── pgvector Cosine Search:     ~20-35 ms
└── Response Serialization:      ~5 ms
Buffer / Headroom:              ~20 ms
```

- **P99 Tail Latency:** All recommendation and search responses must return in under **100 ms**.
- **P95 Tail Latency:** Expected under **60 ms**.
- **Availability:** 99.9% uptime target with container restart policies and health checks.
- **Data Freshness:** User interaction events must update online features in Redis within **5 seconds** of event emission.
- **Privacy & Security:** Complete PII redaction; user UUIDs pseudonymized before data lake persistence.

---

## 3. Train-Serving Skew Prevention Strategy

To ensure zero train-serving skew:
1. **Centralized Transformation Module:** Feature scaling, imputation flags, and categorical encoding are implemented in `src/feature_store/transformer.py` and reused across both offline batch pipelines and online API serving.
2. **Dual-Headed Store Paradigm:**
   - **Offline Store (Parquet/Postgres):** Time-stamped snapshots prevent temporal leakage.
   - **Online Store (Redis):** Key-value caches identical schema fields (`user:{uuid}:features`).
