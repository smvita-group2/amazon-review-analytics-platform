# 07 Glue Pipeline

## Purpose
Provides a detailed breakdown of the AWS Glue PySpark job entry scripts located in `gluejobs/`, specifying input sources, transformation logic, and target S3 destinations.

## Related Files
- [04 Data Pipeline](04_DATA_PIPELINE.md)
- [06 AWS Infrastructure](06_AWS_INFRASTRUCTURE.md)
- [Pipeline Diagram](diagrams/pipeline_diagram.md)

## Key Concepts
- **AWS Glue Job Entry Scripts**: Python scripts deployed to S3 and executed by Glue 4.0 PySpark workers.
- **PySpark Transformations**: Reusable logic imported from `src/` modules.
- **Data Validation**: Rating boundary checks, null cleaning, and schema validation.

## Content

### Glue PySpark Job Scripts (`gluejobs/`)

#### 1. `gluejobs/bronze_to_silver/bronze_to_silver_metadata_glue.py`
- **Purpose**: Ingests and cleans raw product metadata.
- **Transformations**: Array field parsing, price string cleaning, title normalization, ASIN deduplication.
- **Output**: `s3://<bucket>/data/silver/metadata/`.

#### 2. `gluejobs/bronze_to_silver/bronze_to_silver_reviews_glue.py`
- **Purpose**: Processes raw customer review records.
- **Transformations**: Unix timestamp conversion, review text cleaning, rating boundary validation [1.0, 5.0].
- **Output**: `s3://<bucket>/data/silver/reviews/`.

#### 3. `gluejobs/silver_master/silver_master_glue.py`
- **Purpose**: Enriches reviews with product metadata via left inner join on `parent_asin`.
- **Transformations**: Schema normalization, quality check validation, combined master table creation.
- **Output**: `s3://<bucket>/data/silver/silver_master/`.

#### 4. `gluejobs/gold/gold_visualization/gold_visualization_glue.py`
- **Purpose**: Generates analytics-ready tables for Athena queries and Streamlit dashboards.

#### 5. `gluejobs/gold/gold_aggergates/gold_aggregates.py`
- **Purpose**: Computes product rating averages, review volume metrics, and rating distributions.

#### 6. `gluejobs/gold/gold_ml/gold_ml_hybrid_cleaned.py`
- **Purpose**: Prepares sanitized review chunks and metadata documents for ML RAG indexing.

## Next Reading
- [08 ML Pipeline](08_ML_PIPELINE.md)
