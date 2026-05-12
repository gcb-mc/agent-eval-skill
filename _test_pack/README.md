# Financial Agent Test Pack

This package contains **synthetic financial documents** created for testing document understanding agents.

## Included documents
- `northwind_solar_q1_fy2026.pdf` — investor-style PDF update
- `blueriver_retail_fy2025.docx` — board memo in Word
- `cedar_health_services_q4_2025.xlsx` — workbook with metrics and notes
- `financial_eval_dataset.csv` — tabular evaluation set
- `financial_eval_dataset.jsonl` — JSONL evaluation set

## Suggested use
1. Feed each document to the summarizer agent.
2. Use the clarification agent on the summaries.
3. Validate answers to the general questions against the evaluation dataset.

## Note
All content is synthetic and intended only for testing.
