# 07 Glue Pipeline

## Glue PySpark Scripts Breakdown

Located in `gluejobs/`:

### 1. `gluejobs/bronze_to_silver/bronze_to_silver_metadata_glue.py`
- **Purpose**: Cleans raw product metadata.
- **Transformations**: Parses array fields, cleans price strings, normalizes product titles, removes duplicate ASINs.
- **Output**: `s3://<bucket>/data/silver/metadata/`.

### 2. `gluejobs/bronze_to_silver/bronze_to_silver_reviews_glue.py`
- **Purpose**: Processes customer review records.
- **Transformations**: Formats Unix timestamp to timestamp column, cleans review body text, validates rating boundaries [1.0, 5.0].
- **Output**: `s3://<bucket>/data/silver/reviews/`.

### 3. `gluejobs/silver_master/silver_master_glue.py`
- **Purpose**: Enriches reviews with product metadata.
- **Transformations**: Left inner join on `parent_asin`, schema normalization, quality check.
- **Output**: `s3://<bucket>/data/silver/silver_master/`.

### 4. `gluejobs/gold/gold_visualization/gold_visualization_glue.py`
- **Purpose**: Generates analytics-ready tables for Athena and Streamlit dashboards.

### 5. `gluejobs/gold/gold_aggergates/gold_aggregates.py`
- **Purpose**: Computes product rating averages, review volume metrics, and sentiment distribution.

### 6. `gluejobs/gold/gold_ml/gold_ml_hybrid_cleaned.py`
- **Purpose**: Prepares sanitized review chunks and metadata documents for ML RAG indexing.
