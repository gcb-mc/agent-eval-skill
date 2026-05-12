# CSA Talking Points — Multi-Agent Evaluation Notebooks

> **Audience:** Cloud Solution Architects working with Azure AI Foundry & Agents
> **Format:** Two-notebook walkthrough + key evaluation concepts

---

## Part 1: `multi_agent_evaluation.ipynb` — The Readiness Checklist (Start Here)

### What This Notebook Does

> "This is the full pre-production readiness checklist for multi-agent systems with tools. Think of it as the 'can my agents actually run in production?' notebook. **Start here before measuring quality.**"

### Section-by-Section Talking Points

**Section 0 — Configuration (the only cell you edit)**
- Everything is defined in one `MULTI_AGENT_CONFIG` dict — agents, tools, routing tests, E2E scenarios, handoff tests
- This is the pattern to hand customers: define your agents declaratively, then the notebook validates everything automatically
- Uses OpenAI function-calling schema for tool definitions — same format whether you're in Foundry or standalone

**Section 1 — Imports & Helpers**
- Key abstraction: `AgentRouter` class — represents each specialist agent as a function-calling tool
- The LLM's `tool_choice` does the routing — no custom routing logic needed
- `execute_tool()` dispatches to live Azure SDK calls (Compute, Monitor, Advisor, Retail Prices API)

**Sections 2–4 — Infrastructure, RBAC, Connectivity** *(the "plumbing" checks)*
- "Before we test if agents are smart, we test if they can even run"
- Section 2: Does the ACR image exist? Is the agent registered in Foundry? Is the version active?
- Section 3: Does the managed identity have the right RBAC roles at the right scopes?
- Section 4: Can each agent's tools actually reach their backend APIs?
- **Key point for CSAs:** These are the checks that save customers hours of debugging. Most "my agent doesn't work" issues are RBAC or connectivity, not prompt engineering.

**Section 5 — Agent Router Test**
- Tests whether the orchestrator LLM picks the right specialist agent for each prompt
- Pattern: each agent is described as a function-calling tool → the LLM selects via tool_choice
- "This is the multi-agent routing pattern — no LangChain, no custom router, just function calling"

**Section 6 — Per-Agent Tool Selection**
- Within each specialist agent, does the LLM select the correct tool for a given prompt?
- Tests the second level of routing: user → right agent → right tool

**Section 7 — Multi-Agent E2E Scenarios**
- Full pipeline: router → agent selection → tool call → live execution against Azure APIs → grounded response
- Validates that the final response contains expected keywords from real API data
- "This is where you prove the system works end-to-end, not just that individual pieces work"

**Section 8 — Cross-Agent Handoff**
- Tests prompts that need more than one agent (e.g., "resize this VM and show me the cost impact")
- Uses structured JSON output to identify primary and secondary agents
- "Multi-agent handoff is where most systems break down — this section catches that"

**Sections 9–10 — Summary & Quick Fix Commands**
- Auto-generated scorecard with per-agent breakdown
- Quick fix commands for RBAC remediation and image rebuilds
- "You run the notebook, and it tells you exactly what to fix — copy-paste commands"

### When to Use This Notebook
- Customer has **tool-calling agents** with live Azure backends
- You need to validate the full stack: infra → identity → connectivity → routing → execution
- Pre-production readiness gates

---

## Part 2: `test_my_agents_v4.ipynb` — The Quality Evaluation (Step 2)

### What This Notebook Does

> "Once your agents are running, this notebook evaluates agent *quality* — not can it run, but how well does it answer? It uses the Azure AI Evaluation SDK's batch `evaluate()` function with 7 evaluators."

### The Two-Phase Architecture (Most Important Pattern)

```
Phase 1: Call agents → save responses to JSONL     (slow, rate-limited, fragile)
Phase 2: Run evaluate() on saved JSONL → scores    (fast, deterministic, retryable)
```

- "This is the single most important pattern to teach customers. If Phase 2 fails, you just re-run it — no need to re-call agents."
- You can run different evaluator combinations on the same pre-computed data
- JSONL is the bridge format between phases

### Section-by-Section Talking Points

**Section 0 — Config**
- Loads `.env` for endpoints, defines agent names, points to the eval dataset
- Dataset: 36 test cases (24 standard + 12 edge cases) across 3 financial documents
- Edge cases include: prompt injection, ambiguous queries, multilingual, out-of-scope

**Section 1 — Imports & Clients**
- Sets up `DefaultAzureCredential`, OpenAI client, and the 7 evaluators from `azure-ai-evaluation`
- Key import: `from azure.ai.evaluation import evaluate` — the batch function

**Section 2 — Preview Dataset**
- Quick visual of the test pack — standard vs edge case breakdown
- "Always show your customer what they're testing against before showing results"

**Section 3 — Phase 1: Collect Agent Responses**
- Calls each Foundry prompt agent using the `responses.create` + `agent_reference` pattern
- Built-in retry logic (3 attempts, exponential backoff) for 429 errors
- Saves everything to `eval_precomputed_v4.jsonl`
- "This is the slow part — run it before your demo or customer meeting"

**Section 4 — Phase 2, Batch 1: Quality Evaluators**
- Runs 4 evaluators: **Groundedness**, **Relevance**, **Coherence**, **Fluency**
- Each scores 1–5 per response
- "These answer: is the response grounded in context, does it address the question, is it well-structured, and is it readable?"

**Section 5 — Phase 2, Batch 2: Agentic Evaluators**
- 60-second cooldown between batches (rate limit management)
- Runs 3 NEW evaluators: **TaskAdherence**, **IntentResolution**, **ResponseCompleteness**
- "These are purpose-built for agent scenarios — they didn't exist in earlier SDK versions"
- TaskAdherence: Did the agent follow its instructions?
- IntentResolution: Was the user's intent fully resolved?
- ResponseCompleteness: Is all requested information present?

**Sections 6–10 — Results & Visualizations**
- Quality heatmap: evaluator scores × question category
- Standard vs edge case comparison: where do agents break down?
- Edge case weakness ranking: which edge types are most problematic?
- Scrollable detailed results table with color-coded scores
- CSV export for further analysis

### When to Use This Notebook
- Customer has **Foundry prompt agents** (with or without tools)
- You need to measure response quality with structured, repeatable scoring
- Building evaluation into CI/CD or pre-deployment gates

---

## Part 3: Key Evaluation Concepts for CSAs

### 1. Why Evaluation Matters

> "Every customer says their agent 'works.' Evaluation proves it — or reveals where it doesn't."

- Ad-hoc testing ("does this look right?") doesn't scale
- Production agents need baseline scores, regression tracking, and edge case coverage
- Evaluation is how you move from demo to production

### 2. The 7 Evaluators Explained

| Evaluator | Question It Answers | Type |
|-----------|-------------------|------|
| Groundedness | Is the response based on provided context, not hallucinated? | Quality |
| Relevance | Does the response actually address what was asked? | Quality |
| Coherence | Is the response logically structured and consistent? | Quality |
| Fluency | Is the language natural and professional? | Quality |
| **TaskAdherence** | Did the agent follow its system instructions? | Agentic |
| **IntentResolution** | Was the user's actual goal achieved? | Agentic |
| **ResponseCompleteness** | Is all the requested information present? | Agentic |

- Quality evaluators = "is the response good writing?"
- Agentic evaluators = "did the agent do its job?"
- For agent scenarios, the agentic evaluators are often more important

### 3. The Foundry Agent Calling Pattern

```python
response = oai.responses.create(
    extra_body={
        "agent_reference": {"name": agent_name, "type": "agent_reference"}
    },
    input=prompt,
)
answer = response.output_text
```

- This is `responses.create` + `agent_reference` — the current pattern for Foundry prompt agents
- NOT `chat.completions.create`, NOT `beta.assistants`
- Important to call out because customers may have old code using the Assistants API

### 4. Rate Limit Management

- 4 evaluators × 36 rows = fine
- 7 evaluators × 36 rows simultaneously = 429 storm
- Solution: split into 2 batches with a 60-second cooldown
- The SDK does NOT manage this for you — you must do it yourself
- Agent calls also need retry logic (3 attempts, exponential backoff)

### 5. Column Mapping Gotcha

```python
# With a target function:
evaluator_config={"response": "${target.response}"}

# With pre-computed data (no target):
evaluator_config={"response": "${data.response}"}
```

- This trips up everyone the first time
- If you pre-compute responses (recommended), use `${data.response}`
- If you pass a `target` function to `evaluate()`, use `${target.response}`

### 6. Edge Cases Matter Most

- Standard Q&A tests prove the happy path works
- Edge cases reveal real-world failure modes:
  - **Prompt injection**: Does the agent resist manipulation?
  - **Ambiguous queries**: Does it ask for clarification or guess?
  - **Multilingual**: Does it handle non-English input?
  - **Out-of-scope**: Does it gracefully decline?
- "If you only test the happy path, you'll be surprised in production"

### 7. Two Notebooks, Two Purposes — Use in Sequence

| Step | Notebook | Tests | Audience |
|------|----------|-------|----------|
| **1 (Start here)** | `multi_agent_evaluation.ipynb` | Can it run? (infra, RBAC, routing, tools, E2E) | Platform/DevOps teams |
| **2** | `test_my_agents_v4.ipynb` | How well does it answer? (quality + agentic scoring) | AI/ML teams, product owners |

- Start with `multi_agent_evaluation` to validate the plumbing works
- Then use `test_my_agents_v4` to measure and improve response quality
- Use both for full coverage

### 8. What to Tell Customers

> "Build your agents in Foundry. Create a JSONL eval dataset with expected answers. Collect responses in Phase 1, score with `evaluate()` in Phase 2. You get structured results you can put in dashboards — no more ad-hoc 'does this look right?' testing."

---

## Quick Reference — Demo Flow

1. Open `multi_agent_evaluation.ipynb` → walk through the config, explain the 10-section structure, show a few outputs
2. Switch to `test_my_agents_v4.ipynb` → run cells 4–5 live (evaluators), then show the dashboard charts
3. Close with the key concepts: two-phase approach, 7 evaluators, edge cases, rate limit batching
