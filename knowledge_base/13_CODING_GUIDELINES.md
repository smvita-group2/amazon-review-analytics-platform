# 13 Coding Guidelines

## Purpose
Defines engineering conventions, code formatting rules, static type annotations, logging standards, docstring conventions, and error handling policies across the platform.

## Related Files
- [11 Configuration](11_CONFIGURATION.md)
- [12 Testing](12_TESTING.md)
- [14 Common Commands](14_COMMON_COMMANDS.md)

## Key Concepts
- **Strict PEP 8**: Formatting enforced by Black (line length 88) and Isort.
- **Type Annotations**: Mandatory type hints on all public functions verified by Mypy.
- **Central Logging**: Structured logging via `src/common/logger.py` avoiding raw `print()` statements.

## Content

### Technical Conventions

#### 1. Code Style & Formatting
- Enforce PEP 8 using **Black** (`line-length = 88`) and **Isort** (`profile = "black"`).
- Use `snake_case` for variables/functions and `PascalCase` for classes and PySpark custom types.

#### 2. Type Hinting & Static Verification
- Annotate arguments and return values on all public methods (`def transform_reviews(df: DataFrame) -> DataFrame:`).
- Run **Mypy** verification targetting Python 3.10+.

#### 3. Structured Logging
- Instantiate module loggers via `src/common/logger.py`.
- Log at appropriate severity (`INFO` for step progress, `WARNING` for non-fatal mismatches, `ERROR` for job aborts). Avoid standard `print()`.

#### 4. Docstring Standards
- Use Google-style docstrings describing function summary, parameter definitions, and return types.

#### 5. Exception & Schema Handling
- Wrap PySpark data operations in explicit validator functions (`src/validation/`).
- Enforce DataFrame schemas against definitions in `config/datasets/schema.py`.

## Next Reading
- [14 Common Commands](14_COMMON_COMMANDS.md)
