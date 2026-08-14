# Generated Functions Index

## Purpose
Index of core standalone functions across ETL ingestion, data cleaning, validation, RRF fusion, document building, and RAG evaluation.

## Related Files
- [02 Repository Structure](../02_REPOSITORY_STRUCTURE.md)
- [Module Index](module_index.md)
- [Classes Index](classes.md)

## Key Concepts
- **Functional Utility Catalog**: Core helper functions across Spark operations, validation rules, RRF algorithms, and evaluation metrics.

## Content

### `src/` ETL Functions
- `get_spark_session()` (`src/common/spark_session.py`): Configures and returns PySpark Session.
- `setup_logger()` (`src/common/logger.py`): Standardizes console logging formatter.
- `read_json_data()` (`src/ingestion/reader.py`): Ingests raw JSON/GZ dataset into Spark DataFrame.
- `write_parquet_data()` (`src/ingestion/writer.py`): Writes cleaned Spark DataFrame to S3 Parquet.
- `clean_metadata()` (`src/bronze_to_silver/metadata_transformer.py`): Sanitizes product fields.
- `clean_reviews()` (`src/bronze_to_silver/reviews_transformer.py`): Cleans review rating & timestamps.
- `validate_metadata_schema()` (`src/validation/metadata_validator.py`): Validates metadata columns.
- `validate_reviews_schema()` (`src/validation/reviews_validator.py`): Enforces review schema integrity.
- `join_reviews_and_metadata()` (`src/silver_to_gold/silver_master_transformer.py`): Joins reviews & metadata.

### `ml_pipeline/` Functions
- `reciprocal_rank_fusion()` (`ml_pipeline/retrieval/rrf.py`): Merges dense & sparse rank lists ($k=60$).
- `build_product_documents()` (`ml_pipeline/product_documents/document_builder.py`): Constructs RAG text documents.
- `generate_prompt()` (`ml_pipeline/llm/prompt_builder.py`): Formats prompt with context.
- `evaluate_faithfulness()` (`ml_pipeline/evaluation/faithfulness.py`): Calculates faithfulness metrics.

## Next Reading
- [02 Repository Structure](../02_REPOSITORY_STRUCTURE.md)
