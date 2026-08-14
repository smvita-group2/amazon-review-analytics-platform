# 03 Tech Stack

## Purpose
Details the technical ecosystem, programming languages, libraries, cloud infrastructure, and DevOps tools powering the platform.

## Related Files
- [01 Architecture](01_ARCHITECTURE.md)
- [06 AWS Infrastructure](06_AWS_INFRASTRUCTURE.md)
- [08 ML Pipeline](08_ML_PIPELINE.md)
- [10 Terraform](10_TERRAFORM.md)

## Key Concepts
- **Distributed Big Data**: PySpark and AWS Glue 4.0 for multi-gigabyte dataset transformations.
- **Hybrid Search ML**: Combining SentenceTransformers (`all-MiniLM-L6-v2`), ChromaDB, Rank-BM25, and Cross-Encoder (`ms-marco-MiniLM-L-6-v2`).
- **Generative AI**: Google Gemini API via `google-genai` SDK for grounded response generation.

## Content

### Programming Languages
- **Python 3.10 / 3.11**: Primary language for PySpark ETL, ML hybrid search, and Streamlit UI.
- **HCL (HashiCorp Configuration Language)**: Infrastructure provisioning via Terraform.
- **SQL / PySpark SQL**: Analytical queries and schema definitions for Athena/Glue.

### Big Data & Cloud Processing
- **Apache Spark / PySpark**: Distributed data processing and transformation engine.
- **AWS Glue 4.0**: Serverless PySpark job execution environment and Data Catalog.
- **Amazon S3**: Object storage for Medallion architecture (Bronze, Silver, Gold).
- **Amazon Athena**: Serverless interactive SQL query service over S3 tables.

### Machine Learning & NLP
- **SentenceTransformers**: Dense vector embedding generation (`all-MiniLM-L6-v2`).
- **ChromaDB**: Local vector database for semantic similarity indexing.
- **Rank-BM25**: Lexical keyword search algorithm (`BM25Okapi`).
- **Cross-Encoder**: Passage re-ranking model (`ms-marco-MiniLM-L-6-v2`).
- **Google Gemini SDK**: Context-grounded response generation (`google-genai`).

### Web & Business Intelligence
- **Streamlit**: Multi-page Python web application framework.
- **Pandas / PyArrow**: In-memory dataframe processing and Parquet serialization.
- **Power BI**: Business intelligence visualization over Athena SQL views.

### DevOps & Quality Assurance
- **Terraform**: Infrastructure as Code deployment automation.
- **GitHub Actions**: CI/CD pipeline automation (`ci.yml`, `deploy.yml`).
- **PyTest / Black / Isort / Mypy / Flake8**: Testing, linting, formatting, and static typing.

## Next Reading
- [04 Data Pipeline](04_DATA_PIPELINE.md)
