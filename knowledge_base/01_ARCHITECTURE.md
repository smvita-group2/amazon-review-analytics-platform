# 01 Architecture

## Purpose
Provides an architectural overview of the system, detailing the decoupled layers for batch data ingestion, distributed PySpark ETL, hybrid RAG retrieval, LLM synthesis, and web UI.

## Related Files
- [00 Project Overview](00_PROJECT_OVERVIEW.md)
- [04 Data Pipeline](04_DATA_PIPELINE.md)
- [06 AWS Infrastructure](06_AWS_INFRASTRUCTURE.md)
- [08 ML Pipeline](08_ML_PIPELINE.md)
- [Architecture Diagram](diagrams/architecture_diagram.md)

## Key Concepts
- **Layered Decoupling**: Separation of big data batch processing (AWS Glue) from online hybrid retrieval (ChromaDB + BM25) and frontend presentation (Streamlit).
- **Data Lineage**: Unidirectional flow from raw S3 Bronze to Silver master tables to Gold aggregates and vector indices.
- **RAG Pipeline**: Dense + sparse document retrieval with RRF fusion, Cross-Encoder re-ranking, and Gemini LLM synthesis.

## Content

### Architectural Flow
```text
[ Raw Data Ingestion ] ➔ S3 Bronze Layer
                             │ (AWS Glue 4.0 + PySpark ETL)
                             ▼
                        S3 Silver Layer (Cleaned & Validated)
                             │ (AWS Glue Master & Aggregates)
                             ▼
                        S3 Gold Layer (Curated & ML-Ready)
                             ├──► Athena / Power BI (BI Analytics)
                             └──► Hybrid RAG ML Pipeline ➔ ChromaDB + BM25
                                       │ (RRF + Cross-Encoder Rerank)
                                       ▼
                                  Google Gemini LLM
                                       ▼
                                Streamlit Web Application
```

### Core Components
1. **Data Lake (Amazon S3)**: Medallion architecture storing raw JSON, cleaned Parquet, and curated Gold datasets.
2. **ETL Engine (AWS Glue 4.0 & PySpark)**: Distributed cleaning, deduplication, schema validation, and table joining.
3. **Hybrid RAG Engine**: Dual retrieval mechanism combining vector search (ChromaDB) and lexical search (Rank-BM25), re-ranked via Cross-Encoder (`ms-marco-MiniLM-L-6-v2`) and synthesized by Gemini LLM.
4. **Business Intelligence**: AWS Glue Data Catalog, serverless Amazon Athena views, and Power BI dashboards.
5. **Web Application**: Streamlit multi-page frontend providing natural language search and analytics dashboard.
6. **Infrastructure as Code**: Terraform modules managing S3 buckets, Glue jobs/crawlers/workflows, and CloudWatch log groups.

## Next Reading
- [02 Repository Structure](02_REPOSITORY_STRUCTURE.md)
