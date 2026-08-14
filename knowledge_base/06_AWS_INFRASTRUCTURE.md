# 06 AWS Infrastructure

## Purpose
Details all cloud components provisioned on Amazon Web Services (AWS), including S3 storage buckets, AWS Glue Data Catalog, Glue PySpark jobs, Athena, and CloudWatch.

## Related Files
- [01 Architecture](01_ARCHITECTURE.md)
- [07 Glue Pipeline](07_GLUE_PIPELINE.md)
- [10 Terraform](10_TERRAFORM.md)
- [AWS Infrastructure Diagram](diagrams/aws_infrastructure.md)

## Key Concepts
- **Serverless Cloud Architecture**: Pure serverless execution stack using S3, Glue 4.0, and Athena.
- **Glue Data Catalog**: Central metastore for tracking schema evolution across Silver and Gold tables.
- **CloudWatch Logging**: Centralized logging for tracking distributed PySpark job execution.

## Content

### Provisioned AWS Resources

#### 1. Amazon S3 Data Lake
- **Bucket**: `s3://<project_name>-<environment>-<account_id>` (e.g. `amazon-reviews-dev-data`).
- **Prefix Structure**:
  - `/data/bronze/` - Immutable raw JSON/GZ files.
  - `/data/silver/` - Cleaned master Parquet tables.
  - `/data/gold/` - Curated aggregates & ML output tables.
  - `/scripts/` - Packaged AWS Glue PySpark job scripts.
  - `/extra_jars/` - Custom JAR dependencies.

#### 2. AWS Glue 4.0 Components
- **Glue Database**: `amazon_reviews_db_<environment>` cataloging Silver & Gold tables.
- **Glue PySpark Jobs**:
  - `bronze_to_silver_metadata`
  - `bronze_to_silver_reviews`
  - `silver_master`
  - `gold_visualization`
  - `gold_aggregates`
  - `gold_ml_hybrid_cleaned`
- **Glue Crawlers**: Automated crawler scanning S3 Gold output to register Athena tables.
- **Glue Workflow**: Scheduled triggers controlling Bronze ➔ Silver ➔ Gold execution sequence.

#### 3. Amazon Athena & CloudWatch
- **Amazon Athena**: Interactive SQL query engine running queries against Glue Data Catalog.
- **AWS CloudWatch**: Log Groups (`/aws/glue/jobs/<project_name>`) for Glue job monitoring.

## Next Reading
- [07 Glue Pipeline](07_GLUE_PIPELINE.md)
