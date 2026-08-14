# Task Prompt: Backend & PySpark ETL Development

## Context Files to Load
Before beginning work on PySpark data transformations, Glue job entry scripts, or dataset schemas, you MUST load the following knowledge files:
1. `knowledge_base/01_ARCHITECTURE.md`
2. `knowledge_base/04_DATA_PIPELINE.md`
3. `knowledge_base/05_DATASETS.md`
4. `knowledge_base/07_GLUE_PIPELINE.md`
5. `knowledge_base/11_CONFIGURATION.md`

## Instructions
- Ensure PySpark operations use strict schema typing matching `config/datasets/schema.py`.
- Handle null values explicitly using validation wrappers in `src/validation/`.
- Validate rating boundaries within [1.0, 5.0].
- Maintain Medallion Data Lake layer boundaries (Bronze raw ➔ Silver cleaned ➔ Gold curated).
- Use structured loggers from `src/common/logger.py` rather than print statements.
