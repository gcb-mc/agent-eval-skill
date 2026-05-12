# 🧪 Agent Eval Skill

A **GitHub Copilot agent skill** for evaluating **any** multi-agent AI system on Azure AI Foundry. Describe your agents in `agents.yaml`, and this repo gives you everything: evaluation notebooks, test data generation, SDK patterns, and troubleshooting — all driven by your config.

> Inspired by [bradygaster/squad](https://github.com/bradygaster/squad)'s skill-per-folder pattern.

---

## 🚀 Quick Start (5 steps)

```bash
# 1. Clone & install
git clone https://github.com/gcb-mc/agent-eval-skill.git
cd agent-eval-skill
pip install -r requirements.txt

# 2. Configure your agents
cp agents.yaml.template agents.yaml    # ← describe YOUR agents here
cp .env.template .env                  # ← add your Azure endpoints

# 3. Authenticate
az login

# 4. Generate test data
python _test_pack/create_dataset.py

# 5. Run the evaluation
jupyter notebook notebooks/test_my_agents_v4.ipynb
```

That's it. The notebook reads `agents.yaml` and evaluates whatever agents you defined.

> **Note:** `agents.yaml` integration is planned but not yet wired into the notebook. Currently, edit Section 0 (Configuration) in the notebook to point to your agents. See [QUICKSTART.md](QUICKSTART.md) for details.

See **[QUICKSTART.md](QUICKSTART.md)** for the full walkthrough.

---

## 🎯 Two-Notebook Evaluation Journey

This repo provides **two complementary notebooks** — use them in sequence for full coverage:

### Step 1: Can It Run? → `multi_agent_evaluation.ipynb`

The **exploration and readiness** notebook. Use this first to validate that your agents, infrastructure, and tooling actually work before measuring quality.

```
✅ Infrastructure checks    — Is the agent registered? Is the image deployed?
✅ RBAC validation          — Does the managed identity have the right roles?
✅ Tool connectivity        — Can each agent's tools reach their backend APIs?
✅ Agent routing            — Does the orchestrator pick the right specialist?
✅ End-to-end execution     — Full pipeline with live Azure API calls
✅ Cross-agent handoff      — Do multi-agent prompts route correctly?
```

📍 Located at: `examples/azure-vm-agents/multi_agent_evaluation.ipynb`

### Step 2: How Well Does It Run? → `test_my_agents_v4.ipynb`

The **quality evaluation** notebook. Once your agents are running, use this to measure response quality with structured, repeatable scoring and dashboards.

```
📊 7 Azure AI evaluators   — Groundedness, Relevance, Coherence, Fluency,
                              TaskAdherence, IntentResolution, ResponseCompleteness
📊 Two-phase approach      — Phase 1: collect responses → Phase 2: score with evaluate()
📊 36 test cases           — 24 standard + 12 edge cases (prompt injection, ambiguity, etc.)
📊 Dashboard & export      — Heatmaps, standard vs edge comparison, CSV/JSON export
```

📍 Located at: `notebooks/test_my_agents_v4.ipynb`

---

## 📓 Notebooks

| Notebook | Location | Purpose | When to Use |
|----------|----------|---------|-------------|
| `multi_agent_evaluation.ipynb` | `examples/azure-vm-agents/` | **Can it run?** — infra, RBAC, routing, tool connectivity, E2E | First — validate the plumbing works |
| **`test_my_agents_v4.ipynb`** | `notebooks/` | **How well does it run?** — 7 evaluators, dashboards, export | Second — measure and improve quality |

---

## 📦 Skills (for Copilot CLI)

Install as a Copilot skill by copying `.copilot/skills/` into your project, or clone this repo directly.

| Skill | What it teaches Copilot |
|-------|------------------------|
| **[scaffold-eval](.copilot/skills/scaffold-eval/SKILL.md)** | How to scaffold evaluation for ANY agents — `agents.yaml` workflow, dataset generation, result interpretation |
| **[multi-agent-eval](.copilot/skills/multi-agent-eval/SKILL.md)** | Multi-agent evaluation architecture — routing, tool selection, E2E, handoff detection |
| **[eval-sdk-patterns](.copilot/skills/eval-sdk-patterns/SKILL.md)** | Azure AI Evaluation SDK — 7 evaluators, batch `evaluate()`, two-phase approach |
| **[foundry-agent-patterns](.copilot/skills/foundry-agent-patterns/SKILL.md)** | How to call Foundry agents — `responses.create` + `agent_reference` pattern |
| **[eval-troubleshooting](.copilot/skills/eval-troubleshooting/SKILL.md)** | Rate limits, content filters, column mapping gotchas, common fixes |
| **[agent-observability](.copilot/skills/agent-observability/SKILL.md)** | Microsoft's 5 observability best practices |

---

## 📁 Repo Structure

```
agent-eval-skill/
├── agents.yaml.template          # ← YOUR CONFIG: describe your agents here
├── notebooks/
│   └── test_my_agents_v4.ipynb   # ← QUALITY EVAL: 7 evaluators + dashboards
├── _test_pack/
│   ├── create_dataset.py         # generates eval JSONL from agents.yaml
│   └── eval_dataset_template.jsonl
├── .copilot/skills/              # 6 Copilot skills (auto-discovered)
├── examples/
│   ├── financial-agents/         # example: test data + results for financial agents
│   └── azure-vm-agents/         # ← READINESS EVAL: infra + RBAC + routing checks
│       └── multi_agent_evaluation.ipynb
├── docs/                         # evaluation guide, walkthrough, talking points
├── .env.template
├── requirements.txt
└── README.md
```

---

## 🏗️ Two-Phase Evaluation Pattern

```
Phase 1: Call agents → save responses to JSONL     (slow, rate-limited, resumable)
Phase 2: Run evaluate() on saved JSONL → scores    (fast, deterministic, retryable)
```

Phase 1 results are saved incrementally to JSONL. Re-runs automatically resume from where they left off, skipping rows that already have responses.

### Conditional Clarification

For multi-agent pipelines with a clarification step, the evaluation automatically skips clarification for straightforward queries. Only edge cases that benefit from clarification (ambiguous queries, contradictory data, etc.) trigger the full pipeline. This saves API calls and better reflects real-world usage.

### 7 Built-In Evaluators

| Evaluator | Type | Score Range |
|-----------|------|------------|
| Groundedness | Quality | 1–5 |
| Relevance | Quality | 1–5 |
| Coherence | Quality | 1–5 |
| Fluency | Quality | 1–5 |
| TaskAdherence | Agentic | 1–5 |
| IntentResolution | Agentic | 1–5 |
| ResponseCompleteness | Agentic | 1–5 |

Toggle evaluators on/off in `agents.yaml` → `evaluators` section.

---

## 📚 Docs

| Document | Description |
|----------|-------------|
| [QUICKSTART.md](QUICKSTART.md) | Step-by-step bring-your-own-agents guide |
| [EVALUATION_GUIDE.md](docs/EVALUATION_GUIDE.md) | Detailed explanation of the v4 evaluation pipeline |
| [Walkthrough](docs/walkthrough_agent_evaluation_updates.md) | Talk-through of v1→v4 evolution and key patterns |
| [CSA Talking Points](docs/csa-talking-points.md) | Cloud Solution Architect guide for customer conversations |

---

## 🔧 Requirements

- Python 3.10+
- Azure CLI (`az login`)
- Azure subscription with AI Foundry project
- Foundry-hosted agents (any domain)
- `pip install -r requirements.txt`

---

## 📄 License

MIT — see [LICENSE](LICENSE)
