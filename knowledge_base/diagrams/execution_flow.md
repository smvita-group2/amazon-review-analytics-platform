# Execution Flow Diagram

## Purpose
Provides a Mermaid sequence diagram detailing step-by-step query execution flow through the Hybrid RAG engine.

## Related Files
- [08 ML Pipeline](../08_ML_PIPELINE.md)
- [09 Streamlit Pages](../09_STREAMLIT_PAGES.md)

## Key Concepts
- **Hybrid RAG Sequence**: Parallel sparse BM25 and dense ChromaDB search, RRF fusion, Cross-Encoder reranking, and Gemini streaming synthesis.

## Content

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant App as Streamlit UI
    participant Hybrid as HybridSearchEngine
    participant BM25 as BM25Search
    participant Chroma as ChromaDBManager
    participant RRF as Reciprocal Rank Fusion
    participant Cross as CrossEncoderReranker
    participant Gemini as Gemini Client

    User->>App: Submits Natural Language Query
    App->>Hybrid: search(query, top_k)
    par Sparse Keyword Search
        Hybrid->>BM25: search(query)
        BM25-->>Hybrid: Sparse Candidates
    and Dense Vector Search
        Hybrid->>Chroma: query_similar(query)
        Chroma-->>Hybrid: Dense Candidates
    end
    Hybrid->>RRF: reciprocal_rank_fusion(sparse, dense)
    RRF-->>Hybrid: Fused Candidate List
    Hybrid->>Cross: rerank(query, candidates)
    Cross-->>Hybrid: Re-ranked Top Passages
    Hybrid-->>App: Retrieved Context
    App->>Gemini: generate_response(prompt, context)
    Gemini-->>App: Generated Response Stream
    App-->>User: Display Response & Source Cards
```

## Next Reading
- [08 ML Pipeline](../08_ML_PIPELINE.md)
