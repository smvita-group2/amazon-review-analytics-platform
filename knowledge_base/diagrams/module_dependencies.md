# Module Dependencies Diagram

## Purpose
Provides a Mermaid graph illustrating Python module dependencies across `streamlit_app/`, `ml_pipeline/`, and `config/`.

## Related Files
- [02 Repository Structure](../02_REPOSITORY_STRUCTURE.md)
- [08 ML Pipeline](../08_ML_PIPELINE.md)

## Key Concepts
- **Python Imports Graph**: Dependency relationships between UI pages, ML search components, vector DB managers, and dataset configuration files.

## Content

```mermaid
graph TD
    STREAMLIT[streamlit_app/1_Product_Search.py]
    ML_PIPE[ml_pipeline/pipeline.py]
    HYBRID[ml_pipeline/retrieval/hybrid_search.py]
    BM25[ml_pipeline/retrieval/bm25_search.py]
    CHROMA[ml_pipeline/vectordb/chromadb_manager.py]
    RRF[ml_pipeline/retrieval/rrf.py]
    RERANK[ml_pipeline/retrieval/reranker.py]
    GEMINI[ml_pipeline/llm/gemini_client.py]
    CONFIG[config/datasets/paths.py & schema.py]

    STREAMLIT --> ML_PIPE
    ML_PIPE --> HYBRID
    ML_PIPE --> GEMINI
    HYBRID --> BM25
    HYBRID --> CHROMA
    HYBRID --> RRF
    HYBRID --> RERANK
    ML_PIPE --> CONFIG
    HYBRID --> CONFIG
```

## Next Reading
- [02 Repository Structure](../02_REPOSITORY_STRUCTURE.md)
