# Copilot Instructions — Agent Eval Skill

## What This Repo Is

A GitHub Copilot agent skill for evaluating multi-agent AI systems on Azure AI Foundry. The `.copilot/skills/` directory contains 5 skills that Copilot auto-discovers:

1. **multi-agent-eval** — Framework for evaluating multi-agent systems (routing, tools, E2E, handoff)
2. **eval-sdk-patterns** — Azure AI Evaluation SDK patterns (7 evaluators, batch evaluate, two-phase)
3. **foundry-agent-patterns** — How to call Foundry prompt agents (responses.create + agent_reference)
4. **eval-troubleshooting** — Rate limits, content filters, column mapping gotchas
5. **agent-observability** — Microsoft's 5 best practices (monitoring, tracing, logging, eval, governance)

## Build & Run

```bash
pip install -r requirements.txt
az login
cp .env.template .env
# Edit .env with your values
jupyter notebook notebooks/test_my_agents_v4.ipynb
```

## Key Conventions

- Tool definitions use OpenAI function-calling schema
- Agent calls use `responses.create` + `agent_reference` (NOT `chat.completions.create`)
- Evaluation uses two-phase approach: collect responses to JSONL, then run `evaluate()`
- Evaluators are batched (4 quality + 3 agentic) with 30s cooldown between batches
- All Azure interactions require `az login` and `DefaultAzureCredential`
