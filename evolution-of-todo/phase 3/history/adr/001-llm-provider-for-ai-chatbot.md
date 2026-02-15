# ADR-001: LLM Provider for AI Chatbot

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Accepted
- **Date:** 2026-02-11
- **Feature:** 016-ai-chatbot
- **Context:** During Phase 3 implementation, the OpenAI API quota was exhausted (insufficient_quota error). Budget constraint exists - user already purchased Claude Code pro plan and cannot afford additional OpenAI credits. The AI chatbot requires an LLM provider with full tool/function calling support for MCP tool integration (add_task, list_tasks, complete_task, update_task, delete_task).

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security? ✅ YES - affects all AI interactions, cost model, rate limits
     2) Alternatives: Multiple viable options considered with tradeoffs? ✅ YES - OpenAI, Groq, Google Gemini, OpenRouter, Ollama
     3) Scope: Cross-cutting concern (not an isolated detail)? ✅ YES - affects orchestrator, settings, all chat functionality
-->

## Decision

Use **Cerebras API** with **llama-3.3-70b** model as the LLM provider for the AI chatbot.

**Technology Stack:**
- **LLM Provider:** Cerebras (https://api.cerebras.ai/v1)
- **Model:** llama-3.3-70b
- **API Format:** OpenAI-compatible (uses `openai` Python SDK with custom base_url)
- **Tool Calling:** Structured function calling (OpenAI format)
- **Rate Limits:** Free tier - 30 RPM, 1,000,000 tokens/day

**Implementation:**
- 3-setting change in settings.py (cerebras_api_key, cerebras_base_url, cerebras_model)
- Zero changes to MCP tools, schemas, chat endpoint, or frontend
- Settings updated: cerebras_api_key, cerebras_base_url, cerebras_model

### Evolution History

**First Change: OpenAI → Groq (2026-02-11)**
- **Reason:** OpenAI API quota exhausted (insufficient_quota error), budget constraint
- **Provider:** Groq API with llama-3.3-70b-versatile model
- **Rate Limits:** 30 RPM, 14,400 requests/day, 100,000 tokens/day
- **Outcome:** Successfully implemented, but hit daily token limit (100K tokens/day) during testing

**Second Change: Groq → Cerebras (2026-02-11)**
- **Reason:** Groq daily token quota exhausted (100,000 tokens/day limit hit with 429 rate limit error)
- **Provider:** Cerebras API with llama-3.3-70b model
- **Rate Limits:** 30 RPM, 1,000,000 tokens/day (10x more than Groq)
- **Code Impact:** 3-setting change (cerebras_api_key, cerebras_base_url, cerebras_model)
- **Outcome:** Provides 10x more daily tokens for continued development and testing

## Consequences

### Positive

- **Zero cost:** Free tier (30 RPM, 1M tokens/day) sufficient for hackathon scope
- **10x more tokens than Groq:** 1,000,000 tokens/day vs Groq's 100,000 tokens/day - eliminates rate limit bottleneck
- **Minimal migration effort:** OpenAI-compatible API requires only 3-setting change
- **Full tool calling support:** Structured function calling works with MCP tools
- **Fast inference:** Optimized for low latency
- **No credit card required:** Immediate access without payment setup
- **Meets performance goals:** <3 second response time achieved
- **Same model family:** llama-3.3-70b equivalent to Groq's llama-3.3-70b-versatile

### Negative

- **Tool calling stability:** Potential Llama model issues with XML-format tool call generation (mitigated by prompt engineering and parallel_tool_calls=False)
- **Rate limits:** 30 RPM lower than OpenAI paid tiers (acceptable for hackathon, may need upgrade for production)
- **Less mature ecosystem:** Smaller community than OpenAI, fewer examples
- **Model limitations:** llama-3.3-70b less capable than GPT-4o for complex reasoning
- **Prompt engineering required:** System prompt needs explicit tool calling instructions

## Alternatives Considered

**Alternative 1: OpenAI GPT-4o / GPT-3.5-turbo**
- **Why rejected:** API quota exhausted (insufficient_quota error). Budget constraint - user cannot afford additional credits after purchasing Claude Code pro.
- **Tradeoffs:** Best tool calling reliability, most mature, but cost prohibitive for this project.

**Alternative 2: Groq (llama-3.3-70b-versatile)**
- **Why replaced:** Initially chosen as OpenAI replacement. Successfully implemented but daily token quota (100,000 tokens/day) exhausted during testing with 429 rate limit error. Insufficient capacity for continued development.
- **Tradeoffs:** Fast inference (LPU), OpenAI-compatible, but token limits too restrictive for active development.

**Alternative 3: Google Gemini (gemini-1.5-flash / gemini-1.5-pro)**
- **Why not chosen:** Free tier available with good tool calling support, but requires more code changes (different API format, different SDK). Cerebras's OpenAI compatibility made it faster to implement.
- **Tradeoffs:** Comparable free tier, good tool calling, but higher migration effort.

**Alternative 4: OpenRouter**
- **Why not chosen:** Aggregates multiple models with pay-per-use pricing, but tool calling support varies by model. Less predictable behavior and still requires payment.
- **Tradeoffs:** Model flexibility, but inconsistent tool calling and cost uncertainty.

**Alternative 5: Local Ollama**
- **Why rejected:** Requires local hardware (GPU), limited tool calling support, slower inference. Not suitable for stateless cloud deployment.
- **Tradeoffs:** Zero API cost, full control, but infrastructure complexity and performance issues.

## References

- Feature Spec: specs/016-ai-chatbot/spec.md
- Implementation Plan: specs/016-ai-chatbot/plan.md
- Research Documentation: specs/016-ai-chatbot/research.md (R1: LLM Provider Change section)
- Related ADRs: None
- Evaluator Evidence: history/prompts/016-ai-chatbot/004-fix-groq-tool-calling-errors.misc.prompt.md (documents tool calling fixes and validation)
