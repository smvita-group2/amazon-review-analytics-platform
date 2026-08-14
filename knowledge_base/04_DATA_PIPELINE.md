# 04 Data Pipeline

## Purpose
Documents the Medallion Data Lake architecture, detailing the step-by-step transformation flow from raw JSON ingestion to cleaned Silver master datasets and curated Gold tables.

## Related Files
- [05 Datasets](05_DATASETS.md)
- [06 AWS Infrastructure](06_AWS_INFRASTRUCTURE.md)
- [07 Glue Pipeline](07_GLUE_PIPELINE.md)
- [Pipeline Diagram](diagrams/pipeline_diagram.md)

## Key Concepts
- **Medallion Data Lake**: Progressive data refinement across Bronze, Silver, and Gold S3 storage layers.
- **Silver Master Join**: Enriching customer review events with normalized product metadata.
- **Gold Outputs**: Partitioned datasets optimized for Athena analytics, BI dashboards, and ML chunk indexing.

## Content

### Medallion Architecture Flow
```text
Raw Ingestion (S3 Bronze) ➔ Cleaning & Deduplication (S3 Silver) ➔ Aggregations (S3 Gold)
```

### Layer Specifications

#### 1. Bronze Layer (Raw Storage)
- **Format**: Raw JSON / GZ files in `s3://<bucket>/data/bronze/`.
- **Purpose**: Immutable raw data preservation and auditing archive.
- **Datasets**: Amazon Product Metadata (`meta_*.json.gz`) and Customer Reviews (`reviews_*.json.gz`).

#### 2. Silver Layer (Cleaned & Validated Data)
- **Format**: Apache Parquet tables in `s3://<bucket>/data/silver/`.
- **Transformation Steps**:
  - Null value filtering and strict schema casting.
  - Timestamp conversion (`reviewTime` -> `TIMESTAMP`).
  - Text normalization (removing HTML, whitespace trimming).
  - Deduplication on primary keys (`parent_asin`, `user_id`, `timestamp`).
  - Silver Master join combining reviews with product metadata.

#### 3. Gold Layer (Curated & ML-Ready Data)
- **Format**: Parquet files partitioned by `category` and `year/month`.
- **Products**:
  - `gold_aggregates`: Product rating distribution, average ratings, and review volume.
  - `gold_visualization`: Analytical tables optimized for Athena and Power BI.
  - `gold_ml_hybrid_cleaned`: Document chunks prepared for ChromaDB vector embeddings and BM25 index building.

## Next Reading
- [05 Datasets](05_DATASETS.md)
