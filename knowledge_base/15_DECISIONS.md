# 15 Architectural Decisions

## Architectural Decision Log (ADL)

Extracting explicitly documented and implemented design choices in the repository:

1. **Medallion Architecture Pattern**:
   - *Decision*: Divide S3 data lake into Bronze (Raw), Silver (Cleaned), and Gold (Curated/Aggregated) layers.
   - *Rationale*: Guarantees data lineage, auditability, and clear separation of raw data preservation from analytical aggregations.

2. **AWS Glue 4.0 & PySpark for Big Data ETL**:
   - *Decision*: Standardize batch transformation pipelines on AWS Glue 4.0 with PySpark.
   - *Rationale*: Provides serverless distributed compute scaling for multi-GB Amazon review datasets.

3. **Hybrid RAG (Dense + Sparse Retrieval)**:
   - *Decision*: Combine SentenceTransformers vector search (ChromaDB) with Rank-BM25 lexical search via Reciprocal Rank Fusion (RRF).
   - *Rationale*: Pure vector search misses exact product names/ASIN keywords; pure keyword search fails on semantic natural language queries.

4. **Cross-Encoder Re-ranking Step**:
   - *Decision*: Apply `ms-marco-MiniLM-L-6-v2` cross-encoder re-ranking on fused top candidate documents before prompting Gemini.
   - *Rationale*: Filters out low-relevance contexts and significantly improves LLM generation accuracy.

5. **Google Gemini LLM for Response Generation**:
   - *Decision*: Integrate Google Gemini API (`google-genai` SDK) for prompt synthesis.
   - *Rationale*: Provides fast inference times, large context window support, and high factual grounding on review contexts.

6. **Terraform Infrastructure as Code**:
   - *Decision*: Provision all AWS resources (S3, Glue Jobs/Catalog/Crawlers, CloudWatch) via modular Terraform code.
   - *Rationale*: Eliminates manual console setup and guarantees environment reproducibility across environments.
