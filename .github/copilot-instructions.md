# Copilot Instructions — Agent Eval Skill

## What This Repo Is

A GitHub Copilot agent skill for evaluating **any** multi-agent AI system on Azure AI Foundry. Users describe their agents in `agents.yaml` and the repo handles evaluation, scoring, and dashboards.

### Skills (`.copilot/skills/`)

1. **scaffold-eval** — How to scaffold evaluation for any agents from `agents.yaml`
2. **multi-agent-eval** — Multi-agent evaluation framework (routing, tools, E2E, handoff)
3. **eval-sdk-patterns** — Azure AI Evaluation SDK (7 evaluators, batch evaluate, two-phase)
4. **foundry-agent-patterns** — How to call Foundry agents (responses.create + agent_reference)
5. **eval-troubleshooting** — Rate limits, content filters, column mapping gotchas
6. **agent-observability** — Microsoft's 5 observability best practices

## Workflow

```bash
cp agents.yaml.template agents.yaml   # describe your agents
cp .env.template .env                 # add your endpoints
python _test_pack/create_dataset.py   # generate test data
jupyter notebook notebooks/starter_eval.ipynb  # run evaluation
```

## Key Files

- `agents.yaml` — Single source of truth for agent configuration
- `notebooks/starter_eval.ipynb` — Generic, config-driven evaluation notebook
- `_test_pack/create_dataset.py` — Generates eval JSONL from agents.yaml
- `examples/` — Domain-specific reference implementations (financial, Azure VM)

## Key Conventions

- Agent calls use `responses.create` + `agent_reference` (NOT `chat.completions.create`)
- Evaluation uses two-phase approach: collect responses to JSONL, then run `evaluate()`
- Phase 1 responses are cached with SHA-256 fingerprints
- All Azure interactions require `az login` and `DefaultAzureCredential`
- Agent configuration lives in `agents.yaml`, not hardcoded in notebooks
