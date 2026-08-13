# AI Prompt: Refactor Module

Use this prompt template when requesting AI assistance to refactor code:

```markdown
# TASK: Refactor Module

Target Module: <MODULE_PATH>
Objective: <REFACTORING_GOAL e.g., Extract transformer logic, decouple vector store>

## Refactoring Constraints
1. Maintain existing function signatures and backwards compatibility.
2. Improve code readability, modularity, and type safety.
3. Preserve comments and docstrings.
4. Run full test suite `pytest` before and after refactoring.
```
