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
| `test_my_agents_v4.ipynb` | Two-phase approach, incremental resume, conditional clarification, full dashboard |

### v4 Highlights

- **Conditional clarification**: Only edge cases with ambiguous/contradictory content trigger the clarification agent. Standard queries use a 2-agent pipeline (summarizer → reporter), saving ~24 API calls per run.
- **Incremental resume**: Responses are saved row-by-row. Interrupted runs pick up where they left off.
- **60s timeout**: Agent calls time out after 60 seconds with automatic retry.

## Test Data

Located in `test_data/`:

| File | Description |
|------|-------------|
| `northwind_solar_q1_fy2026.pdf` | Investor-style PDF quarterly update |
| `blueriver_retail_fy2025.docx` | Board memo in Word format |
| `cedar_health_services_q4_2025.xlsx` | Financial metrics workbook |
| `financial_eval_dataset.csv` | Tabular evaluation set |
| `financial_eval_dataset.jsonl` | JSONL evaluation set |

The v4 notebook also uses `examples/financial-agents/eval_dataset_v4.jsonl` (36 test cases: 24 standard + 12 edge).

## How to use as reference

These are **domain-specific examples**. For your own agents, use the generic workflow:

1. Fill in `agents.yaml` at repo root with your agents
2. Run `notebooks/starter_eval.ipynb`

See the main [README](../../README.md) for details.
