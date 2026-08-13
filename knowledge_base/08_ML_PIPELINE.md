# 08 ML Pipeline

## Hybrid RAG Architecture

Located in `ml_pipeline/`:

```text
Query ──┬──► Semantic Search (ChromaDB + SentenceTransformers) ──┐
        │                                                         ├──► RRF Fusion ──► Cross-Encoder ──► Gemini LLM ──► Response
        └──► Lexical Search (Rank-BM25 Keyword Index) ───────────┘
```

## Module Breakdown

1. **Document Builder (`product_documents/`)**:
   - `document_builder.py`: Formats product metadata & reviews into text documents.
   - `review_selector.py`: Selects top informative positive and negative reviews per product.

2. **Vector Database & Embeddings (`vectordb/` & `embeddings/`)**:
   - `embedding_model.py`: Generates dense embeddings using `all-MiniLM-L6-v2`.
   - `chromadb_manager.py`: Stores vector collections and executes similarity search.

3. **Keyword & Hybrid Retrieval (`retrieval/`)**:
   - `bm25_builder.py` / `bm25_search.py`: Pre-tokenizes corpus and performs BM25 keyword matching.
   - `rrf.py`: Combines dense and sparse ranks via Reciprocal Rank Fusion ($k=60$).
   - `reranker.py`: Re-ranks top candidate documents using `ms-marco-MiniLM-L-6-v2`.

4. **LLM Synthesis (`llm/`)**:
   - `prompt_builder.py`: Constructs grounded prompts containing retrieved context.
   - `gemini_client.py`: Calls Google Gemini API (`gemini-2.5-flash`, `gemini-1.5-flash`, `gemini-3.5-flash`).

5. **Evaluation (`evaluation/`)**:
   - `faithfulness.py`: Measures context hallucination score.
   - `retrieval_relevance.py`: Evaluates retrieval precision and recall.
