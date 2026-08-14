# Task Prompt: Testing & Quality Assurance

## Context Files to Load
Before writing or extending PyTest unit or integration tests in `tests/`, you MUST load the following knowledge files:
1. `knowledge_base/11_CONFIGURATION.md`
2. `knowledge_base/12_TESTING.md`
3. `knowledge_base/13_CODING_GUIDELINES.md`
4. `knowledge_base/14_COMMON_COMMANDS.md`

## Instructions
- Re-use shared PyTest fixtures in `tests/conftest.py` (e.g. `spark_session`).
- Write unit tests for all new PySpark transformer functions and validators.
- Ensure test functions start with `test_` and contain explicit assertions.
- Verify code formatting with `black` and type annotations with `mypy` before submitting.
