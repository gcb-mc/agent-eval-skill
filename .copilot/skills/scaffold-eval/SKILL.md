---
name: "scaffold-eval"
description: "Scaffold complete evaluation for any Azure AI Foundry agents — agents.yaml-driven setup, dataset generation, starter notebook workflow, result interpretation"
domain: "ai-agent-evaluation"
confidence: "high"
source: "repo workflow for bringing your own Foundry agents into a reusable evaluation scaffold"
---

## Context

This skill teaches how to scaffold a **complete evaluation for any Azure AI Foundry agents** using this repo's config-driven workflow. The key idea is: **describe your agents once in `agents.yaml`, generate realistic JSONL test data, run the starter notebook, then compare results per agent**.

Use this skill when:
- Bringing your own Foundry agents into this repo
- Creating a starter evaluation without hardcoding agent details in notebooks
- Generating realistic test data for different agent roles
- Running the two-phase evaluation flow (cache responses first, score second)
- Explaining evaluation outputs to users and teammates

## Workflow

### Bring Your Own Agents

1. Clone the repo and install dependencies
2. Copy `agents.yaml.template` → `agents.yaml`
3. Fill in your Foundry agent names and metadata
4. Set up `.env` with your Foundry endpoints
5. Generate test data: `python _test_pack/create_dataset.py`
6. Run `notebooks/test_my_agents_v4.ipynb`
7. Review the dashboard and per-agent scores

### What `agents.yaml` Controls

`agents.yaml` sits at the **repo root** and is the single source of truth for evaluation. Its format is defined in `agents.yaml.template`.

It contains:
- **Project settings** — endpoint env vars and model deployment
- **Agents** — `name`, `description`, `role`, `input_type`, `output_type`, `sample_prompt`
- **Dataset config** — JSONL path, row count, column names
- **Evaluator toggles** — which quality, safety, or correctness evaluators to run
- **Output settings** — where precomputed responses and eval scores are written

### Minimal `agents.yaml` Shape

```yaml
project:
  endpoint_env: "AZURE_AI_ENDPOINT"
  eval_endpoint_env: "AZURE_AI_EVAL_ENDPOINT"
  model: "gpt-4o"

agents:
  my-agent:
    description: "What the agent does"
    role: "summarizer"
    input_type: "text"
    output_type: "summary"
    sample_prompt: "Summarize the following content."

dataset:
  path: "eval_dataset.jsonl"
  rows_per_agent: 5

evaluators:
  groundedness: true
  relevance: true
  coherence: true
  fluency: true
  f1_score: true
  violence: false

output:
  results_dir: "eval_results"
  precomputed_file: "precomputed.jsonl"
  eval_results_file: "eval_results.json"
```

## Patterns

### Read `agents.yaml` First

Before generating data or editing notebooks:
1. Read `agents.yaml`
2. Read each agent's `description`, `role`, `input_type`, `output_type`, and `sample_prompt`
3. Infer what realistic user queries look like for that domain
4. Generate test rows that reflect the real tasks the agent should handle

`description` tells you the business purpose. `sample_prompt` tells you the interaction style. `input_type` and `output_type` tell you what the dataset's `query`, `context`, and `ground_truth` should look like.

### Generate Test Data for Any Agent

Create JSONL rows with these columns:
- `query`
- `context`
- `ground_truth`

Guidelines:
- **Query** should sound like a real user request for that agent
- **Context** should contain the information the agent would use or reference
- **Ground truth** should be a plausible ideal answer for the configured `output_type`

Examples by output type:
- `summary` → context is source material, ground truth is a concise summary
- `helpful answer` → context is customer/account/product info, ground truth is the desired response
- `review comments` → context is code diff or PR notes, ground truth is specific review feedback
- `recommendation` → context is product/catalog/customer needs, ground truth is a recommendation with rationale
- `analysis with charts` → context is structured metrics, ground truth is the expected analysis narrative and chart direction

If available, you can auto-generate starter data with:

```bash
python _test_pack/create_dataset.py
```

### Customize the Starter Notebook

`notebooks/test_my_agents_v4.ipynb` reads `agents.yaml` automatically.

The default customization path is:
1. Fill out `agents.yaml`
2. Create or generate the dataset
3. Run the notebook

That means the notebook should stay mostly generic. Users only need to edit the notebook if they want:
- Custom evaluator logic
- Additional preprocessing or postprocessing
- Extra visualizations
- Agent-specific assertions beyond the shared scaffold

### Two-Phase Evaluation Interpretation

The scaffold uses a two-phase pattern:

```text
Phase 1: Call agents and save responses to JSONL
Phase 2: Run Azure AI Evaluation SDK scorers on saved outputs
```

Outputs:
- **Phase 1** → precomputed JSONL with agent responses
- **Phase 2** → evaluation scores from the Azure AI Evaluation SDK

Why this matters:
- Re-run scoring without re-calling agents
- Save money on repeated agent calls
- Compare evaluator combinations on the same cached outputs

### Score Ranges

| Score Type | Range | Meaning |
|------------|-------|---------|
| Quality evaluators | `1-5` | Higher is better |
| Safety evaluators | `0-7` severity | Lower is safer |
| F1 | `0-1` | Higher means better token/answer overlap |

The dashboard should be used for **per-agent comparison** — which agent is strongest on relevance, which has safety concerns, and which has weak completeness or correctness.

## Agent Type Examples

### Customer Service Bot

```yaml
customer-service-bot:
  description: "Answers customer support questions about orders, refunds, and account issues"
  role: "responder"
  input_type: "customer question"
  output_type: "helpful answer"
  sample_prompt: "My refund has not arrived yet. What should I do next?"
```

### Code Review Agent

```yaml
code-review-agent:
  description: "Reviews code changes and identifies bugs, risks, and missing tests"
  role: "reviewer"
  input_type: "code diff"
  output_type: "review comments"
  sample_prompt: "Review this pull request diff and identify correctness or security issues."
```

### Sales Assistant

```yaml
sales-assistant:
  description: "Recommends products based on customer requirements and budget"
  role: "advisor"
  input_type: "product question"
  output_type: "recommendation"
  sample_prompt: "Which laptop would you recommend for a small design team with a moderate budget?"
```

### Document Summarizer

```yaml
document-summarizer:
  description: "Summarizes long documents into concise, structured takeaways"
  role: "summarizer"
  input_type: "long document"
  output_type: "summary"
  sample_prompt: "Summarize this annual report into key business, financial, and risk highlights."
```

### Data Analyst

```yaml
data-analyst:
  description: "Answers business questions using structured data and explains trends visually"
  role: "analyst"
  input_type: "data question"
  output_type: "analysis with charts"
  sample_prompt: "Analyze quarterly sales performance and highlight the main trends and outliers."
```

## Anti-Patterns

- Don't hardcode agent names in notebooks — load them from `agents.yaml`
- Don't skip Phase 1 caching — it saves API calls, time, and money
- Don't run every evaluator by default if you only need a subset — toggle them in `agents.yaml`
- Don't use the same endpoint for agents and evals in production if separate endpoints help with rate limits
- Don't generate generic test prompts divorced from the agent's role — use `description` and `sample_prompt` as the anchor
- Don't treat the notebook as the source of truth — keep the configuration in `agents.yaml`
