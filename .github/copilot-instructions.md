# Copilot Instructions — Agent Eval Skill

## What This Repo Is

A GitHub Copilot agent skill for evaluating **any** multi-agent AI system on Azure AI Foundry. Users describe their agents in `agents.yaml` and the repo handles evaluation, scoring, and dashboards.

> **Note:** `agents.yaml` integration is planned but not yet wired into the notebooks. Currently, users edit notebook config cells directly to point to their agents.

### Skills (`.copilot/skills/`)

1. **scaffold-eval** — How to scaffold evaluation for any agents from `agents.yaml`
2. **multi-agent-eval** — Multi-agent evaluation framework (routing, tools, E2E, handoff)
3. **eval-sdk-patterns** — Azure AI Evaluation SDK (7 evaluators, batch evaluate, two-phase)
4. **foundry-agent-patterns** — How to call Foundry agents (responses.create + agent_reference)
5. **eval-troubleshooting** — Rate limits, content filters, column mapping gotchas
6. **agent-observability** — Microsoft's 5 observability best practices

## Two-Notebook Evaluation Journey

### Step 1: Can it run? → `multi_agent_evaluation.ipynb`
Exploration and readiness — infra checks, RBAC, tool connectivity, agent routing, E2E execution, cross-agent handoff.

### Step 2: How well does it run? → `test_my_agents_v4.ipynb`
Quality evaluation — 7 evaluators (4 quality + 3 agentic), two-phase approach, dashboards, CSV/JSON export.

## Workflow

```bash
cp agents.yaml.template agents.yaml   # describe your agents
cp .env.template .env                 # add your endpoints

# Step 1: Validate readiness
jupyter notebook examples/azure-vm-agents/multi_agent_evaluation.ipynb

# Step 2: Measure quality
jupyter notebook notebooks/test_my_agents_v4.ipynb
```

## Key Files

- `agents.yaml` — Single source of truth for agent configuration (planned integration)
- `examples/azure-vm-agents/multi_agent_evaluation.ipynb` — Readiness notebook (infra, RBAC, routing, E2E)
- `notebooks/test_my_agents_v4.ipynb` — Quality evaluation notebook with 7 evaluators and dashboards
- `_test_pack/create_dataset.py` — Generates eval JSONL from agents.yaml
- `examples/financial-agents/` — Sample test data and results for the quality evaluation notebook

## Key Conventions

- Agent calls use `responses.create` + `agent_reference` (NOT `chat.completions.create`)
- Quality evaluation uses two-phase approach: collect responses to JSONL, then run `evaluate()`
- Phase 1 responses are saved incrementally to JSONL and resume automatically on re-run
- Phase 2 evaluators run in two batches with 60s cooldown to avoid 429 rate limits
- All Azure interactions require `az login` and `DefaultAzureCredential`
