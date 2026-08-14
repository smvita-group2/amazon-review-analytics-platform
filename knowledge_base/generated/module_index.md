# Generated Module Index

## Purpose
Provides an index mapping Python packages and submodules across `src/` and `ml_pipeline/`.

## Related Files
- [02 Repository Structure](../02_REPOSITORY_STRUCTURE.md)
- [Classes Index](classes.md)
- [Functions Index](functions.md)
- [Dependencies Index](dependencies.md)

## Key Concepts
- **Module Indexing**: Rapid code navigation matrix mapping Python import paths to functional responsibilities.

## Content

### ETL Modules (`src/`)
- `src.common.logger`: Centralized logger configuration.
- `src.common.spark_session`: PySpark SparkSession factory.
- `src.ingestion.reader`: Data ingestion reader functions.
- `src.ingestion.writer`: Data lake Parquet writer functions.
- `src.bronze_to_silver.metadata_transformer`: Raw product metadata cleaning functions.
- `src.bronze_to_silver.reviews_transformer`: Raw customer review cleaning functions.
- `src.silver_to_gold.silver_master_transformer`: Silver master joined dataset builder.
- `src.silver_to_gold.gold_visualization_transformer`: Gold dashboard aggregation metrics.
- `src.validation.metadata_validator`: Metadata schema validator routines.
- `src.validation.reviews_validator`: Reviews schema validator routines.

### ML Modules (`ml_pipeline/`)
- `ml_pipeline.common`: Path resolution, S3 utilities, I/O wrappers.
- `ml_pipeline.product_documents`: Document chunk builder, review selector.
- `ml_pipeline.embeddings`: Embedding model generator (`all-MiniLM-L6-v2`).
- `ml_pipeline.vectordb`: ChromaDB manager & vector database persistence.
- `ml_pipeline.retrieval`: Rank-BM25, RRF fusion, Cross-Encoder, Hybrid search.
- `ml_pipeline.llm`: Gemini client & prompt builder.
- `ml_pipeline.evaluation`: RAG evaluation metrics (faithfulness, relevance).

## Next Reading
- [02 Repository Structure](../02_REPOSITORY_STRUCTURE.md)
