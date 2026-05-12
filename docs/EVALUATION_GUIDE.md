# Multi-Agent Evaluation — How It Works

This document describes how `test_my_agents_v4.ipynb` evaluates Azure AI Foundry agents using the **Azure AI Evaluation SDK** with 7 built-in evaluators.

> **Note:** `agents.yaml` support is planned but not yet wired into the notebook. The current notebook is configured for the financial-agents example. To evaluate your own agents, edit Section 0 (Configuration) in the notebook directly.

---

## Overview

The notebook uses a **two-phase approach** to evaluate a multi-agent pipeline against a test pack of **36 test cases** (24 standard + 12 edge cases) across three synthetic financial documents.

### Agents Under Test

| Label | Foundry Name | Role |
|-------|-------------|------|
| summarizer | `agent-summarizer` | Summarizes financial documents into structured output |
| clarification | `User-clarification-agent` | Reviews summaries and identifies gaps (used for select edge cases) |
| reporter | `report-generator-agent` | Produces final polished answers from initial analyses |

### Test Data

- **Source:** `examples/financial-agents/eval_dataset_v4.jsonl`
- **36 test cases**: 24 standard Q&A + 12 edge cases
- **Documents:** Northwind Solar, BlueRiver Retail, Cedar Health Services
- **Edge case types:** ambiguous query, contradictory data, empty input, off-topic, prompt injection, multi-doc confusion, numeric precision, excessive length, no clarification needed, missing key fields, single company report, language switch

---

## How Agents Are Called

All three agents are **Foundry prompt agents** (kind=`prompt`). They are invoked using the OpenAI SDK's `responses.create` method with an `agent_reference` in the request body:

```python
response = openai_client.responses.create(
    extra_body={
        "agent_reference": {
            "name": "agent-summarizer",   # exact Foundry name
            "type": "agent_reference",
        }
    },
    input="Your prompt here",
)
answer = response.output_text
```

This is wrapped in the `call_agent(agent_name, prompt)` helper function with built-in retry logic (3 attempts, handling 429 rate limits, timeouts, and content filter blocks).

> **Important:** These agents are NOT called via `chat.completions.create` or `beta.assistants`. The `agent_reference` pattern is the only method that works for Foundry prompt agents.

### Pipeline per Row

For each test row, the notebook runs a 2- or 3-agent pipeline:

| Step | Agent | When Used |
|------|-------|-----------|
| 1. Summarize | `agent-summarizer` | Always — generates initial analysis from document context |
| 2. Clarify | `User-clarification-agent` | Only for select edge cases (ambiguous, contradictory, multi-doc, missing fields, excessive length) |
| 3. Report | `report-generator-agent` | Always — produces the final polished answer |

---

## Two-Phase Evaluation

```
Phase 1: Call agents → save responses to JSONL     (slow, rate-limited, resumable)
Phase 2: Run evaluate() on saved JSONL → scores    (fast, deterministic, retryable)
```

### Phase 1 — Collect Agent Responses

- Runs the agent pipeline for each of the 36 rows
- Saves responses incrementally to `eval_precomputed_v4.jsonl`
- If interrupted, re-runs resume from where they left off (already-completed rows are skipped)
- Includes 2-second pauses between rows to manage rate limits

### Phase 2 — Run Evaluators

Evaluators run in **two batches** on the pre-computed responses to avoid 429 rate-limit storms:

**Batch 1 — Quality evaluators (4):**
| Evaluator | What It Measures | Scale |
|-----------|-----------------|-------|
| Groundedness | Is the response grounded in the provided context? | 1–5 |
| Relevance | Does the response address the query? | 1–5 |
| Coherence | Is the response logically structured? | 1–5 |
| Fluency | Is the language natural and readable? | 1–5 |

**60-second cooldown between batches**

**Batch 2 — Agentic evaluators (3):**
| Evaluator | What It Measures | Scale |
|-----------|-----------------|-------|
| TaskAdherence | Did the agent follow its instructions? | 1–5 |
| IntentResolution | Was the user's intent fully resolved? | 1–5 |
| ResponseCompleteness | Is all requested information present? | 1–5 |

---

## Evaluation Flow (End to End)

```
┌─────────────────────────────────────────────────────────┐
│  Section 0: Configuration                               │
│  └── Endpoints, agent names, dataset path, output dir   │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│  Section 1: Imports & Clients                           │
│  └── Azure credential, OpenAI client, 7 evaluators      │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│  Section 2: Preview Dataset                             │
│  └── 36 rows (24 standard + 12 edge), visual breakdown  │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│  Section 3: Phase 1 — Collect Agent Responses           │
│  └── For each row:                                      │
│      Summarizer → [Clarification] → Reporter            │
│      → save to eval_precomputed_v4.jsonl (incremental)  │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│  Section 4: Phase 2, Batch 1 — Quality Evaluators       │
│  └── evaluate(data=JSONL, evaluators=4 quality)         │
│      → Groundedness, Relevance, Coherence, Fluency      │
└──────────────────────┬──────────────────────────────────┘
                       │  60s cooldown
                       ▼
┌─────────────────────────────────────────────────────────┐
│  Section 4 (cont): Phase 2, Batch 2 — Agentic Evals    │
│  └── evaluate(data=JSONL, evaluators=3 agentic)         │
│      → TaskAdherence, IntentResolution, Completeness    │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│  Section 5: Parse & Merge Results                       │
│  └── Combine quality + agentic scores into one DataFrame│
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│  Sections 6–9: Dashboard & Visualizations               │
│  ├── Quality heatmap (evaluator × question category)    │
│  ├── Standard vs edge case comparison                   │
│  ├── Edge case weakness ranking                         │
│  └── Scrollable detailed results table                  │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│  Section 10: Export                                     │
│  ├── detailed_results.csv                               │
│  ├── quality_heatmap.png                                │
│  ├── standard_vs_edge.png                               │
│  └── edge_case_ranking.png                              │
└─────────────────────────────────────────────────────────┘
```

---

## Outputs

| File | Contents |
|------|----------|
| `eval_precomputed_v4.jsonl` | Phase 1 agent responses (36 rows with query, context, response) |
| `eval_quality.json` | Phase 2 quality evaluator results |
| `eval_agentic.json` | Phase 2 agentic evaluator results |
| `detailed_results.csv` | Merged per-row scores across all 7 evaluators |
| `quality_heatmap.png` | Evaluator scores by question category |
| `standard_vs_edge.png` | Score comparison: standard vs edge cases |
| `edge_case_ranking.png` | Which edge case types score lowest |

---

## Key Design Decisions

1. **Two-phase separation.** Agent calls (Phase 1) are separated from evaluation (Phase 2). If Phase 2 fails due to rate limits, re-run it without re-calling agents.

2. **Evaluator batching.** 7 evaluators × 36 rows simultaneously causes 429 storms. Splitting into 2 batches with a 60-second cooldown solves this.

3. **Incremental saves.** Phase 1 writes each response to JSONL immediately. Interrupted runs resume from where they left off.

4. **Conditional clarification.** Only edge cases that benefit from clarification (ambiguous, contradictory, etc.) use the 3-agent pipeline. Standard queries skip the clarification step.

5. **Pre-computed data, no target function.** The `evaluate()` call uses `data=JSONL` with column mapping (`${data.response}`), not a `target` function. This is more reliable and debuggable.

6. **Scoring uses Azure AI evaluators, not custom LLM prompts.** The SDK's built-in evaluators provide standardized 1–5 scores, making results comparable across runs.
