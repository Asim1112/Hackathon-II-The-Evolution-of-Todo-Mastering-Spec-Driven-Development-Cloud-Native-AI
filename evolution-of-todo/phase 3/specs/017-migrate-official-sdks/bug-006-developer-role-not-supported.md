# BUG-006: Cerebras API Rejects "developer" Role

**Date**: 2026-02-12
**Status**: Root cause identified, fix ready

## Error

```
openai.UnprocessableEntityError: Error code: 422
body.messages.1: Input tag 'developer' found using 'role' does not match any of the expected tags: 'system', 'user', 'assistant', 'tool'
```

## Root Cause

In `chatkit_server.py` line 128, the user context message uses `role: "developer"`:

```python
user_context_message = {
    "role": "developer",  # ❌ Not supported by Cerebras
    "content": (...)
}
```

While the OpenAI Agents SDK's `Message` type accepts `"developer"` role, **Cerebras API** (llama-3.3-70b) only supports:
- `system`
- `user`
- `assistant`
- `tool`

## Fix

Change `"role": "developer"` to `"role": "system"` in line 128.

System messages have high priority in instruction hierarchy (similar to developer messages) and are supported by all OpenAI-compatible APIs.
