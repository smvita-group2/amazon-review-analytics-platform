# 15 Architectural Decisions

## Purpose
Documents the explicit Architectural Decision Log (ADL), detailing major architectural design choices, technical tradeoffs, and underlying design rationale.

## Related Files
- [01 Architecture](01_ARCHITECTURE.md)
- [04 Data Pipeline](04_DATA_PIPELINE.md)
- [08 ML Pipeline](08_ML_PIPELINE.md)
- [10 Terraform](10_TERRAFORM.md)

## Key Concepts
- **Architectural Decision Log (ADL)**: Persistent record of architectural choices and justification.
- **Tradeoff Analysis**: Justifying specific technologies (AWS Glue 4.0, Hybrid RAG, Cross-Encoder, Gemini LLM, Terraform).

## Content

### Architectural Decision Log

#### 1. Medallion Architecture Pattern
- **Decision**: Organize S3 storage into Bronze (Raw), Silver (Cleaned), and Gold (Curated/Aggregated) layers.
- **Rationale**: Guarantees raw data preservation, complete data auditability, clean schema boundaries, and decoupled analytics layer.

#### 2. AWS Glue 4.0 & PySpark for Big Data ETL
- **Decision**: Standardize batch transformations on serverless AWS Glue 4.0 PySpark jobs.
- **Rationale**: Delivers automatic compute scaling for multi-GB e-commerce review datasets without managing persistent Spark clusters.

#### 3. Hybrid RAG (Dense Embeddings + Sparse BM25)
- **Decision**: Fuse SentenceTransformers (`all-MiniLM-L6-v2`) vector search with Rank-BM25 keyword search via Reciprocal Rank Fusion (RRF).
- **Rationale**: Pure vector search struggles with exact product ASIN/model terms; pure keyword search fails on semantic natural language queries.

#### 4. Cross-Encoder Re-ranking Step
- **Decision**: Insert `ms-marco-MiniLM-L-6-v2` cross-encoder re-ranking after RRF fusion.
- **Rationale**: Filters out noise candidates, improves precision, and prevents LLM context window overflow.

#### 5. Google Gemini LLM Integration
- **Decision**: Use Google Gemini API (`google-genai` SDK) for RAG answer generation.
- **Rationale**: Delivers fast inference latency, large context handling, and high factual accuracy on review context grounding.

#### 6. Modular Terraform Infrastructure as Code
- **Decision**: Provision all AWS cloud resources via modular Terraform configurations.
- **Rationale**: Eliminates manual AWS console changes and guarantees environment reproducibility across dev, staging, and prod.

## Next Reading
- [16 TODO](16_TODO.md)
