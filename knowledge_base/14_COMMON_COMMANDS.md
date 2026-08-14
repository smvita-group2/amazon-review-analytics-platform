# 14 Common Commands

## Purpose
Serves as an execution cheatsheet providing copy-pasteable CLI commands for testing, code formatting, running the Streamlit web app, packaging scripts, deploying Terraform, and executing ML runners.

## Related Files
- [10 Terraform](10_TERRAFORM.md)
- [12 Testing](12_TESTING.md)
- [13 Coding Guidelines](13_CODING_GUIDELINES.md)

## Key Concepts
- **Standard Toolchain**: PyTest, Black, Isort, Flake8, Mypy, Streamlit, Terraform, and custom bash deploy scripts.

## Content

### Development & Testing
```bash
# Run full PyTest test suite
pytest

# Run tests with stdout output and verbose mode
pytest -sv

# Run specific test module
pytest tests/test_validation.py

# Code formatting & static linting
black src/ gluejobs/ ml_pipeline/ streamlit_app/ tests/
isort src/ gluejobs/ ml_pipeline/ streamlit_app/ tests/
flake8 src/ gluejobs/ ml_pipeline/
mypy src/ ml_pipeline/
```

### Streamlit Application
```bash
# Launch Streamlit web app locally
streamlit run streamlit_app/Home.py
```

### Packaging & AWS Deployment
```bash
# Package Glue job scripts & zip dependencies
./scripts/build/package.sh

# Deploy packaged scripts and assets to S3 dev environment
./scripts/deploy/deploy-dev.sh
```

### Infrastructure Provisioning (Terraform)
```bash
# Navigate to Terraform working directory
cd terraform

# Initialize Terraform modules and providers
terraform init

# Preview deployment plan
terraform plan -var-file="terraform.tfvars"

# Apply infrastructure changes
terraform apply -var-file="terraform.tfvars" -auto-approve
```

### ML Pipeline Execution
```bash
# Initialize ChromaDB vector DB and BM25 index
python ml_pipeline/run_initializer.py

# Run standalone BM25 index builder
python ml_pipeline/run_bm25_builder.py

# Execute ML pipeline test search script
python ml_pipeline/test_pipeline.py
```

## Next Reading
- [15 Decisions](15_DECISIONS.md)
