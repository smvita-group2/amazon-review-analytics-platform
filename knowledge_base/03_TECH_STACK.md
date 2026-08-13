# 03 Tech Stack

## Programming Languages

- **Python 3.10 / 3.11**: Primary language for ETL, ML pipeline, and web UI.
- **HCL (HashiCorp Configuration Language)**: Infrastructure provisioning via Terraform.
- **SQL / PySpark SQL**: Querying and aggregating datasets in Glue/Athena.

## Big Data & Cloud Runtime

- **Apache Spark / PySpark**: Distributed data processing engine.
- **AWS Glue 4.0**: Managed PySpark execution environment and Data Catalog.
- **Amazon S3**: Object storage for Medallion architecture layers.
- **Amazon Athena**: Serverless interactive query service.

## Machine Learning & NLP

- **SentenceTransformers**: `all-MiniLM-L6-v2` dense vector embedding generation.
- **ChromaDB**: Local vector database for semantic similarity indexing.
- **Rank-BM25**: Lexical keyword search algorithm (`BM25Okapi`).
- **Cross-Encoder**: `ms-marco-MiniLM-L-6-v2` passage re-ranking.
- **Google Gemini SDK**: `google-genai` for context-grounded response generation.

## Web & Analytics

- **Streamlit**: Web frontend framework.
- **Pandas / PyArrow**: Local dataframe processing and Parquet serialization.
- **Power BI**: Business Intelligence reporting layer over Athena views.

## Infrastructure & DevOps

- **Terraform**: IaC tool for AWS resource deployment.
- **GitHub Actions**: CI/CD automation (`ci.yml`, `deploy.yml`).
- **PyTest / Flake8 / Black / Mypy**: Quality assurance and code formatting.
