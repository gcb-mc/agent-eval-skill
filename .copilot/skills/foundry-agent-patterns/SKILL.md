---
name: "foundry-agent-patterns"
description: "How to call Azure AI Foundry prompt agents — responses.create + agent_reference, AIProjectClient setup, agent registration"
domain: "azure-ai-foundry"
confidence: "high"
source: "production patterns for Foundry-hosted prompt agents using OpenAI SDK + agent_reference"
---

## Context

This skill covers the correct patterns for calling **Azure AI Foundry prompt agents** using the OpenAI SDK. The `responses.create` + `agent_reference` pattern is the current method — it replaces the old Assistants beta API. In this repo, agent names and related configuration should come from `agents.yaml`, not hardcoded strings in notebooks or scripts.

Use this skill when:
- Calling Foundry prompt agents from Python code
- Setting up `AIProjectClient` for agent registration and management
- Understanding the difference between `responses.create` and `chat.completions.create`
- Building retry logic for agent calls
- Setting up credentials and environment for Foundry projects

## Patterns

### Calling Foundry Prompt Agents

```python
agent_name = "your-agent-name"  # load this from agents.yaml
response = openai_client.responses.create(
    extra_body={
        "agent_reference": {
            "name": agent_name,
            "type": "agent_reference",
        }
    },
    input="Your prompt here",
)
answer = response.output_text
```

**Important:**
- This is `responses.create` + `agent_reference` — NOT `chat.completions.create`
- NOT `beta.assistants` (old pattern, deprecated for Foundry prompt agents)
- The `agent_reference.name` must match the exact name registered in Foundry
- Prefer loading the agent name from `agents.yaml` so the same config drives scaffolding, execution, and evaluation

### AIProjectClient Setup

```python
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

credential = DefaultAzureCredential()
project_client = AIProjectClient(
    endpoint=os.environ["AZURE_AI_ENDPOINT"],
    credential=credential,
)
```

### OpenAI Client via Foundry

```python
openai_client = project_client.inference.get_azure_openai_client()
```

This gives you an OpenAI client configured to talk to your Foundry project's inference endpoint.

### Agent Call with Retry Logic

```python
def call_agent(agent_name: str, prompt: str, max_retries: int = 3) -> str:
    for attempt in range(max_retries):
        try:
            response = openai_client.responses.create(
                extra_body={
                    "agent_reference": {"name": agent_name, "type": "agent_reference"}
                },
                input=prompt,
            )
            return response.output_text
        except Exception as e:
            if "429" in str(e) and attempt < max_retries - 1:
                time.sleep(2 ** attempt * 5)
            elif "content_filter" in str(e).lower():
                return "[CONTENT_FILTERED]"
            else:
                return "[ERROR]"
    return "[ERROR]"
```

### Environment Configuration

```bash
# .env.template
AZURE_SUBSCRIPTION_ID=<your-subscription-id>
AZURE_AI_ENDPOINT=https://<account>.services.ai.azure.com/api/projects/<project>
AZURE_AI_EVAL_ENDPOINT=https://<account>.services.ai.azure.com
AZURE_ACR_NAME=<your-acr-name>
```

### Agent Registration Verification

Use Azure CLI to verify agent registration:

```python
def az_cli(cmd: str) -> dict:
    """Run Azure CLI command and return JSON output."""
    result = subprocess.run(
        ["az"] + cmd.split() + ["--output", "json"],
        capture_output=True, text=True
    )
    return json.loads(result.stdout)
```

### When to Use Which API

| Pattern | Use Case |
|---------|----------|
| `responses.create` + `agent_reference` | Foundry prompt agents (current, recommended) |
| `chat.completions.create` | Direct LLM calls (e.g., for scoring/evaluation) |
| `beta.assistants` | **Deprecated** for Foundry prompt agents |

## Anti-Patterns

- Don't use `chat.completions.create` to call Foundry prompt agents — it won't route to the agent
- Don't use the Assistants beta API for Foundry agents — it's deprecated for this purpose
- Don't call agents without retry logic — 429 errors are common with rate-limited endpoints
- Don't hardcode endpoints — use environment variables and `.env` files
- Don't use the agent to judge its own outputs — use a separate LLM (like `gpt-4o`) for evaluation scoring
