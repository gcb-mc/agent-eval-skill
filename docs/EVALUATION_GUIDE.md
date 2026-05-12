# Multi-Agent Evaluation — How It Works

This document describes exactly how `test_my_agents_v2.ipynb` evaluates your Azure AI Foundry agents, what calls each agent, and how scores are calculated.

---

## Overview

The notebook runs a structured evaluation of three Foundry prompt agents against a test pack of 24 Q&A pairs derived from three synthetic financial documents. It tests each agent individually, then tests them together in a pipeline.

### Agents Under Test

| Label | Foundry Name | Role |
|-------|-------------|------|
| summarizer | `agent-summarizer` | Summarizes financial documents into structured output |
| clarification | `User-clarification-agent` | Asks follow-up questions about financial summaries |
| reporter | `report-generator-agent` | Generates consolidated financial reports |

### Test Data

- **Source:** `_test_pack/financial_eval_dataset.csv` (also available as `.jsonl`)
- **24 Q&A pairs** across 3 documents, 8 questions per document
- **Documents:** Northwind Solar (PDF), BlueRiver Retail (DOCX), Cedar Health Services (XLSX)
- **Question categories:** Company name, reporting period, revenue, net income, operating expenses, operating margin, risks, outlook/guidance

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

This is wrapped in the `call_agent(agent_name, prompt)` helper function used throughout the notebook.

> **Important:** These agents are NOT called via `chat.completions.create` or `beta.assistants`. The `agent_reference` pattern is the only method that works for Foundry prompt agents.

### Where Each Agent Is Called

| Section | Agent Used | Purpose |
|---------|-----------|---------|
| 4 — Connectivity Check | All 3 agents | Smoke test — sends "Say OK in one word" to verify each agent is reachable |
| 5 — Document Summarization | `agent-summarizer` | Summarizes each of the 3 financial documents |
| 6 — Q&A Accuracy | `agent-summarizer` | Answers 24 factual questions based on the summaries |
| 9 — Clarification Test | `User-clarification-agent` | Reviews each summary and generates follow-up questions |
| 10 — Report Generator | `report-generator-agent` | Produces a consolidated report from all 3 summaries |
| 11 — Pipeline Test | All 3 agents (in sequence) | End-to-end: Summarize → Clarify → Report on one document |

### Where the LLM (Not an Agent) Is Called

| Section | Model Used | Purpose |
|---------|-----------|---------|
| 6 — Q&A Accuracy (scoring step) | `gpt-4o` via `chat.completions.create` | Judges whether the agent's answer matches the expected answer |

This is the **only place** a direct LLM call is made. It uses `chat.completions.create` (not the agent reference pattern) because scoring requires a neutral evaluator, not one of the agents under test.

---

## How Scoring Works

### Step 1: The Agent Answers a Question

For each of the 24 Q&A pairs, the notebook:

1. Takes the summary that `agent-summarizer` already produced for that document
2. Sends a prompt to `agent-summarizer` asking it to answer the question based on the summary
3. Captures the agent's response as the "actual answer"

### Step 2: An LLM Scores the Answer

The `score_answer(question, expected, actual)` function sends a scoring prompt to `gpt-4o`:

```
You are a strict evaluator. Compare the ACTUAL answer to the EXPECTED answer.

Question: {question}
Expected: {expected}
Actual: {actual}

Respond with JSON: { "match": true/false, "score": 0-100, "reason": "..." }
```

The LLM returns a structured judgment with three fields.

### Score Ranges

| Score | Label | Meaning |
|-------|-------|---------|
| 90–100 | Full match | All key facts are present |
| 60–89 | Mostly correct | Most key facts present, minor omissions |
| 30–59 | Partial match | Some facts present, significant gaps |
| 0–29 | Wrong/missing | Answer is incorrect or doesn't address the question |

### Match vs. Score

- **`match`** (boolean): `true` if the key facts from the expected answer are present in the actual answer. Exact wording is not required.
- **`score`** (0–100): A granular accuracy rating within the ranges above.
- **`reason`** (string): A brief explanation of why the score was given.

### Aggregate Metrics

The dashboard (Section 7) computes:

- **Average Score:** Mean of all 24 individual scores
- **Match Rate:** Percentage of questions where `match == true`
- **Pass/Fail counts:** Count of `match == true` vs `match == false`

These are also broken down by document and by question category in the charts.

---

## Evaluation Flow (End to End)

```
┌─────────────────────────────────────────────────────────┐
│  Section 2: Load Test Pack                              │
│  ├── 24 Q&A pairs from CSV                              │
│  └── Evidence text from 3 financial documents           │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│  Section 4: Connectivity Check                          │
│  └── call_agent(each_agent, "Say OK") → verify alive    │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│  Section 5: Document Summarization                      │
│  └── For each document:                                 │
│      call_agent("agent-summarizer", document_context)   │
│      → produces 3 summaries (stored for later use)      │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│  Section 6: Q&A Evaluation (24 questions)               │
│  └── For each Q&A pair:                                 │
│      1. call_agent("agent-summarizer", question+summary)│
│         → actual answer                                 │
│      2. chat.completions.create(scoring_prompt)         │
│         → { match, score, reason }                      │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│  Section 7–8: Dashboard & Detailed Results              │
│  ├── KPI cards (avg score, match rate, pass/fail)       │
│  ├── Bar charts by document                             │
│  ├── Score heatmap (category × document)                │
│  └── Scrollable color-coded results table               │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│  Section 9: Clarification Agent Test                    │
│  └── call_agent("User-clarification-agent", summary)    │
│      → count follow-up questions (pass if ≥ 2)          │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│  Section 10: Report Generator Test                      │
│  └── call_agent("report-generator-agent", all_summaries)│
│      → consolidated financial report                    │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│  Section 11: Multi-Agent Pipeline                       │
│  └── Summarizer → Clarification → Report Generator     │
│      (one document, sequential handoff)                 │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│  Section 12: Export                                     │
│  ├── eval_results.csv (all 24 scored rows)              │
│  ├── eval_results_by_document.png                       │
│  ├── eval_score_distribution.png                        │
│  └── Final summary report (HTML)                        │
└─────────────────────────────────────────────────────────┘
```

---

## Outputs

| File | Contents |
|------|----------|
| `eval_results.csv` | All 24 Q&A results with actual answers, scores, match flags, and reasons |
| `eval_results_by_document.png` | Bar chart of scores and pass/fail by document |
| `eval_score_distribution.png` | Score histogram and category×document heatmap |

---

## Key Design Decisions

1. **Scoring uses a separate LLM, not the agent itself.** The evaluator must be neutral — using the agent to judge its own answers would be circular.

2. **Exact wording is not required for a match.** The scoring prompt instructs the LLM to check for key facts, not string equality. "$128.4M" and "$128.4 million" both match.

3. **Document content comes from the eval dataset's evidence column**, not from parsing the actual PDF/DOCX/XLSX files. This keeps the evaluation deterministic and avoids document-parsing failures.

4. **The clarification agent is scored by question count** (≥2 follow-up questions = pass) rather than factual accuracy, since its job is to ask questions, not answer them.

5. **The pipeline test (Section 11) is qualitative.** It verifies that the three agents can chain together, but doesn't score the final output against ground truth.
