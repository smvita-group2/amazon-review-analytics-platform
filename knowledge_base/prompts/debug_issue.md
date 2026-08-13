# AI Prompt: Debug Issue

Use this prompt template when requesting AI assistance to debug a failure:

```markdown
# TASK: Debug Issue

Error Description / Traceback:
<PASTE_ERROR_TRACEBACK>

Affected Pipeline / Component:
<COMPONENT_NAME e.g., Glue bronze_to_silver, ChromaDB manager>

## Debugging Instructions
1. Inspect full un-truncated error log.
2. Locate exact line of failure and trace root cause upstream.
3. Fix root cause without suppressing exceptions or returning dummy data.
4. Run `pytest` to verify fix.
```
