# 🚀 Quickstart — Bring Your Own Agents

Evaluate **any** Azure AI Foundry agents in under 10 minutes.

> **Two-notebook journey:** Start with `multi_agent_evaluation.ipynb` to validate your agents can run (infra, RBAC, routing), then use `test_my_agents_v4.ipynb` to measure how well they perform (quality scoring + dashboards).

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

## Step 5: Validate Your Agents Can Run (Exploration)

Start with the **readiness notebook** to verify infrastructure, RBAC, and connectivity:

```bash
jupyter notebook examples/azure-vm-agents/multi_agent_evaluation.ipynb
```

This notebook checks:
- ✅ Agent registration and infrastructure
- ✅ Identity and RBAC permissions
- ✅ Tool backend connectivity
- ✅ Agent routing and selection
- ✅ End-to-end execution
- ✅ Cross-agent handoff

> **Tip:** Use this notebook as a template — adapt the config section to your agents and tools.

## Step 6: Measure Quality (Evaluation)

Once your agents are running, measure response quality with the **evaluation notebook**:

```bash
jupyter notebook notebooks/test_my_agents_v4.ipynb
```

> **Note:** `agents.yaml` integration is planned but not yet wired into the notebook. Currently, edit Section 0 (Configuration) in the notebook to point to your agents, dataset, and output paths.

The notebook will:
1. **Phase 1**: Call each agent with every test prompt → cache responses to JSONL
2. **Phase 2**: Score responses with 7 Azure AI evaluators in two batches:
   - **Batch 1 (Quality):** Groundedness, Relevance, Coherence, Fluency
   - **Batch 2 (Agentic):** TaskAdherence, IntentResolution, ResponseCompleteness
3. **Dashboard**: Heatmaps, standard vs edge case comparison, weakness ranking
4. **Export**: Save results as CSV + JSON + PNG charts

### What you'll see

```
📞 Phase 1: Calling 3-agent pipeline for 36 rows...
  [ 1/36] What is the company name?... ✅
  [ 2/36] What reporting period...     ✅
  ...
✅ Phase 1 complete: 36 responses in 478s

🚀 Phase 2a: Running 4 quality evaluators...
✅ Batch 1 done in 72s
⏳ Pausing 60s before batch 2...
🚀 Phase 2b: Running 3 agentic evaluators...
✅ Batch 2 done in 65s

📊 Dashboard ready — 7 evaluators × 36 rows
```

---

## 🔄 Re-running

Phase 1 results are **saved incrementally** — each response is written to the JSONL as it completes. If the notebook is interrupted, re-runs pick up where you left off. To force a full re-run, delete the output JSONL file.

---

## 📂 Want to see examples?

The `examples/` directory has two complete, working evaluations:

| Example | Agents | Domain | Purpose |
|---------|--------|--------|---------|
| `examples/azure-vm-agents/` | Monitor Recommender, VM Resize Analyst | Azure infrastructure | **Step 1:** Readiness checks (infra, RBAC, routing) |
| `examples/financial-agents/` | Summarizer, Clarifier, Reporter | Financial documents | **Step 2:** Sample test data + results for quality eval |

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `FileNotFoundError: agents.yaml` | Copy `agents.yaml.template` to `agents.yaml` and fill in your agents |
| `KeyError: 'AZURE_AI_ENDPOINT'` | Add your endpoint to `.env` and restart the Jupyter kernel |
| `429 rate limit errors` | Built-in retry logic handles most cases; the notebook uses 60s cooldown between eval batches |
| Agent calls return `[ERROR]` | Verify agent names match exactly what's in Foundry portal |
| Content filter blocks evaluators | Use subtler test prompts (see `eval-troubleshooting` skill) |
| Phase 1 interrupted mid-run | Re-run the cell — it resumes from the last saved response |

---

## Next Steps

- **Customize test data**: Replace `[TODO]` entries in `eval_dataset.jsonl` with real expected answers
- **Add evaluators**: Toggle safety evaluators on in `agents.yaml` → `evaluators` section
- **Ask Copilot**: With the skills installed, ask Copilot CLI things like "how do I add a custom evaluator?" or "why am I getting 429 errors?"
