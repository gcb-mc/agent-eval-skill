# 🚀 Quickstart — Bring Your Own Agents

This guide walks you through using this repo to evaluate **your own** Azure AI Foundry agents.

---

## Step 1: Clone & Install

```bash
git clone https://github.com/gcb-mc/agent-eval-skill.git
cd agent-eval-skill
pip install -r requirements.txt
```

## Step 2: Configure Environment

```bash
cp .env.template .env
```

Edit `.env` with your values:

```bash
AZURE_SUBSCRIPTION_ID=<your-subscription-id>
AZURE_AI_ENDPOINT=https://<your-account>.services.ai.azure.com/api/projects/<your-project>
AZURE_AI_EVAL_ENDPOINT=https://<your-account>.services.ai.azure.com
AZURE_ACR_NAME=<your-acr-name>
```

Then authenticate:

```bash
az login
```

## Step 3: Choose Your Notebook

| Notebook | Purpose | Required Env Vars | Required Data |
|----------|---------|-------------------|---------------|
| `test_my_agents.ipynb` | Basic agent routing + custom scoring | `AZURE_AI_ENDPOINT` | `_test_pack/financial_eval_dataset.csv` |
| `test_my_agents_v2.ipynb` | Multi-agent pipeline + dashboard charts | `AZURE_AI_ENDPOINT` | `_test_pack/financial_eval_dataset.csv` |
| `test_my_agents_v3.ipynb` | Azure AI Eval SDK (individual evaluators) | `AZURE_AI_ENDPOINT`, `AZURE_AI_EVAL_ENDPOINT` | `_test_pack/financial_eval_dataset.csv` |
| `test_my_agents_v4.ipynb` | Batch `evaluate()` with 7 evaluators | `AZURE_AI_ENDPOINT`, `AZURE_AI_EVAL_ENDPOINT` | `eval_dataset_v4.jsonl` |
| `multi_agent_evaluation.ipynb` | Full DevOps eval (infra, RBAC, routing, E2E) | `AZURE_AI_ENDPOINT`, `AZURE_SUBSCRIPTION_ID`, `AZURE_ACR_NAME` | None (uses live Azure APIs) |

## Step 4: Customize for Your Agents

Every notebook has a **Section 0 — Configuration** cell at the top. Look for `# ⬇️ CUSTOMIZE` markers. Here's what to replace:

### For `test_my_agents*.ipynb` (v1–v4):

Replace the agent names with your Foundry-registered agent names:

```python
# ⬇️ CUSTOMIZE: Replace with your Foundry agent names
AGENTS = {
    "summarizer": "your-summarizer-agent",      # was: agent-summarizer
    "clarification": "your-clarification-agent", # was: User-clarification-agent
    "reporter": "your-reporter-agent",           # was: report-generator-agent
}
```

Replace the model deployment:

```python
# ⬇️ CUSTOMIZE: Your evaluation model deployment
EVAL_DEPLOYMENT = "gpt-4o"   # or whatever model you have deployed
```

### For `multi_agent_evaluation.ipynb`:

Replace the entire `MULTI_AGENT_CONFIG` with your agents:

```python
# ⬇️ CUSTOMIZE: Define your agents
MULTI_AGENT_CONFIG = {
    "project_endpoint": os.environ["AZURE_AI_ENDPOINT"],
    "subscription_id": os.environ["AZURE_SUBSCRIPTION_ID"],
    "acr_name": os.environ["AZURE_ACR_NAME"],
    "model_deployment": "gpt-4.1-mini",   # ⬇️ CUSTOMIZE
    "agents": [
        {
            "name": "your-agent-name",    # ⬇️ CUSTOMIZE
            "description": "What this agent does",
            # ... see README for full schema
        },
    ],
}
```

## Step 5: Create Your Eval Dataset

If using `test_my_agents_v4.ipynb`, create a JSONL file with your test cases. See `_test_pack/eval_dataset_template.jsonl` for the expected format:

```json
{"sample_id": "T-001", "query": "Your test question", "context": "Reference context", "expected_answer": "Expected answer", "response": "", "category": "standard", "document_id": "DOC-001"}
```

Fields:
| Field | Required | Description |
|-------|----------|-------------|
| `sample_id` | Yes | Unique test case ID |
| `query` | Yes | The question/prompt to send to the agent |
| `context` | Yes | Reference context for grounding evaluation |
| `expected_answer` | Yes | The correct/expected answer |
| `response` | No | Leave empty — Phase 1 fills this in automatically |
| `category` | Yes | `standard` or `edge_case` |
| `document_id` | No | Group ID for per-document analysis |

## Step 6: Run

```bash
# From repo root
jupyter notebook notebooks/test_my_agents_v4.ipynb
```

**Important:** Always launch Jupyter from the **repo root** directory, not from `notebooks/`. The notebooks resolve paths relative to the repo root.

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `FileNotFoundError: _test_pack/...` | Launch Jupyter from the repo root, not `notebooks/` |
| `429 rate limit errors` | The notebooks include retry logic; if persistent, increase cooldown in config |
| Agent calls return errors | Check RBAC roles on your agent's managed identity (run `multi_agent_evaluation.ipynb` sections 2-4) |
| `AZURE_AI_EVAL_ENDPOINT` missing | Required for v3/v4 notebooks — add to `.env` |
| Content filter blocks evaluators | Use subtler edge case prompts (see eval-troubleshooting skill) |
