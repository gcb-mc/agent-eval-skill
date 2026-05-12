# Azure VM Agents — Example Evaluation

This notebook demonstrates evaluating **Azure infrastructure management agents** deployed in Azure AI Foundry:

| Agent | Role |
|-------|------|
| `monitor-recommendations-agent` | Retrieves Azure Monitor recommendations |
| `vm-resize-analyst-agent` | Analyzes VM sizing and recommends changes |

## Requirements

This example requires additional Azure permissions and resources:
- `AZURE_SUBSCRIPTION_ID` — subscription with VMs to analyze
- `AZURE_ACR_NAME` — Azure Container Registry (for tool images)
- RBAC roles: Reader on subscription, Monitor Reader, Advisor Reader

## Notebook

- `multi_agent_evaluation.ipynb` — Full multi-agent eval with tool connectivity checks, routing, handoff detection

## How to use as reference

This is a **domain-specific example**. For your own agents, use the generic workflow:

1. Fill in `agents.yaml` at repo root with your agents
2. Run `notebooks/starter_eval.ipynb`

See the main [README](../../README.md) for details.
