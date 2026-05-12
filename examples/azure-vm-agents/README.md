# Azure VM Agents — Readiness Evaluation (Step 1)

> **Start here.** This notebook validates that your agents can actually run before you measure quality.

This notebook demonstrates the **exploration and readiness** evaluation for Azure infrastructure management agents deployed in Azure AI Foundry:

| Agent | Role |
|-------|------|
| `monitor-recommendations-agent` | Retrieves Azure Monitor recommendations |
| `vm-resize-analyst-agent` | Analyzes VM sizing and recommends changes |

## What It Checks

| Section | Validates |
|---------|-----------|
| Infrastructure | Agent registration, container images, version status |
| RBAC | Managed identity roles at correct scopes |
| Connectivity | Tool backends reachable (Azure APIs) |
| Routing | Orchestrator picks the right specialist agent |
| Tool selection | Each agent selects the right tool for a prompt |
| E2E execution | Full pipeline with live Azure API calls |
| Handoff | Multi-agent prompts route correctly |
| Summary | Auto-generated scorecard + quick-fix commands |

## Requirements

This example requires additional Azure permissions and resources:
- `AZURE_SUBSCRIPTION_ID` — subscription with VMs to analyze
- `AZURE_ACR_NAME` — Azure Container Registry (for tool images)
- RBAC roles: Reader on subscription, Monitor Reader, Advisor Reader

## Notebook

- `multi_agent_evaluation.ipynb` — Full readiness evaluation with infrastructure, RBAC, routing, and E2E checks

## Two-Notebook Journey

This is **Step 1** of the evaluation journey:

1. ✅ **Step 1 (this notebook):** Can it run? — Validate infra, identity, connectivity, routing
2. 📊 **Step 2:** How well does it run? — Use [`notebooks/test_my_agents_v4.ipynb`](../../notebooks/test_my_agents_v4.ipynb) for quality scoring with 7 evaluators and dashboards

See the main [README](../../README.md) for the full workflow.
