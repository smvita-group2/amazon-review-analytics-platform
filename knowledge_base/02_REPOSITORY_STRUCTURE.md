# 02 Repository Structure

## Purpose
Outlines the physical workspace directory organization, module boundaries, and component responsibilities across the platform.

## Related Files
- [00 Project Overview](00_PROJECT_OVERVIEW.md)
- [01 Architecture](01_ARCHITECTURE.md)
- [Module Index](generated/module_index.md)
- [Functions Index](generated/functions.md)

## Key Concepts
- **Modular Layout**: Strict separation between core PySpark source (`src/`), cloud Glue job entry scripts (`gluejobs/`), ML retrieval engine (`ml_pipeline/`), Streamlit UI (`streamlit_app/`), and IaC (`terraform/`).
- **Configuration Isolation**: Central configuration in `config/` decoupled from application logic.

## Content

### Directory Layout
```text
amazon-review-analytics-platform/
├── config/              # Central dataset schemas, path maps, and constants
├── docs/                # Architecture documentation assets
├── gluejobs/            # AWS Glue PySpark job entry scripts (Bronze, Silver, Gold)
├── ml_pipeline/         # Hybrid RAG engine, embeddings, vector DB, LLM synthesis
├── scripts/             # Packaging, deployment, and utility shell scripts
├── src/                 # PySpark ETL transformations, validators, and loggers
├── streamlit_app/       # Streamlit web application pages and custom theme
├── terraform/           # IaC configurations (S3, Glue, CloudWatch modules)
├── tests/               # PyTest unit, validation, and pipeline integration tests
├── .github/             # CI/CD workflows for testing and deployment
├── pyproject.toml       # Code quality configurations (Black, Isort, Mypy)
├── requirements.txt     # Production Python dependencies
└── README.md            # Primary repository README
```

### Module Responsibilities
- **`src/`**: Reusable PySpark transformation, data validation, and logging utilities used by Glue jobs.
- **`gluejobs/`**: Standalone AWS Glue PySpark scripts deployed to S3 for distributed execution.
- **`ml_pipeline/`**: Document chunking, dense vector embeddings, ChromaDB, BM25 indices, RRF fusion, Cross-Encoder, and Gemini LLM.
- **`streamlit_app/`**: Interactive web app including Home overview, Product Search RAG page, and Analytics Dashboard.
- **`terraform/`**: Infrastructure as Code scripts provisioning S3, Glue, Catalog, Crawlers, and IAM roles.
- **`tests/`**: PyTest test suite covering PySpark logic, validation, ML pipeline, and smoke tests.

## Next Reading
- [03 Tech Stack](03_TECH_STACK.md)
