# 00 Project Overview

## Purpose
The Amazon Review Analytics Platform is an intelligent product search and analytics platform that transforms raw e-commerce metadata and customer reviews into actionable insights and conversational answers.

## Related Files
- [01 Architecture](01_ARCHITECTURE.md)
- [02 Repository Structure](02_REPOSITORY_STRUCTURE.md)
- [03 Tech Stack](03_TECH_STACK.md)
- [04 Data Pipeline](04_DATA_PIPELINE.md)
- [20 Agent Index](20_AGENT_INDEX.md)

## Key Concepts
- **Medallion Architecture**: Data lake split into Bronze (raw), Silver (cleaned), and Gold (curated) layers.
- **Hybrid RAG**: Fuses vector dense search (`SentenceTransformers` + `ChromaDB`) with lexical search (`Rank-BM25`) using Reciprocal Rank Fusion (RRF) and Cross-Encoder re-ranking.
- **Generative Synthesis**: Context-grounded response generation via Google Gemini LLM API.

## Content

### Business Problem
Online shoppers encounter significant friction:
- Manually reading hundreds of reviews across multiple product pages.
- Standard search engines failing on complex natural language queries.
- Disconnect between keyword matches and true semantic shopper intent.
- Difficulty comparing feedback and sentiment trends across product variants.

### Core Solution
An end-to-end cloud platform combining big data batch ETL with hybrid RAG:
1. **Medallion Data Lake**: Automated data processing via AWS Glue 4.0 & PySpark.
2. **Hybrid Retrieval**: Combines semantic embeddings (`all-MiniLM-L6-v2`) and Rank-BM25 keyword indices.
3. **Cross-Encoder Reranking**: Re-ranks candidate documents using `ms-marco-MiniLM-L-6-v2`.
4. **Generative RAG**: Context-grounded answer generation via Google Gemini API.
5. **Analytics & Frontend**: Streamlit multi-page web app and Athena / Power BI integrations.

### Core Capabilities
- **Natural Language Search**: Intelligent query execution over product reviews and metadata.
- **Review Summarization**: AI-generated summaries of positive, negative, and key product aspects.
- **Automated Data Processing**: End-to-end PySpark ETL pipeline for Bronze, Silver, and Gold datasets.
- **Infrastructure as Code**: Reproducible AWS infrastructure deployment managed via Terraform.

## Next Reading
- [01 Architecture](01_ARCHITECTURE.md)
