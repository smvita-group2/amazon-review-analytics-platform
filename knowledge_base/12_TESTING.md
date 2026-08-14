# 12 Testing

## Purpose
Outlines the PyTest test framework, test suite architecture, local PySpark session fixtures, schema validation rules, ML unit tests, and pipeline integration tests.

## Related Files
- [11 Configuration](11_CONFIGURATION.md)
- [13 Coding Guidelines](13_CODING_GUIDELINES.md)
- [14 Common Commands](14_COMMON_COMMANDS.md)

## Key Concepts
- **Isolated PySpark Fixture**: Automated setup and teardown of lightweight local PySpark sessions in `conftest.py`.
- **Validation Unit Testing**: Verification of rating boundary limits, missing field handling, and null cleaning logic.
- **ML Component Testing**: Verifying dense/sparse indexing, RRF score calculations, and Cross-Encoder outputs.

## Content

### Test Suite Breakdown (`tests/`)

#### 1. `tests/conftest.py`
- Shared PyTest fixtures: `spark_session` (memory-capped local PySpark context) and synthetic review/metadata DataFrames.

#### 2. `tests/test_smoke.py`
- Environment verification: confirms module imports, PySpark initialization, and configuration loading.

#### 3. `tests/test_validation.py`
- Unit tests for schema validation rules, boundary checking (rating range [1.0, 5.0]), and missing value sanitization in `src/validation/`.

#### 4. `tests/test_transformers.py`
- Unit tests for PySpark data transformations in `src/bronze_to_silver/` and `src/silver_to_gold/`.

#### 5. `tests/test_pipelines.py`
- End-to-end integration tests executing PySpark workflows against mock data paths.

#### 6. `tests/test_ml_pipeline.py`
- Unit tests for ML modules (Document Builder, BM25 indexing, ChromaDB vector manager, RRF calculation, Cross-Encoder reranking).

## Next Reading
- [13 Coding Guidelines](13_CODING_GUIDELINES.md)
