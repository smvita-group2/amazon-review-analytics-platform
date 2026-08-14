# 11 Configuration

## Purpose
Specifies the centralized configuration strategy across PySpark schemas, dataset path mappings, ML model parameters, tool linter configurations, and environment secrets.

## Related Files
- [05 Datasets](05_DATASETS.md)
- [08 ML Pipeline](08_ML_PIPELINE.md)
- [13 Coding Guidelines](13_CODING_GUIDELINES.md)

## Key Concepts
- **Centralized Schema Map**: PySpark `StructType` schema definitions located in `config/datasets/schema.py`.
- **Environment Decoupling**: S3 production paths versus local path overrides for unit testing.
- **YAML ML Settings**: Externalized ML hyperparameters (`settings.yaml`) for retrieval weights, vector database collection names, and model checkpoints.

## Content

### Configuration Files Breakdown

#### 1. `config/datasets/paths.py`
- S3 data path map (`BRONZE_DIR`, `SILVER_DIR`, `GOLD_DIR`, `SCRIPTS_DIR`).
- Local file system path overrides for development and PyTest execution.

#### 2. `config/datasets/schema.py`
- PySpark `StructType` schema declarations for product metadata and customer reviews.

#### 3. `config/datasets/constants.py`
- Category lists (`All_Beauty`, `Electronics`, `Home_and_Kitchen`).
- Standard rating bounds [1.0, 5.0], date formats, and partitioning keys.

#### 4. `ml_pipeline/config/settings.yaml`
- ML pipeline hyperparameters:
  - Dense embedding model (`all-MiniLM-L6-v2`).
  - Vector DB collection name and storage path.
  - RRF fusion parameter ($k=60$).
  - Cross-Encoder model (`ms-marco-MiniLM-L-6-v2`).
  - Default LLM checkpoint (`gemini-2.5-flash`).

#### 5. `pyproject.toml` & `.env`
- Tool specifications (Black line-length 88, Isort, Mypy, PyTest targets).
- Environment secrets (`GEMINI_API_KEY`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION`).

## Next Reading
- [12 Testing](12_TESTING.md)
