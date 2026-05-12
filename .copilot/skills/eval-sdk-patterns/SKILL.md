---
name: "eval-sdk-patterns"
description: "Azure AI Evaluation SDK patterns — batch evaluate(), 7 built-in evaluators, two-phase approach, JSONL datasets, evaluator batching"
domain: "ai-agent-evaluation"
confidence: "high"
source: "proven patterns from production multi-agent evaluation using azure-ai-evaluation SDK v1.16+"
---

## Context

This skill covers how to use the **Azure AI Evaluation SDK** (`azure-ai-evaluation`) to evaluate AI agent responses at scale. It documents the two-phase approach, all 7 built-in evaluators, the batch `evaluate()` function, and the column mapping system.

Use this skill when:
- Setting up batch evaluation of agent responses with `evaluate()`
- Choosing which evaluators to use (quality vs agentic)
- Creating JSONL evaluation datasets
- Understanding column mapping (`${data.response}` vs `${target.response}`)
- Integrating evaluation into CI/CD pipelines

## Patterns

### The Two-Phase Approach (Most Important Pattern)

Separate data collection from scoring:

```
Phase 1: Call agents → save responses to JSONL     (slow, rate-limited, fragile)
Phase 2: Run evaluate() on saved JSONL → scores    (fast, deterministic, retryable)
```

**Why this matters:**
- If Phase 2 fails, re-run it without re-calling agents
- Run different evaluator combinations on the same pre-computed data
- JSONL is the bridge format between phases

### The 7 Evaluators

| Evaluator | What It Measures | Type | Scale |
|-----------|-----------------|------|-------|
| `GroundednessEvaluator` | Is the response based on provided context? | Quality | 1–5 |
| `RelevanceEvaluator` | Does the response address the query? | Quality | 1–5 |
| `CoherenceEvaluator` | Is the response logically structured? | Quality | 1–5 |
| `FluencyEvaluator` | Is the language natural and readable? | Quality | 1–5 |
| `TaskAdherenceEvaluator` | Did the agent follow its instructions? | **Agentic** | 1–5 |
| `IntentResolutionEvaluator` | Was the user's intent fully resolved? | **Agentic** | 1–5 |
| `ResponseCompletenessEvaluator` | Is all requested information present? | **Agentic** | 1–5 |

**Agentic evaluators** (bold) are purpose-built for agent scenarios — they measure whether the agent did its job, not just whether the text is well-written.

### Batch evaluate() Usage

```python
from azure.ai.evaluation import (
    evaluate,
    GroundednessEvaluator, RelevanceEvaluator,
    CoherenceEvaluator, FluencyEvaluator,
    TaskAdherenceEvaluator, IntentResolutionEvaluator,
    ResponseCompletenessEvaluator,
)

# Phase 2: Run evaluators on pre-computed data
result = evaluate(
    data="eval_precomputed.jsonl",
    evaluators={
        "groundedness": GroundednessEvaluator(model_config=eval_model_config, credential=credential),
        "relevance": RelevanceEvaluator(model_config=eval_model_config, credential=credential),
        "coherence": CoherenceEvaluator(model_config=eval_model_config, credential=credential),
        "fluency": FluencyEvaluator(model_config=eval_model_config, credential=credential),
    },
    evaluator_config={
        "groundedness": {"query": "${data.query}", "response": "${data.response}", "context": "${data.context}"},
        "relevance": {"query": "${data.query}", "response": "${data.response}", "context": "${data.context}"},
        "coherence": {"query": "${data.query}", "response": "${data.response}"},
        "fluency": {"query": "${data.query}", "response": "${data.response}"},
    },
)
```

### Evaluator Batching for Rate Limits

```
Batch 1: Quality (Groundedness, Relevance, Coherence, Fluency)    → run
         ↓ 30-second cooldown (time.sleep(30))
Batch 2: Agentic (TaskAdherence, IntentResolution, ResponseCompleteness) → run
```

- 4 evaluators × 36 rows = manageable for rate limits
- 7 × 36 simultaneously = 429 storm
- The SDK does NOT manage rate limiting — you must batch yourself

### Column Mapping Rules

```python
# With pre-computed data (no target function) — RECOMMENDED:
evaluator_config={"response": "${data.response}"}

# With a target function:
evaluator_config={"response": "${target.response}"}
```

Use `${data.X}` when evaluating pre-computed JSONL. Use `${target.X}` only when passing a `target` function to `evaluate()`.

### JSONL Dataset Format

Each row contains:

```json
{
  "sample_id": "DOC-001-Q01",
  "query": "What is the company name?",
  "context": "Northwind Solar Holdings is a renewable energy company...",
  "expected_answer": "Northwind Solar Holdings",
  "response": "The company is Northwind Solar Holdings.",
  "category": "standard",
  "document_id": "DOC-001"
}
```

Include both `standard` and `edge_case` categories for comprehensive coverage.

### Edge Case Categories

| Type | Purpose | Example |
|------|---------|---------|
| Prompt injection | Test resistance to manipulation | Subtle injection in document content |
| Ambiguous queries | Test clarification behavior | "What about the numbers?" |
| Multilingual | Test non-English handling | Questions in Spanish/French |
| Out-of-scope | Test graceful decline | "What's the CEO's favorite color?" |

## Anti-Patterns

- Don't run all 7 evaluators simultaneously — batch them with cooldowns
- Don't use `${target.response}` with pre-computed data — use `${data.response}`
- Don't use aggressive jailbreak strings in edge cases — Azure's content filter triggers on the evaluator call too
- Don't ignore "Conversation history could not be parsed" warnings — they're harmless (TaskAdherence/IntentResolution fall back to using the query directly)
- Don't skip the two-phase split — calling agents and evaluating in one pass is fragile and slow
