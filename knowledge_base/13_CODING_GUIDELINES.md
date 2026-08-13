# 13 Coding Guidelines

## Inferred Engineering Conventions

1. **Code Formatting & Style**:
   - Follow PEP 8 guidelines enforced by **Black** (line length limit = 88) and **Isort**.
   - Use explicit, descriptive variable and function names (`snake_case` for functions/variables, `PascalCase` for classes).

2. **Type Hints & Static Analysis**:
   - Provide type annotations on all public function parameters and return types.
   - Enforce type checks via **Mypy** (`python_version = "3.10"`).

3. **Logging**:
   - Use central logger setup from `src/common/logger.py` or `ml_pipeline/common/logger.py`.
   - Log at appropriate levels (`INFO` for pipeline progress, `WARNING` for schema mismatches, `ERROR` for job failures). Avoid plain `print()` in production modules.

4. **Docstrings & Documentation**:
   - Include standard Sphinx/Google-style docstrings describing function summary, args, and returns.

5. **Error & Schema Handling**:
   - Use explicit validation wrappers (`src/validation/`) rather than swallowing exceptions.
   - Validate PySpark dataframes against schema specs in `config/datasets/schema.py`.
