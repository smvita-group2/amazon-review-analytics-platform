# Generated Class Index

Key classes across core modules:

## ETL & Validation Classes (`src/`)
- `MetadataTransformer`: Product metadata cleaning & cast transformer.
- `ReviewsTransformer`: Customer review normalization transformer.
- `SilverMasterTransformer`: Master join and enrichment transformer.
- `GoldVisualizationTransformer`: BI metrics aggregation transformer.
- `MetadataValidator`: PySpark schema validation for metadata datasets.
- `ReviewsValidator`: Star rating, null handling, and review validator.

## ML & Retrieval Classes (`ml_pipeline/`)
- `EmbeddingGenerator`: Generates dense vector embeddings (`sentence-transformers`).
- `ChromaDBManager`: Persistent vector storage, insertion, and similarity query manager.
- `BM25Builder`: Pre-processes text corpus and builds BM25 lexical index.
- `BM25Search`: Performs sparse keyword query matching over BM25 index.
- `CrossEncoderReranker`: Re-ranks top-N candidate passages using CrossEncoder.
- `HybridSearchEngine`: Orchestrates BM25, ChromaDB, RRF fusion, and CrossEncoder re-ranking.
- `GeminiClient`: Wraps Google Gemini API calls for streaming and response generation.
- `DocumentBuilder`: Formats product metadata and review excerpts into document chunks.
