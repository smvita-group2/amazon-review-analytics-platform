# 01 Architecture

## System Overview

The platform uses a layered architecture separating batch data processing, hybrid ML retrieval, generative response synthesis, and visual analytics.

## Architectural Layers

```text
[ Raw Data Ingestion ] ➔ S3 Bronze Layer
                             │ (AWS Glue + PySpark ETL)
                             ▼
                        S3 Silver Layer (Cleaned & Validated)
                             │ (AWS Glue Master/Aggregates)
                             ▼
                        S3 Gold Layer (Curated & Visualizations)
                             ├──► Athena / Power BI (Analytics)
                             └──► Hybrid RAG ML Pipeline ➔ ChromaDB + BM25
                                       │ (RRF + Cross-Encoder Rerank)
                                       ▼
                                  Google Gemini LLM
                                       ▼
                                Streamlit Web App
```

## Core Components

1. **Data Lake (Amazon S3)**: Medallion architecture storing raw, cleaned, and aggregated Parquet/JSON data.
2. **ETL Pipeline (AWS Glue 4.0 & PySpark)**: Distributed data cleaning, deduplication, schema validation, and aggregation.
3. **Hybrid RAG Engine**: Dual retrieval mechanism combining vector search (ChromaDB) and lexical search (BM25), re-ranked via Cross-Encoder and synthesized by Gemini 3.5/2.5/1.5 Flash.
4. **BI & Analytics**: AWS Glue Data Catalog, Athena views, and Power BI dashboards.
5. **Frontend Application**: Streamlit multi-page web application providing interactive search and dashboard metrics.
6. **Infrastructure as Code**: Terraform modules managing S3 buckets, Glue jobs/crawlers/workflows, and CloudWatch log groups.
