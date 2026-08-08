# Amazon Review Analytics Platform

A scalable, serverless, cloud-native analytics platform for processing Amazon product reviews using a Medallion Architecture (Bronze, Silver, Gold layers) powered entirely by **AWS Glue**, **Amazon S3**, **AWS Glue Data Catalog**, **Amazon CloudWatch**, **Terraform**, and **GitHub Actions**.

---

## Architectural Overview

```
Developer Push
      ↓
GitHub Actions (CI/CD)
      ↓
CI Checks (Black, isort, Flake8, Pytest, Bandit, MyPy, Terraform Validate)
      ↓
Merge to develop / main
      ↓
Build Deployment Artifact (ZIP) + Sync Glue Scripts to S3
      ↓
Merge to main
      ↓
Terraform Apply
      ↓
AWS Glue PySpark Jobs (Bronze → Silver → Gold)
      ↓
AWS Glue Catalog Crawler
      ↓
Amazon Athena / Analytics & BI Dashboards
```

---

## Platform Infrastructure & Stack

- **Data Processing**: AWS Glue PySpark 4.0 Jobs (Serverless ETL)
- **Data Storage**: Amazon S3 Medallion Storage (`bronze/`, `silver/`, `gold/`)
- **Metadata & Catalog**: AWS Glue Data Catalog Database & Crawlers
- **Monitoring & Logging**: Amazon CloudWatch Logs & Metrics
- **Infrastructure as Code**: Terraform (>= 1.5)
- **CI/CD Pipeline**: GitHub Actions (Automated CI checks & Branch-gated CD deployment)

---

## Data Pipeline Architecture (Medallion Layers)

1. **Bronze Layer (`s3://<bucket>/bronze/`)**:
   - Stores raw Amazon review and metadata JSON/Parquet files.
2. **Silver Layer (`s3://<bucket>/silver/`)**:
   - `bronze_to_silver_reviews_glue.py`: Standardizes review schema, cleans text fields, formats timestamps, deduplicates records.
   - `bronze_to_silver_metadata_glue.py`: Parses product metadata, cleans attributes, normalizes categories.
   - `silver_master_glue.py`: Joins Silver reviews with product metadata to produce the unified Silver Master dataset.
3. **Gold Layer (`s3://<bucket>/gold/`)**:
   - `gold_visualization_glue.py`: Prepares aggregated metrics for visualization dashboards.
   - `gold_aggregates.py`: Generates rating distributions, product-level sentiment, and monthly trend aggregates.
   - `gold_ml_hybrid_cleaned.py`: Prepares cleaned, high-quality feature datasets for the Hybrid RAG ML pipeline.
4. **Glue Crawler & Athena**:
   - The Glue Crawler runs automatically following Gold job completion, updating tables in `amazon_reviews_db` for querying in Amazon Athena.

---

## Repository Structure

```
.
├── .github/
│   └── workflows/
│       ├── ci.yml          # CI Quality & Security Checks
│       └── deploy.yml      # CD Artifact Build, S3 Upload, & Terraform Apply
├── config/                  # Configuration files
├── gluejobs/                # AWS Glue PySpark Job Scripts
│   ├── bronze_to_silver/
│   │   ├── bronze_to_silver_metadata_glue.py
│   │   └── bronze_to_silver_reviews_glue.py
│   ├── silver_master/
│   │   └── silver_master_glue.py
│   └── gold/
│       ├── gold_aggergates/
│       │   └── gold_aggregates.py
│       ├── gold_ml/
│       │   └── gold_ml_hybrid_cleaned.py
│       └── gold_visualization/
│           └── gold_visualization_glue.py
├── ml_pipeline/             # Machine Learning & Hybrid RAG Pipeline
├── scripts/                 # Build & Deployment Utility Scripts
│   ├── build/
│   │   ├── build.sh
│   │   └── package.sh
│   └── deploy/
│       └── deploy-dev.sh
├── src/                     # Shared Python utilities & core modules
├── terraform/               # Infrastructure as Code
│   ├── main.tf
│   ├── variables.tf
│   ├── outputs.tf
│   ├── terraform.tfvars
│   └── modules/
│       ├── glue/            # Glue DB, Jobs, Crawlers & Workflows
│       ├── monitoring/      # CloudWatch Logging & Metrics
│       └── s3/              # S3 Bucket & Medallion Folders
└── tests/                   # Pytest Unit & Integration Tests
```

---

## Local Development & Validation

### 1. Install Dependencies
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Run Quality & Security Checks
```bash
# Code Formatting Check
black --check .

# Import Sorting Check
isort --check-only .

# Linting
flake8 .

# Unit Tests & Coverage
pytest --cov=src --cov-report=term-missing

# Security Audit
bandit -r src

# Static Type Checking
mypy --explicit-package-bases src
```

### 3. Terraform Validation
```bash
cd terraform
terraform init -backend=false
terraform fmt -check -recursive
terraform validate
```

---

## CI/CD Pipeline & GitHub Secrets

### GitHub Secrets Required:
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_SESSION_TOKEN`

### GitHub Variables Required:
- `AWS_REGION` (e.g., `us-east-1`)
- `S3_BUCKET` (e.g., `amazon-review-analytics-shreyash-471112764802`)
- `S3_ARTIFACT_PREFIX` (e.g., `artifacts`)

### Deployment Behavior:
- **CI Workflow (`ci.yml`)**: Runs on all pushes and pull requests to validate Python code and Terraform formatting.
- **CD Workflow (`deploy.yml`)**: On pushes to `develop` or `main`:
  - Packages deployment ZIP and syncs Glue scripts to S3.
  - Runs `terraform plan`.
  - Executes `terraform apply` **ONLY** on the `main` branch.
