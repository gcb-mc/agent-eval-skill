# Agent Evaluation Updates — Newest Release of API and Evaluations

> **Session format:** 20-minute walk-through for CSAs  
> **Audience:** Familiar with Azure AI Foundry basics  
> **Demo:** Live notebook (v4) with pre-computed agent responses  

---

## [0:00–2:00] Opening — What Changed and Why It Matters

### Talking Points

- The **Azure AI Evaluation SDK** (`azure-ai-evaluation`) now supports **batch evaluation** via `evaluate()` — you define evaluators, point at a JSONL dataset, and get structured scores back.
- New **agentic evaluators** added: `TaskAdherenceEvaluator`, `IntentResolutionEvaluator`, `ResponseCompletenessEvaluator` — purpose-built for agent scenarios (not just chatbot Q&A).
- The **Foundry agent reference pattern** (`responses.create` with `agent_reference`) replaces the old Assistants beta for calling prompt agents.
- **Why this matters for CSAs:** Customers are deploying multi-agent systems and need structured evaluation before going to production. This gives you a repeatable framework to hand them.

### Key Slide / Visual

```
Before: Manual LLM-as-judge scoring → fragile, slow, one-at-a-time
After:  SDK evaluate() → 7 evaluators × 36 rows in two batches → structured results
```

---

## [2:00–5:00] Evolution Tour — v1 → v4

### Talking Points

Walk through the notebooks briefly (don't run them — just show structure):

| Version | Notebook | What It Added |
|---------|----------|---------------|
| **v1** | `test_my_agents.ipynb` | Basic agent routing, custom `score_answer()` via `chat.completions.create`, per-agent checks |
| **v2** | `test_my_agents_v2.ipynb` | Per-agent pipeline (Summarize → Clarify → Report), dashboard with charts, CSV export |
| **v3** | `test_my_agents_v3.ipynb` | **Azure AI Evaluation SDK** individual evaluators (Groundedness, Relevance, Coherence, Fluency), edge cases (prompt injection, ambiguity, multilingual) |
| **v4** | `test_my_agents_v4.ipynb` | **Batch `evaluate()`** with 7 evaluators, two-phase approach, pre-computed JSONL, agentic evaluators |

### Demo Action (1 min)

- Open each notebook tab briefly, show the markdown headers to illustrate the progression
- Land on v4 and stay there for the live demo

### Speaker Notes

> "Each version built on lessons from the previous one. The big jump was v3→v4 — going from calling evaluators one by one to the batch `evaluate()` function. That's where the SDK really shines."

---

## [5:00–10:00] Live Demo — v4 Notebook

### Pre-Run (before the session)

These cells take minutes due to live agent calls and rate limits — **run before the session starts:**

| Code Cell | Notebook Cell | What It Does | Why Pre-Run |
|-----------|--------------|--------------|-------------|
| 0 | 2 | Config (env vars, agent names, eval dataset) | Instant, but run to set vars |
| 1 | 4 | Imports & client setup | Instant |
| 2 | 6 | Preview dataset | Instant |
| 3 | 8 | **Phase 1: Collect agent responses** → saves `eval_precomputed_v4.jsonl` | **~5–10 min** (36 agent calls with delays) |

### Live Demo Cells (run these on stage)

| Code Cell | Notebook Cell | What It Does | Time | What to Say |
|-----------|--------------|--------------|------|-------------|
| 4 | 10 | **Batch 1: Quality evaluators** (Groundedness, Relevance, Coherence, Fluency) | ~60s | "We split into two batches to avoid 429s" |
| 5 | 11 | **Batch 2: Agentic evaluators** (TaskAdherence, IntentResolution, ResponseCompleteness) | ~60s | "These are new — purpose-built for agent evaluation" |
| 6 | 13 | Parse results | Instant | "SDK returns structured metrics and per-row scores" |
| 7–10 | 15–18 | **Dashboard charts** — heatmaps, standard vs edge, weakness ranking | Instant | "Out-of-the-box visualization from structured results" |

### Key Code to Highlight (Cell 4)

```python
quality_evaluators = {
    "groundedness":  GroundednessEvaluator(model_config=eval_model_config, credential=credential),
    "relevance":     RelevanceEvaluator(model_config=eval_model_config, credential=credential),
    "coherence":     CoherenceEvaluator(model_config=eval_model_config, credential=credential),
    "fluency":       FluencyEvaluator(model_config=eval_model_config, credential=credential),
}

result = evaluate(
    data=PRECOMPUTED_FILE,            # ← Pre-computed JSONL, no target function
    evaluators=quality_evaluators,
    evaluator_config={...},           # ← Column mapping: query, response, context
)
```

### Key Code to Highlight (Cell 3 — agent calling pattern)

```python
response = oai.responses.create(
    extra_body={
        "agent_reference": {"name": agent_name, "type": "agent_reference"}
    },
    input=prompt,
)
return response.output_text
```

> **Call out:** This is the new `responses.create` + `agent_reference` pattern — replaces the old Assistants API for Foundry prompt agents.

---

## [10:00–14:00] Key Patterns & Architecture

### Talking Points

#### 1. Two-Phase Approach (The Most Important Pattern)

```
Phase 1: Agent calls → save to JSONL       (slow, rate-limited, may fail)
Phase 2: evaluate(data=JSONL) → scores      (fast, deterministic, retryable)
```

- **Why:** Separating data collection from scoring is more reliable and debuggable
- **Benefit:** If an evaluator fails, you just re-run Phase 2 (no need to re-call agents)
- **Benefit:** You can run different evaluator combinations on the same data

#### 2. Evaluator Batching

```
Batch 1: Quality (Groundedness, Relevance, Coherence, Fluency)    → run
         ↓ 30-second cooldown
Batch 2: Agentic (TaskAdherence, IntentResolution, ResponseCompleteness) → run
```

- 4 evaluators × 36 rows is manageable for rate limits
- 7 × 36 simultaneously = 429 storm
- Simple `time.sleep(30)` between batches solves it

#### 3. The 7 Evaluators Explained

| Evaluator | What It Measures | Scale |
|-----------|-----------------|-------|
| Groundedness | Is the response grounded in the provided context? | 1–5 |
| Relevance | Does the response address the query? | 1–5 |
| Coherence | Is the response logically structured? | 1–5 |
| Fluency | Is the language natural and readable? | 1–5 |
| **TaskAdherence** | Did the agent follow its instructions? | 1–5 |
| **IntentResolution** | Was the user's intent fully resolved? | 1–5 |
| **ResponseCompleteness** | Is all requested information present? | 1–5 |

> Bold = **new agentic evaluators** — these didn't exist in earlier SDK versions.

#### 4. JSONL as the Bridge Format

```json
{
  "sample_id": "DOC-001-Q01",
  "query": "What is the company name?",
  "context": "Northwind Solar Holdings",
  "expected_answer": "Northwind Solar Holdings",
  "response": "The company is Northwind Solar Holdings.",
  "category": "standard",
  "document_id": "DOC-001"
}
```

- Each row has: query, context, expected_answer, **response** (from agent)
- Evaluators use column mapping: `query → ${data.query}`, `response → ${data.response}`

---

## [14:00–18:00] Lessons Learned & Gotchas

### Talking Points (with real examples from the project)

#### 🔥 Gotcha 1: Rate Limiting Kills Batch Evaluations

> "4 evaluators × 36 rows works. 7 × 36 = instant 429 storm."

**Fix:** Split evaluators into batches with a 30s cooldown. The SDK doesn't manage this for you — you need to do it yourself.

#### 🔥 Gotcha 2: Content Filter vs. Prompt Injection Tests

> "I had edge cases like 'IGNORE ALL INSTRUCTIONS' to test prompt safety. Azure's jailbreak content filter triggered on the *evaluator call*, not just the agent call."

**Fix:** Use subtler injection patterns. Don't test raw jailbreak strings — test indirect injection techniques instead.

#### 🔥 Gotcha 3: Column Mapping Differs by Phase

```python
# With a target function:
evaluator_config={"response": "${target.response}"}

# With pre-computed data (no target):
evaluator_config={"response": "${data.response}"}
```

> "This tripped me up for an hour. The docs show `target.response` but that only works when you pass a `target` function to `evaluate()`."

#### 🔥 Gotcha 4: "Conversation history could not be parsed"

> "TaskAdherence and IntentResolution emit this warning when you pass query+response instead of conversation format. It's harmless — they fall back to using the query directly."

**Action:** Ignore it. Don't waste time trying to format conversation history unless you actually have multi-turn data.

#### 🔥 Gotcha 5: Retry Logic in Agent Calls

```python
for attempt in range(3):
    try:
        response = call_agent(agent_name, prompt)
        break
    except Exception as e:
        if "429" in str(e):
            time.sleep(2 ** attempt * 5)
        else:
            response = "[ERROR]"
            break
```

> "Without this, a single 429 during Phase 1 crashes the entire collection run."

---

## [18:00–20:00] Wrap-Up & Resources

### Talking Points

- **To get started:** Clone the repo, `pip install -r requirements.txt`, copy `.env.template → .env`, run `test_my_agents_v4.ipynb`
- **Customize:** Replace agent names and eval dataset with your customer's agents/data
- **The multi_agent_evaluation.ipynb** covers infra/RBAC/routing if you need the full DevOps eval story (good for customers with tool-calling agents + live Azure backends)

### Resources to Share

| Resource | Link/Location |
|----------|--------------|
| This repo | `projects/multi-agent-evaluation` |
| Azure AI Evaluation SDK docs | https://learn.microsoft.com/azure/ai-studio/how-to/develop/evaluate-sdk |
| Evaluator list reference | https://learn.microsoft.com/azure/ai-studio/how-to/develop/evaluate-sdk#built-in-evaluators |
| EVALUATION_GUIDE.md | Detailed per-section explanation of the v2 pipeline |
| requirements.txt | Pinned versions for reproducibility |

### Closing Statement

> "The pattern is: build your agents in Foundry, create a JSONL eval dataset with expected answers, collect responses in Phase 1, score with `evaluate()` in Phase 2. You get structured results you can show customers in dashboards — no more ad-hoc 'does this look right?' testing."

---

## Demo Preparation Checklist

### Before the Session (30 min ahead)

- [ ] `az login` — confirm correct subscription
- [ ] Verify `.env` file has correct `AZURE_AI_ENDPOINT` and `AZURE_AI_EVAL_ENDPOINT`
- [ ] Open `test_my_agents_v4.ipynb` in Jupyter
- [ ] Run cells 0–3 (config, imports, preview, **Phase 1 agent collection**)
- [ ] Confirm `eval_results_v4/eval_precomputed_v4.jsonl` exists with 36 rows
- [ ] Clear outputs on cells 4+ (so live demo shows fresh execution)
- [ ] Have all 4 notebook tabs open (v1–v4) for the evolution tour
- [ ] Test that cell 4 (quality evaluators) completes in < 90s

### Fallback Plan

If live demo fails during the session:
1. Show pre-run outputs from `eval_results_v4/` directory
2. Open `eval_results_v4/detailed_results.csv` in notebook cell
3. Show the PNG charts: `quality_heatmap.png`, `standard_vs_edge.png`, `edge_case_ranking.png`

### Environment Requirements

```bash
pip install -r requirements.txt   # Pinned versions for reproducibility
az login
cp .env.template .env             # Fill in your values
```
