# Generated Classes Index

## Purpose
Index of core Python class abstractions across ETL transformations, data validation, ML retrieval, and LLM synthesis.

## Related Files
- [02 Repository Structure](../02_REPOSITORY_STRUCTURE.md)
- [Module Index](module_index.md)
- [Functions Index](functions.md)

## Key Concepts
- **Core Abstractions**: Class hierarchy separating data transformation engines from vector managers and LLM clients.

## Content

### ETL & Validation Classes (`src/`)
- `MetadataTransformer`: Product metadata cleaning & schema casting transformer.
- `ReviewsTransformer`: Customer review normalization transformer.
- `SilverMasterTransformer`: Master join and enrichment transformer.
- `GoldVisualizationTransformer`: BI metrics aggregation transformer.
- `MetadataValidator`: PySpark schema validation for metadata datasets.
- `ReviewsValidator`: Star rating limits, null handling, and review validator.

### ML & Retrieval Classes (`ml_pipeline/`)
- `EmbeddingGenerator`: Dense vector embedding generator (`sentence-transformers`).
- `ChromaDBManager`: Persistent vector storage, insertion, and similarity query manager.
- `BM25Builder`: Corpus pre-processing and BM25 lexical index builder.
- `BM25Search`: Sparse keyword query matching engine over BM25 index.
- `CrossEncoderReranker`: Passage re-ranker using CrossEncoder model.
- `HybridSearchEngine`: Orchestrator combining BM25, ChromaDB, RRF fusion, and CrossEncoder.
- `GeminiClient`: Wrapper for Google Gemini API invocation and streaming response generation.
- `DocumentBuilder`: Formats product metadata and review excerpts into document chunks.

## Next Reading
- [02 Repository Structure](../02_REPOSITORY_STRUCTURE.md)
