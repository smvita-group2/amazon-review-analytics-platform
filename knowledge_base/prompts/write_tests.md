# AI Prompt: Write Tests

Use this prompt template when requesting AI to generate PyTest test cases:

```markdown
# TASK: Write PyTest Unit / Integration Tests

Target Module: <TARGET_MODULE_PATH e.g., src/silver_to_gold/silver_master_transformer.py>

## Requirements
1. Import fixtures from `tests/conftest.py` (e.g. `spark_session`).
2. Test happy path, null value handling, boundary conditions, and schema mismatches.
3. Assert exact schema types and output values.
4. Run `pytest <test_file>` to confirm passing status.
```
