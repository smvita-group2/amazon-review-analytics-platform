# 04 Data Pipeline

## Medallion Architecture Flow

```text
Raw Ingestion (S3 Bronze) ➔ Cleaning & Deduplication (S3 Silver) ➔ Aggregations (S3 Gold)
```

## Layer Specifications

### 1. Bronze Layer (Raw Storage)
- **Format**: Raw JSON / GZ files in `s3://<bucket>/data/bronze/`.
- **Purpose**: Archival and exact historical raw data preservation.
- **Datasets**: Amazon Product Metadata (`meta_*.json.gz`) and Customer Reviews (`reviews_*.json.gz`).

### 2. Silver Layer (Cleaned & Validated Data)
- **Format**: Apache Parquet / Delta.
- **Transformation Steps**:
  - Null value filtering and schema casting.
  - Timestamp parsing (`reviewTime` -> `TIMESTAMP`).
  - Text cleaning (removing HTML tags, normalizing text).
  - De-duplication on primary keys (`parent_asin`, `user_id`, `timestamp`).
  - Silver Master join combining reviews with product metadata.

### 3. Gold Layer (Curated & ML-Ready Data)
- **Format**: Parquet files partitioned by category/date.
- **Products**:
  - `gold_aggregates`: Product-level review summaries, average ratings, rating distribution.
  - `gold_visualization`: Analytical tables optimized for Athena and Power BI.
  - `gold_ml_hybrid_cleaned`: Document chunks prepared for embedding and BM25 index building.
