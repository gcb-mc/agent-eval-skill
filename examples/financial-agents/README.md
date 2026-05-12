# Financial Agents — Example Evaluation

These notebooks demonstrate evaluating **financial document processing agents** deployed in Azure AI Foundry:

| Agent | Role |
|-------|------|
| `agent-summarizer` | Summarizes financial documents |
| `User-clarification-agent` | Asks clarifying questions on ambiguous requests |
| `report-generator-agent` | Generates formatted reports from data |

## Notebooks (progressive complexity)

| Notebook | What it adds |
|----------|-------------|
| `test_my_agents.ipynb` | Basic agent calling + simple quality scoring |
| `test_my_agents_v2.ipynb` | Routing evaluation + comparison dashboard |
| `test_my_agents_v3.ipynb` | Azure AI Evaluation SDK evaluators |
| `test_my_agents_v4.ipynb` | Two-phase approach, caching, 7 evaluators, full dashboard |

## Test Data

- `financial_eval_dataset.csv` / `.jsonl` — evaluation prompts about financial documents
- `eval_dataset_v4.jsonl` — enhanced dataset for v4 notebook
- `*.pdf, *.docx, *.xlsx` — synthetic financial documents referenced in prompts

## How to use as reference

These are **domain-specific examples**. For your own agents, use the generic workflow:

1. Fill in `agents.yaml` at repo root with your agents
2. Run `notebooks/starter_eval.ipynb`

See the main [README](../../README.md) for details.
