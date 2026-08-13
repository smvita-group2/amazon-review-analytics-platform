# AI Prompt: Implement Feature

Use this prompt template when requesting AI assistance to add a new feature to the repository:

```markdown
# TASK: Implement New Feature

Target Feature: <FEATURE_NAME_OR_DESCRIPTION>
Target Component: <MODULE_PATH e.g., src/bronze_to_silver/ or ml_pipeline/retrieval/>

## Context & Requirements
- Read `knowledge_base/01_ARCHITECTURE.md` and `knowledge_base/13_CODING_GUIDELINES.md`.
- Ensure new code conforms to PEP 8, Black line length (88), and Mypy typing rules.
- Maintain existing API contracts and update invocation sites.

## Steps Required
1. Inspect existing interfaces in target module.
2. Implement feature cleanly without breaking existing tests.
3. Write PyTest unit tests covering success and edge cases in `tests/`.
4. Verify with `pytest`.
```
