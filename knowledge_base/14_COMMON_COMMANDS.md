# 14 Common Commands

## Development & Testing

```bash
# Run full PyTest suite
pytest

# Run tests with stdout and verbose output
pytest -sv

# Run specific test file
pytest tests/test_validation.py

# Code formatting & linting
black src/ gluejobs/ ml_pipeline/ streamlit_app/ tests/
isort src/ gluejobs/ ml_pipeline/ streamlit_app/ tests/
flake8 src/ gluejobs/ ml_pipeline/
mypy src/ ml_pipeline/
```

## Streamlit Application

```bash
# Launch Streamlit frontend locally
streamlit run streamlit_app/Home.py
```

## Build & Deployment Scripts

```bash
# Package Glue job scripts & zip dependencies
./scripts/build/package.sh

# Deploy packaged scripts and assets to S3 dev environment
./scripts/deploy/deploy-dev.sh
```

## Terraform Infrastructure

```bash
# Navigate to Terraform directory
cd terraform

# Initialize Terraform modules and plugins
terraform init

# Plan infrastructure deployment
terraform plan -var-file="terraform.tfvars"

# Apply infrastructure changes
terraform apply -var-file="terraform.tfvars" -auto-approve
```

## ML Pipeline Runners

```bash
# Initialize vector database and BM25 index
python ml_pipeline/run_initializer.py

# Run standalone BM25 index builder
python ml_pipeline/run_bm25_builder.py

# Execute ML pipeline test search
python ml_pipeline/test_pipeline.py
```
