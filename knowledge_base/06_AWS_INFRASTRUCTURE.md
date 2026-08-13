# 06 AWS Infrastructure

## Managed AWS Resources

1. **Amazon S3 Data Lake**:
   - Bucket: `s3://<project_name>-<environment>-<account_id>` (e.g. `amazon-reviews-dev-data`).
   - Prefix Structure:
     - `/data/bronze/` - Raw ingestion.
     - `/data/silver/` - Cleaned master tables.
     - `/data/gold/` - Curated aggregates & ML output.
     - `/scripts/` - Packaged Glue PySpark scripts.
     - `/extra_jars/` - Custom dependencies.

2. **AWS Glue 4.0 Components**:
   - **Glue Database**: `amazon_reviews_db_<environment>` cataloging Silver & Gold tables.
   - **Glue PySpark Jobs**:
     - `bronze_to_silver_metadata`
     - `bronze_to_silver_reviews`
     - `silver_master`
     - `gold_visualization`
     - `gold_aggregates`
     - `gold_ml_hybrid_cleaned`
   - **Glue Crawlers**: Automated crawler scanning S3 Gold output to register Athena tables.
   - **Glue Workflow**: Scheduled trigger sequencing Bronze -> Silver -> Gold execution.

3. **Amazon Athena**:
   - Query engine executing analytical views against Glue Data Catalog.

4. **AWS CloudWatch**:
   - Log Groups `/aws/glue/jobs/<project_name>` for ETL job execution monitoring.
