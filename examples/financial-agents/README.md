# Financial Agents — Example Data

Sample test data and evaluation results for **financial document processing agents** deployed in Azure AI Foundry:

| Agent | Role |
|-------|------|
| `agent-summarizer` | Summarizes financial documents |
| `User-clarification-agent` | Asks clarifying questions on ambiguous requests |
| `report-generator-agent` | Generates formatted reports from data |

## Test Data

Located in `test_data/`:

| File | Description |
|------|-------------|
| `northwind_solar_q1_fy2026.pdf` | Investor-style PDF quarterly update |
| `blueriver_retail_fy2025.docx` | Board memo in Word format |
| `cedar_health_services_q4_2025.xlsx` | Financial metrics workbook |
| `financial_eval_dataset.csv` | Tabular evaluation set |
| `financial_eval_dataset.jsonl` | JSONL evaluation set |

The evaluation uses `eval_dataset_v4.jsonl` (36 test cases: 24 standard + 12 edge).

## Sample Results

The `eval_results_v4/` directory contains pre-computed evaluation results from running these agents through the notebook, useful as a reference for expected output format.

## How to use as reference

This is a **domain-specific example**. For your own agents, use the generic workflow:

1. Fill in `agents.yaml` at repo root with your agents
2. Run [`notebooks/test_my_agents_v4.ipynb`](../../notebooks/test_my_agents_v4.ipynb)

See the main [README](../../README.md) for details.
