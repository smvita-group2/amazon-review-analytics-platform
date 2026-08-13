# 12 Testing

## Testing Strategy

The test suite in `tests/` uses PyTest and local PySpark sessions to validate data transformations, schema validation rules, ML components, and pipeline end-to-end flows.

## Test Files Breakdown

- **`tests/conftest.py`**:
  - Provides shared PyTest fixtures, including `spark_session` (local PySpark context configured with memory limits) and sample mock review/metadata dataframes.

- **`tests/test_smoke.py`**:
  - Smoke tests verifying environment imports, PySpark initialization, and configuration file accessibility.

- **`tests/test_validation.py`**:
  - Validates schema validation rules, type checking, boundary enforcement (e.g. rating [1, 5]), and missing field handling in `src/validation/`.

- **`tests/test_transformers.py`**:
  - Unit tests for PySpark data transformations in `src/bronze_to_silver/` and `src/silver_to_gold/`.

- **`tests/test_pipelines.py`**:
  - End-to-end integration tests running PySpark pipelines against mock S3/local data paths.

- **`tests/test_ml_pipeline.py`**:
  - Tests ML components (Document Builder, BM25 indexing, ChromaDB vector manager, RRF score calculation, Cross-Encoder reranking).
