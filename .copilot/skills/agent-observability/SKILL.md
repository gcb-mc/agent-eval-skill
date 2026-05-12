---
name: "agent-observability"
description: "Microsoft's 5 best practices for AI agent observability — continuous monitoring, tracing, logging, evaluation, governance — from Foundry and Agent 365"
domain: "ai-agent-observability"
confidence: "high"
source: "compiled from Microsoft official blogs, Build 2025, Ignite 2025, and Azure AI Foundry docs (April 2026)"
---

## Context

This skill summarizes Microsoft's recommended best practices for AI agent observability and evaluation, drawn from official announcements for Azure AI Foundry and Microsoft Agent 365 (GA May 2026). It covers the "Agent Factory" 5-pillar framework published by Microsoft employees.

Use this skill when:
- Designing observability for AI agent systems
- Planning evaluation and monitoring strategies
- Implementing governance for multi-agent deployments
- Understanding Microsoft's recommended tooling (Foundry, Agent 365, Purview, Defender)
- Building production-ready agent systems with proper tracing and auditing

## Microsoft's 5 Observability Pillars

### 1. Continuous Monitoring

Track agent actions, decisions, and interactions in real time.

**What to monitor:**
- Agent execution: which tools were called, in what order, with what inputs/outputs
- Performance: latency, token usage, run success rates
- Anomalies: unexpected behavior patterns, "shadow AI" (agents acting outside intended scope)
- Cost: token consumption trends per agent, per scenario

**Tooling:**
- Azure AI Foundry Agent Monitoring Dashboard (Preview)
- Azure Monitor + Application Insights integration
- Agent 365 admin center dashboards

### 2. Tracing

Capture detailed execution flows to answer not just "what happened" but "why and how."

**What to trace:**
- Agent reasoning chains: how the agent selected tools, formulated responses
- Tool call sequences: input/output for each tool invocation
- Multi-agent interactions: which agent delegated to which, and why
- Model selection: which model was used and with what parameters

**Tooling:**
- OpenTelemetry-based tracing in Foundry (Preview)
- Microsoft Agent Framework tracing — agents emit traces into Foundry
- Hosted-agent tracing — tool calls and session steps surface in Foundry traces

**Implementation pattern:**
```python
# OpenTelemetry setup for Foundry agents
from opentelemetry import trace
from azure.monitor.opentelemetry.exporter import AzureMonitorTraceExporter

tracer = trace.get_tracer(__name__)
exporter = AzureMonitorTraceExporter(connection_string="...")

with tracer.start_as_current_span("agent-evaluation") as span:
    span.set_attribute("agent.name", agent_name)
    span.set_attribute("eval.phase", "collection")
    response = call_agent(agent_name, prompt)
    span.set_attribute("response.length", len(response))
```

### 3. Logging

Maintain comprehensive logs of agent decisions, tool calls, and internal state changes.

**What to log:**
- Every agent decision point and its rationale
- Tool call arguments and return values
- State transitions in multi-step workflows
- Errors, retries, and fallback behaviors

**Best practices:**
- Use structured logging (JSON format) for machine-parseable records
- Include correlation IDs across agent interactions
- Log at appropriate levels (DEBUG for traces, INFO for decisions, ERROR for failures)
- Retain logs for compliance and post-incident forensics

### 4. Evaluation

Systematically assess agent outputs through automated tools and human-in-the-loop review.

**Evaluation stages:**
- **Development:** Run evaluators in notebooks during agent development
- **CI/CD:** Integrate `evaluate()` into GitHub Actions / Azure DevOps pipelines
- **Production:** Continuous evaluation on live traffic (sampling-based)

**Built-in evaluators (Azure AI Evaluation SDK):**
- Quality: Groundedness, Relevance, Coherence, Fluency
- Agentic: TaskAdherence, IntentResolution, ResponseCompleteness
- Safety: Red Teaming Agent (PyRIT-based adversarial testing)

**Evaluation as code pattern:**
- Version-control evaluation scenarios, risk configs, and baseline prompts
- Store evaluation results in structured storage for trend tracking
- Auto-generate compliance-ready evaluation reports

### 5. Governance

Enforce policies and standards for ethical, safe, and compliant agent operations.

**Key capabilities:**
- **Agent Registry:** Use Microsoft Entra as the single source of truth for all agents (assign unique Agent IDs)
- **Access Controls:** Role-based access — only approved agents access sensitive data
- **Policy Enforcement:** Quarantine, disable, or limit agents displaying risky behavior
- **Compliance:** Integration with Microsoft Purview for data protection and insider risk management
- **Security:** Microsoft Defender integration for threat monitoring

**Agent 365 governance features (GA May 2026):**
- Centralized control plane for all agents (Microsoft-native and third-party)
- Unified observability dashboards across the agent fleet
- Lifecycle management: deployment → monitoring → decommissioning with audit trails

## Key Announcements (2025–2026)

### Azure AI Foundry
- **Foundry Agent Service (GA)** — production-grade with enterprise security and observability
- **Foundry Control Plane (Preview)** — centralized governance, lifecycle management, policy enforcement
- **Continuous Evaluation Custom Evaluators (Preview)** — plug code/prompt-based evaluators into CI/CD
- **Agent Monitoring Dashboard (Preview)** — latency, token usage, run success rates, evaluator scores
- **Red Teaming Agent** — automated adversarial testing using PyRIT
- **OpenTelemetry tracing (Preview)** — agents emit traces for tool calls and session steps

### Microsoft Agent 365 (GA May 2026)
- Enterprise control plane for ALL AI agents (Microsoft-native and third-party)
- Deep integrations: Defender, Purview, Entra for security/compliance/data protection
- Unified admin center with observability dashboards
- Available with M365 E7 and Agent 365 subscriptions

### Microsoft Purview for Agents
- AI observability and insider risk management (GA late May 2026)
- Detailed monitoring, compliance enforcement, risk policy creation for agents

## Gaps to Address in Your Projects

If your agent evaluation project does not yet include these, consider adding:

| Gap | Priority | How to Address |
|-----|----------|----------------|
| OpenTelemetry tracing | High | Add `opentelemetry` + `azure-monitor-opentelemetry-exporter` to requirements; instrument agent calls with spans |
| CI/CD evaluation pipeline | High | Create GitHub Actions workflow that runs `evaluate()` on every push |
| Red teaming / PyRIT | Medium | Add PyRIT-based adversarial test suite alongside quality evaluators |
| Entra / Purview governance | Medium | Register agents in Entra with Agent IDs; attach Purview data policies |

## Anti-Patterns

- Don't treat observability as optional — it's the foundation for debugging, compliance, and trust
- Don't monitor only happy paths — instrument error flows, retries, and fallback behaviors
- Don't skip the governance layer — agent sprawl is a real risk in enterprise environments
- Don't evaluate only during development — run continuous evaluation on production traffic
- Don't use ad-hoc "does this look right?" testing — use structured, repeatable evaluation with `evaluate()`
