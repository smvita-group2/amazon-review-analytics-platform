# Architecture Diagram

## Purpose
Provides a visual Mermaid flowchart representing the Amazon Review Analytics Platform end-to-end layered architecture.

## Related Files
- [01 Architecture](../01_ARCHITECTURE.md)
- [06 AWS Infrastructure](../06_AWS_INFRASTRUCTURE.md)
- [08 ML Pipeline](../08_ML_PIPELINE.md)

## Key Concepts
- **Layer Separation**: Unidirectional flow from raw S3 ingestion to distributed Glue PySpark ETL, hybrid ML retrieval, Gemini LLM synthesis, and Streamlit frontend UI.

## Content

```mermaid
graph TD
    subgraph Data Lake - S3
        A[Bronze Layer: Raw JSON/GZ] --> B[AWS Glue + PySpark ETL]
        B --> C[Silver Layer: Cleaned Parquet]
        C --> D[Gold Layer: Curated Data]
    end

    subgraph Business Intelligence
        D --> E[Glue Catalog Crawler]
        E --> F[Amazon Athena Views]
        F --> G[Power BI Analytics]
    end

    subgraph Hybrid RAG Engine
        D --> H[Product Document Builder]
        H --> I[ChromaDB Vector Store]
        H --> J[Rank-BM25 Lexical Index]
        I --> K[Reciprocal Rank Fusion - RRF]
        J --> K
        K --> L[Cross-Encoder Reranker]
        L --> M[Google Gemini LLM]
    end

    M --> N[Streamlit Web App]
    G --> N
```

## Next Reading
- [01 Architecture](../01_ARCHITECTURE.md)
