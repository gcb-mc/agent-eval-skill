---
name: "multi-agent-eval"
description: "Evaluate multi-agent AI systems on Azure AI Foundry — routing accuracy, tool selection, E2E pipelines, cross-agent handoff, infrastructure readiness"
domain: "ai-agent-evaluation"
confidence: "high"
source: "battle-tested framework for evaluating Foundry-hosted multi-agent systems with live Azure backends"
---

## Context

This skill teaches how to evaluate **multi-agent AI systems with tools** hosted on Azure AI Foundry. It covers the full evaluation stack: infrastructure validation, RBAC checks, agent routing accuracy, tool selection, end-to-end pipeline testing, and cross-agent handoff detection. In this repo, treat `agents.yaml` as the source of truth for agent, evaluator, and scenario configuration.

Use this skill when:
- Setting up evaluation for multi-agent systems on Azure AI Foundry
- Building pre-production readiness checks for tool-calling agents
- Testing agent routing (does the right specialist agent get selected?)
- Validating E2E flows: user prompt → router → agent → tool call → live execution → grounded response
- Detecting and testing cross-agent handoff scenarios

## Architecture

The evaluation framework is structured as 10 sections:

| # | Section | What It Tests |
|---|---------|---------------|
| 0 | Configuration | Define N agents, their tools, routing tests, E2E scenarios, handoff tests |
| 1 | Imports & Helpers | Shared utilities, `AgentRouter` class, live tool executors |
| 2 | Per-Agent Infrastructure | ACR image exists, agent registered in Foundry, version active |
| 3 | Per-Agent Identity & RBAC | Managed identity roles assigned at correct scopes |
| 4 | Per-Agent Tool Connectivity | Each agent's backend APIs are reachable |
| 5 | Agent Router | Orchestrator LLM picks the correct specialist agent for each prompt |
| 6 | Per-Agent Tool Selection | Within each agent, LLM picks the correct tool |
| 7 | Multi-Agent E2E | Full pipeline: router → agent → tool → live execution → grounded response |
| 8 | Cross-Agent Handoff | Prompts requiring multiple agents are correctly identified and planned |
| 9 | Summary Report | System-wide score, per-agent breakdown, failure details |
| 10 | Quick Fix Commands | Auto-generated RBAC fix + rebuild commands |

## Patterns

### Declarative Agent Configuration

Everything is defined in `agents.yaml` and loaded into a single `MULTI_AGENT_CONFIG` dict at runtime:

```python
MULTI_AGENT_CONFIG = {
    "project_endpoint": "https://...",
    "subscription_id": "...",
    "acr_name": "...",
    "model_deployment": "gpt-4.1-mini",
    "agents": [
        {
            "name": "your-agent-name",
            "description": "What this agent does...",
            "version": "latest",
            "image_name": "your-agent-image",
            "image_tag": "latest",
            "required_roles": [{"role": "Reader", "scope": "subscription"}],
            "tools": [
                # OpenAI function-calling tool definitions
            ],
            "tool_selection_tests": [("User prompt", "expected_tool_name")],
            "tool_executors": {"tool_name": "Description of backend API"},
        },
    ],
    "routing_tests": [("User prompt", "expected_agent_name")],
    "e2e_scenarios": [{
        "name": "Scenario name",
        "prompt": "User prompt",
        "expected_agent": "agent-name",
        "expected_tool": "tool-name",
        "validation_keywords": ["keyword1", "keyword2"],
    }],
    "handoff_tests": [{
        "name": "Handoff scenario",
        "prompt": "Complex prompt needing multiple agents",
        "expected_primary_agent": "agent-a",
        "expected_secondary_agents": ["agent-b"],
    }],
}
```

### Agent Router Pattern

The `AgentRouter` class represents each specialist agent as an OpenAI function-calling tool. The LLM's `tool_choice` selects the agent — no custom routing logic needed.

### Assertion Framework

Two assertion functions track results globally and per-agent:

- `check(name, passed, detail)` — system-level assertion
- `agent_check(agent_name, test_name, passed, detail)` — per-agent assertion

Test names use section prefixes: `infra:`, `rbac:`, `tool_conn:`, `routing:`, `e2e:`

### Live Tool Execution

`execute_tool(tool_name, tool_args)` dispatches to the live backend or service handlers defined for the agents in `agents.yaml`. Returns a dict on success or `{"error": ...}` on failure.

### Adding a New Agent

1. Add the agent definition to `agents.yaml` with its name, description, deployment metadata, tools, and evaluation settings
2. Regenerate or load `MULTI_AGENT_CONFIG` from `agents.yaml`
3. Add or update routing tests in `routing_tests`
4. Add or update E2E scenarios in `e2e_scenarios`
5. Optionally add handoff tests
6. If new backend integrations are needed, add a handler branch in `execute_tool()`

## Anti-Patterns

- Don't test agent quality before validating infrastructure — most "my agent doesn't work" issues are RBAC or connectivity
- Don't use `chat.completions.create` for Foundry prompt agents — use `responses.create` + `agent_reference`
- Don't test only the happy path — include edge cases, ambiguous queries, and cross-agent scenarios
- Don't hardcode Azure subscription details — use `.env` files and `DefaultAzureCredential`
