# Generated Module Index

Map of Python packages and modules:

## ETL Modules (`src/`)
- `src.common.logger`: Logging configuration.
- `src.common.spark_session`: SparkSession initializer.
- `src.ingestion.reader`: Data ingestion reader functions.
- `src.ingestion.writer`: Data lake writer functions.
- `src.bronze_to_silver.metadata_transformer`: Raw metadata cleaner.
- `src.bronze_to_silver.reviews_transformer`: Raw reviews cleaner.
- `src.silver_to_gold.silver_master_transformer`: Joined master dataset builder.
- `src.silver_to_gold.gold_visualization_transformer`: Dashboard aggregator.
- `src.validation.metadata_validator`: Metadata schema validator.
- `src.validation.reviews_validator`: Reviews schema validator.
- `src.pipelines`: Entry pipelines for Glue execution.

## ML Modules (`ml_pipeline/`)
- `ml_pipeline.common`: Path resolution, S3 utils, I/O wrappers.
- `ml_pipeline.product_documents`: Document builder, review selector.
- `ml_pipeline.embeddings`: Embedding model & generator.
- `ml_pipeline.vectordb`: ChromaDB manager & vector persistence.
- `ml_pipeline.retrieval`: BM25, RRF, Cross-Encoder, Hybrid search.
- `ml_pipeline.llm`: Gemini client & prompt builder.
- `ml_pipeline.evaluation`: RAG metric evaluations.
