# 08 ML Pipeline

## Purpose
Details the Machine Learning and Hybrid RAG architecture located in `ml_pipeline/`, covering document building, dense vector indexing, sparse BM25 indexing, Reciprocal Rank Fusion, Cross-Encoder reranking, and Gemini LLM integration.

## Related Files
- [01 Architecture](01_ARCHITECTURE.md)
- [03 Tech Stack](03_TECH_STACK.md)
- [09 Streamlit Overview](09_STREAMLIT_OVERVIEW.md)
- [Execution Flow Diagram](diagrams/execution_flow.md)

## Key Concepts
- **Hybrid Search**: Combining dense vector semantic search (SentenceTransformers + ChromaDB) with sparse keyword retrieval (Rank-BM25).
- **Reciprocal Rank Fusion (RRF)**: Merging rank positions from dense and sparse retrieval algorithms ($k=60$).
- **Cross-Encoder Reranking**: Re-evaluating top candidate document passages with `ms-marco-MiniLM-L-6-v2`.
- **LLM Grounding**: Prompting Google Gemini LLM using strictly retrieved product review context.

## Content

### Hybrid RAG Flow Architecture
```text
Query ──┬──► Semantic Search (ChromaDB + SentenceTransformers) ──┐
        │                                                         ├──► RRF Fusion ──► Cross-Encoder ──► Gemini LLM ──► Response
        └──► Lexical Search (Rank-BM25 Keyword Index) ───────────┘
```

### Module Breakdown (`ml_pipeline/`)

#### 1. Document Builder (`product_documents/`)
- `document_builder.py`: Constructs cohesive text documents from product metadata and reviews.
- `review_selector.py`: Selects top positive and negative reviews per product family.

#### 2. Vector DB & Embeddings (`vectordb/` & `embeddings/`)
- `embedding_model.py`: Generates dense embeddings via `all-MiniLM-L6-v2`.
- `chromadb_manager.py`: Manages local ChromaDB vector store collections and similarity queries.

#### 3. Hybrid Retrieval & Reranking (`retrieval/`)
- `bm25_builder.py` / `bm25_search.py`: Builds and queries BM25Okapi lexical index.
- `rrf.py`: Implements Reciprocal Rank Fusion score aggregation.
- `reranker.py`: Applies `ms-marco-MiniLM-L-6-v2` cross-encoder scoring.

#### 4. LLM Synthesis (`llm/`) & Evaluation (`evaluation/`)
- `prompt_builder.py` & `gemini_client.py`: Constructs prompts and invokes Gemini API (`gemini-2.5-flash`).
- `faithfulness.py` & `retrieval_relevance.py`: Evaluates retrieval recall and LLM faithfulness scores.

## Next Reading
- [09 Streamlit Overview](09_STREAMLIT_OVERVIEW.md)
