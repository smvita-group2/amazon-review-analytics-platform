# 02 Repository Structure

## Workspace Overview

```text
amazon-review-analytics-platform/
├── config/              # Central dataset schemas, path configs, and constants
├── docs/                # Architecture diagrams and documentation assets
├── gluejobs/            # AWS Glue PySpark job entry scripts (Bronze, Silver, Gold)
├── ml_pipeline/         # Hybrid RAG ML engine, embeddings, vector DB, LLM integration
├── scripts/             # Build, packaging, and AWS Glue deployment shell scripts
├── src/                 # PySpark ETL modules, data transformers, and validators
├── streamlit_app/       # Streamlit web application pages and custom styling
├── terraform/           # IaC configurations (S3, Glue, CloudWatch modules)
├── tests/               # PyTest unit, validation, and integration tests
├── .github/             # CI/CD workflows for testing and deployment
├── pyproject.toml       # Python code quality tools configuration (Black, Isort, Mypy)
├── requirements.txt     # Production dependencies for local and cloud runtimes
└── README.md            # Primary repository README
```

## Module Responsibilities

- **`src/`**: Shared PySpark transformation, ingestion, and validation logic reused by Glue jobs.
- **`gluejobs/`**: Standalone AWS Glue job scripts deployed to S3 for distributed execution.
- **`ml_pipeline/`**: Document generation, embeddings, ChromaDB, BM25 index, RRF, Cross-Encoder, and Gemini LLM.
- **`streamlit_app/`**: User interface containing Home overview, Product Search RAG page, and Analytics Dashboard.
- **`terraform/`**: Automated AWS infrastructure provisioning with modular Terraform scripts.
- **`tests/`**: Test suite covering PySpark transformations, validators, ML components, and smoke tests.
