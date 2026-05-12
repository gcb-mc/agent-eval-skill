# 🚀 Quickstart — Bring Your Own Agents

Evaluate **any** Azure AI Foundry agents in under 10 minutes.

---

## Step 1: Clone & Install

```bash
git clone https://github.com/gcb-mc/agent-eval-skill.git
cd agent-eval-skill
pip install -r requirements.txt
```

## Step 2: Describe Your Agents

Copy the template and edit it:

```bash
cp agents.yaml.template agents.yaml
```

Open `agents.yaml` and replace the example agents with yours:

```yaml
agents:
  # Replace these with YOUR Foundry agent names
  my-customer-service-bot:
    description: "Answers customer questions about products and policies"
    role: "responder"
    input_type: "customer question"
    output_type: "helpful answer"
    sample_prompt: "What is your return policy for electronics?"

  my-escalation-agent:
    description: "Escalates complex issues to human support"
    role: "clarifier"
    input_type: "customer complaint"
    output_type: "escalation decision"
    sample_prompt: "I've been waiting 3 weeks for my refund and nobody is helping me."
```

**Agent roles** the dataset generator understands: `summarizer`, `clarifier`, `reporter`, `responder`, `reviewer`, `advisor`, `analyst`. Use any role — unknown roles get generic test templates.

## Step 3: Configure Environment

```bash
cp .env.template .env
```

Edit `.env`:

```bash
AZURE_AI_ENDPOINT=https://<your-account>.services.ai.azure.com/api/projects/<your-project>
AZURE_AI_EVAL_ENDPOINT=https://<your-account>.services.ai.azure.com
```

Then authenticate:

```bash
az login
```

## Step 4: Generate Test Data

```bash
python _test_pack/create_dataset.py
```

This reads `agents.yaml` and generates `eval_dataset.jsonl` with role-appropriate test prompts. Review the output and replace `[TODO]` entries with real test cases for better evaluation quality.

Options:
```bash
python _test_pack/create_dataset.py --rows 10      # 10 rows per agent
python _test_pack/create_dataset.py --output my_tests.jsonl  # custom output path
```

## Step 5: Run the Evaluation

```bash
# From repo root (important!)
jupyter notebook notebooks/starter_eval.ipynb
```

The notebook will:
1. Load your agents from `agents.yaml`
2. **Phase 1**: Call each agent with every test prompt → cache responses
3. **Phase 2**: Score responses with Azure AI evaluators (groundedness, relevance, etc.)
4. **Dashboard**: Show per-agent comparison charts
5. **Export**: Save results as CSV + JSON

### What you'll see

```
✅ Loaded 2 agents from agents.yaml
   • my-customer-service-bot (responder): Answers customer questions...
   • my-escalation-agent (clarifier): Escalates complex issues...
✅ Loaded 10 rows from eval_dataset.jsonl
   Progress: 5/20
   Progress: 10/20
   ...
✅ Phase 1 complete — 20 responses saved
✅ 5 evaluators active: ['groundedness', 'relevance', 'coherence', 'fluency', 'f1_score']
✅ Phase 2 complete — evaluation scores computed
```

---

## 🔄 Re-running

Phase 1 results are **cached** — if your agents and dataset haven't changed, re-runs skip the slow agent calls and jump straight to scoring. Change an agent name or modify the dataset and the cache invalidates automatically.

---

## 📂 Want to see examples?

The `examples/` directory has two complete, working evaluations:

| Example | Agents | Domain |
|---------|--------|--------|
| `examples/financial-agents/` | Summarizer, Clarifier, Reporter | Financial document processing |
| `examples/azure-vm-agents/` | Monitor Recommender, VM Resize Analyst | Azure infrastructure management |

These show the evaluation framework applied to real-world agent systems.

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `FileNotFoundError: agents.yaml` | Copy `agents.yaml.template` to `agents.yaml` and fill in your agents |
| `KeyError: 'AZURE_AI_ENDPOINT'` | Add your endpoint to `.env` and restart the Jupyter kernel |
| `429 rate limit errors` | Built-in retry logic handles most cases; increase `time.sleep()` in Phase 1 if persistent |
| Agent calls return `[ERROR]` | Verify agent names match exactly what's in Foundry portal |
| Content filter blocks evaluators | Use subtler test prompts (see `eval-troubleshooting` skill) |
| Phase 1 not caching | Check that `eval_results/.cache_meta.json` fingerprint matches |

---

## Next Steps

- **Customize test data**: Replace `[TODO]` entries in `eval_dataset.jsonl` with real expected answers
- **Add evaluators**: Toggle safety evaluators on in `agents.yaml` → `evaluators` section
- **Ask Copilot**: With the skills installed, ask Copilot CLI things like "how do I add a custom evaluator?" or "why am I getting 429 errors?"
