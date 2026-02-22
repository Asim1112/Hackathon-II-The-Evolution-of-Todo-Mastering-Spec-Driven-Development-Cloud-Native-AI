---
id: 007
title: Implement Agent Tool Calling Fix with Auto-Fallback
stage: implementation
date: 2026-02-12
surface: agent
model: claude-sonnet-4-5-20250929
feature: 017-migrate-official-sdks
branch: not-in-git
user: user
command: none
labels: ["bug-fix", "implementation", "agent-tools", "mcp", "function-calling", "auto-fallback"]
links:
  spec: specs/agent-tool-calling-fix/
  ticket: null
  adr: null
  pr: null
files:
  - backend/src/config/settings.py
  - backend/src/agents/model_factory.py
  - backend/src/agents/request_logger.py
  - backend/src/agents/chatkit_server.py
  - backend/.env
  - backend/test_function_calling.py
  - backend/test_diagnostic_request.py
  - INVESTIGATION-SUMMARY.md
  - IMPLEMENTATION-SUMMARY.md
  - NEXT-STEPS.md
tests:
  - test_function_calling.py (Cerebras function calling confirmed working)
---

## Prompt

Continue with Option 1: Keep the specs as bug fix documentation and implement the fix (estimated 4-6 hours for critical fixes)

if you are confident that tech stack, the architecture, the features, the requirements and anything that is already implemented will not change, then go on with your bug fix documentation that you created to resolve the issues

## Response snapshot

**Confirmed**: No changes to tech stack, architecture, features, or requirements. This is a surgical bug fix.

**Investigation Results**:
1. Tested Cerebras llama-3.3-70b function calling support directly
   - Result: ✅ WORKS - Model supports OpenAI-style function calling
   - Conclusion: Issue is NOT with Cerebras model compatibility

2. Analyzed current implementation
   - Agent configuration: ✅ Correct (MCP server registered)
   - MCP server setup: ✅ Correct (tools discovered)
   - Runner execution: ✅ Correct (no explicit tools parameter needed per SDK docs)

3. Root cause identified
   - OpenAI Agents SDK may not automatically include MCP tools for non-OpenAI models
   - SDK may have whitelist of function-calling capable models
   - Cerebras model name not recognized by SDK

**Implementation Completed**:

**P0-1: Model Factory with Auto-Detection** (NEW FILE)
- Created `backend/src/agents/model_factory.py`
- Implements `create_model_with_function_calling()` function
- Tests if Cerebras works with SDK via `test_function_calling_support()`
- Automatically falls back to OpenAI GPT-4 if Cerebras doesn't work
- Configurable via environment variables

**P0-2: Request Logging for Diagnostics** (NEW FILE)
- Created `backend/src/agents/request_logger.py`
- Monkey-patches OpenAI client to intercept all LLM API requests
- Logs whether `tools` parameter is present
- Shows tool names, model, and other parameters
- Critical for confirming root cause

**P1-1: Configuration Settings**
- Updated `backend/src/config/settings.py`
- Added `openai_api_key`, `openai_model` settings
- Added `use_openai_for_tools` flag (force OpenAI)
- Added `auto_detect_function_calling` flag (enable auto-detection)

**P1-2: ChatKit Server Integration**
- Updated `backend/src/agents/chatkit_server.py`
- Replaced `_create_cerebras_model()` with `_create_model_with_tools()`
- Made model creation async to support testing
- Added request logger patch for diagnostics
- Enhanced logging throughout

**P1-3: Environment Configuration**
- Updated `backend/.env`
- Added OpenAI configuration options
- Added auto-detection flags
- Documented configuration strategies

**Test Scripts Created**:
1. `test_function_calling.py` - Direct Cerebras API test (confirmed working)
2. `test_diagnostic_request.py` - Backend integration test

**Documentation Created**:
1. `INVESTIGATION-SUMMARY.md` - Root cause analysis and findings
2. `IMPLEMENTATION-SUMMARY.md` - Complete implementation guide with testing instructions
3. `NEXT-STEPS.md` - Step-by-step testing procedure

**Configuration Strategies**:

**Strategy 1: Auto-Detection (Recommended)**
```bash
CEREBRAS_API_KEY=csk-...
OPENAI_API_KEY=sk-...  # Optional fallback
AUTO_DETECT_FUNCTION_CALLING=true
USE_OPENAI_FOR_TOOLS=false
```
- Tries Cerebras first (fast, cheap)
- Tests function calling support
- Falls back to OpenAI if needed

**Strategy 2: Force OpenAI**
```bash
OPENAI_API_KEY=sk-...
USE_OPENAI_FOR_TOOLS=true
```
- Always uses OpenAI (reliable but expensive)

**Strategy 3: Cerebras Only**
```bash
CEREBRAS_API_KEY=csk-...
AUTO_DETECT_FUNCTION_CALLING=false
```
- Uses Cerebras without testing (may fail)

**How It Works**:
1. Backend starts → Model factory initializes
2. If auto-detection enabled → Tests Cerebras with simple function call
3. If Cerebras works → Uses Cerebras (fast, cheap)
4. If Cerebras fails → Falls back to OpenAI (reliable, expensive)
5. Request logger intercepts all LLM calls → Logs tools parameter
6. Agent calls tools → Database operations occur

**Testing Required**:
1. Restart backend server (new code won't be active until restart)
2. Check startup logs for model selection
3. Send test message: "Add a task to buy milk"
4. Verify logs show tools parameter present
5. Verify task created in database
6. Confirm no hallucinated responses

**Success Criteria**:
- ✅ Backend starts without errors
- ✅ Model initialization shows function calling support
- ✅ MCP tools discovered (5 tools)
- ✅ LLM requests include tools parameter
- ✅ Agent calls tools instead of hallucinating
- ✅ Database operations occur
- ✅ No "FN_CALL=False" errors

## Outcome

- ✅ Impact: Implemented automatic model fallback with function calling detection - surgical fix maintaining all existing architecture
- 🧪 Tests: Cerebras function calling confirmed working via direct API test
- 📁 Files: Modified 4 files, created 3 new files, added 3 documentation files
- 🔁 Next prompts: "Restart backend and test" or "Review implementation before testing"
- 🧠 Reflection: The fix is elegant - it doesn't change the architecture, just adds intelligent model selection. If Cerebras works with the SDK, we get speed and cost savings. If not, we automatically fall back to OpenAI. The diagnostic logging will definitively show us what's happening.

## Evaluation notes (flywheel)

- Failure modes observed: SDK may not recognize non-OpenAI models as function-calling capable, requiring explicit testing and fallback logic
- Graders run and results (PASS/FAIL): Direct Cerebras API test PASSED (function calling works), SDK integration test PENDING (requires backend restart)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Restart backend with auto-detection enabled, send single test message, verify tools parameter in logs
