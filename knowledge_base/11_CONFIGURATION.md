# 11 Configuration

## Configuration Management Strategy

The repository follows a centralized configuration pattern split across dataset definitions, ML settings, tool configs, and environment secrets.

## Key Configuration Files

1. **`config/datasets/paths.py`**:
   - Central S3 path map for `BRONZE_DIR`, `SILVER_DIR`, `GOLD_DIR`, `SCRIPTS_DIR`.
   - Local directory path overrides for dev testing.

2. **`config/datasets/schema.py`**:
   - PySpark `StructType` schema declarations for product metadata and reviews.

3. **`config/datasets/constants.py`**:
   - Supported category lists (e.g., `All_Beauty`, `Electronics`).
   - Default rating bounds, date formats, and partitioning constants.

4. **`ml_pipeline/config/settings.yaml`**:
   - ML model parameters:
     - Embedding model name (`all-MiniLM-L6-v2`).
     - Vector DB path & collection name.
     - RRF parameter $k=60$.
     - Cross-encoder reranker model name (`ms-marco-MiniLM-L-6-v2`).
     - Default LLM model (`gemini-2.5-flash`).

5. **`pyproject.toml`**:
   - Python linting & formatting specs (Black line-length 88, Isort profile black, Mypy settings, PyTest target directory).

6. **Environment Secrets (`.env`)**:
   - `GEMINI_API_KEY`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION`.
