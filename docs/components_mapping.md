# System Components & Capabilities Matrix

This reference details the core components and capabilities implemented across the codebase.

---

| System Capability | Implementation Location in Project | Description |
| :--- | :--- | :--- |
| **AI System Architecture** | `docs/architecture.md`, `docs/system_requirements_nfr.md` | Formal architecture specification, NFR latency budgets, and Mermaid dataflow diagrams. |
| **ETL Pipeline** | `src/data_engineering/kafka_producer.py`, `src/data_engineering/kafka_consumer.py`, `src/data_engineering/etl_batch.py`, `scripts/init_warehouse.sql` | Streaming event ingestion from Kafka to MinIO Lake and batch transformation into PostgreSQL. |
| **Feature Engineering Pipeline** | `src/feature_store/transformer.py`, `src/feature_store/online_store.py`, `src/feature_store/offline_store.py` | Missing value indicators (MNAR/MAR), Z-score standardization, categorical hashing, and Redis caching. |
| **Model Training Pipeline** | `src/modeling/train_ctr.py`, `src/modeling/time_split.py`, `src/modeling/evaluate.py` | Time-series expanding window split (preventing data leakage), XGBoost classifier training, and MLflow logging. |
| **API Development & Serving** | `app/main.py`, `app/api/search.py`, `app/api/recommend.py`, `app/api/feedback.py` | Production FastAPI application exposing `/search`, `/recommend`, `/predict`, and `/feedback` endpoints. |
| **Containerization** | `Dockerfile` | Multi-stage, production-grade container build packaging FastAPI, dependencies, and model runtime. |
| **Local Deployment & Orchestration** | `docker-compose.yml`, `scripts/init_warehouse.sql`, `config/prometheus.yml` | Multi-container orchestrated cluster running API, Postgres+pgvector, Redis, Kafka, and Prometheus. |
| **Model & Latency Monitoring** | `app/core/metrics.py`, `config/prometheus.yml`, `tests/performance/test_latency_sla.py` | Prometheus metrics instrumentation tracking request latency percentiles (P95/P99) and inference throughput. |
| **Covariate Drift Detection** | `src/monitoring/ks_drift_detector.py`, `tests/unit/test_drift.py` | Two-sample Kolmogorov-Smirnov (KS) statistical hypothesis testing detecting covariate shift on serving data. |
| **End-to-End Self-Healing Lifecycle** | `src/monitoring/retrain_trigger.py`, `src/monitoring/champion_challenger.py`, `scripts/run_simulation.py` | Complete closed-loop self-healing lifecycle: stream -> feature -> infer -> drift -> retrain -> champion-challenger gate. |
