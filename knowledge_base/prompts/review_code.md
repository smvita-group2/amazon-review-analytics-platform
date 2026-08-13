# AI Prompt: Code Review

Use this prompt template when requesting an AI code review:

```markdown
# TASK: Review Code

Target Files: <FILE_PATHS>

## Review Criteria
1. Architecture & Design: Alignment with Medallion data lake or Hybrid RAG architecture.
2. Quality & Standards: Black line length (88), explicit type hints, Mypy compliance.
3. Performance: Spark shuffle optimization, vector search indexing efficiency.
4. Robustness: Exception handling, logging, schema validation.
5. Verification: Comprehensive PyTest coverage.

Output recommendations grouped by Severity (Critical, Warning, Optimization).
```
