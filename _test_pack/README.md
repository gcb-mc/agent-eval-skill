# 🧪 Test Data Toolkit

Generic tools for generating evaluation datasets from `agents.yaml`.

## Contents

- `create_dataset.py` — Reads `agents.yaml` and generates role-appropriate test prompts
- `eval_dataset_template.jsonl` — Template showing the expected JSONL format

## Usage

```bash
python _test_pack/create_dataset.py
python _test_pack/create_dataset.py --rows 10 --output my_tests.jsonl
```

## Domain-Specific Test Data

For domain-specific test data (documents, pre-built datasets), see the example directories:

- `examples/financial-agents/test_data/` — Financial documents and evaluation datasets
- `examples/azure-vm-agents/` — Azure VM management test scenarios

## Creating Your Own Test Data

1. Fill in `agents.yaml` with your agent definitions
2. Run `create_dataset.py` to generate a starter dataset
3. Review and replace `[TODO]` entries with real expected answers
4. Add domain-specific documents as needed
