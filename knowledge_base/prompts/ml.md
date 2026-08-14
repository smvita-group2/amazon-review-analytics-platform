# Task Prompt: Hybrid RAG & Machine Learning Engine

## Context Files to Load
Before beginning work on `ml_pipeline/` modules (Document Builder, ChromaDB, BM25, RRF, Cross-Encoder, Gemini LLM), you MUST load the following knowledge files:
1. `knowledge_base/01_ARCHITECTURE.md`
2. `knowledge_base/03_TECH_STACK.md`
3. `knowledge_base/08_ML_PIPELINE.md`
4. `knowledge_base/11_CONFIGURATION.md`

## Instructions
- Ensure dense embedding generation uses `all-MiniLM-L6-v2`.
- Ensure lexical search uses Rank-BM25 (`BM25Okapi`).
- Merge dense and sparse search ranks via Reciprocal Rank Fusion ($k=60$).
- Apply `ms-marco-MiniLM-L-6-v2` cross-encoder scoring for document passage re-ranking.
- Invoke Gemini LLM using strict context grounding without hallucination.
