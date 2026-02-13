# BUG-004: UserMessageItem Missing Required inference_options Field

**Date**: 2026-02-12
**Status**: Root cause identified

## Error

```
pydantic_core._pydantic_core.ValidationError: 1 validation error for UserMessageItem
inference_options  Field required [type=missing, ...]
```

## Root Cause

ChatKit v1.6.0 `UserMessageItem` (in `chatkit/types.py` line 607) requires:
```python
inference_options: InferenceOptions  # REQUIRED, no default
```

`InferenceOptions` (line 761-766):
```python
class InferenceOptions(BaseModel):
    tool_choice: ToolChoice | None = None
    model: str | None = None
```

Both fields inside `InferenceOptions` are optional, but the field itself on `UserMessageItem` is required.

## Affected Code

In `store_adapter.py`, there are 4 places that create/validate `UserMessageItem`:
1. Line 62-70: Legacy plain-text user message construction (missing `inference_options`)
2. Line 83: `UserMessageItem.model_validate(data)` (stored JSON may lack `inference_options`)
3. Line 89-97: Fallback user message construction (missing `inference_options`)

## Fix

1. Import `InferenceOptions` from `chatkit.types`
2. Add `inference_options=InferenceOptions()` to all 3 direct constructions
3. For `model_validate()`, inject default `inference_options` into data dict if missing
