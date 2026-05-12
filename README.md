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
jupyter notebook notebooks/starter_eval.ipynb
```

That's it. The starter notebook reads `agents.yaml` and evaluates whatever agents you defined.

See **[QUICKSTART.md](QUICKSTART.md)** for the full walkthrough.

---

## 🎯 How It Works

```
agents.yaml          →  create_dataset.py  →  eval_dataset.jsonl
(your agents)           (generates test data)

eval_dataset.jsonl   →  starter_eval.ipynb  →  Phase 1: call agents → responses
                                             →  Phase 2: evaluate() → scores
                                             →  Dashboard + export
```

1. **`agents.yaml`** — Single config file where you describe your agents (names, roles, descriptions, sample prompts)
2. **`create_dataset.py`** — Auto-generates evaluation JSONL with role-appropriate test cases
3. **`starter_eval.ipynb`** — Config-driven notebook that evaluates any agents with 7 Azure AI evaluators
4. **Results** — Per-agent dashboard, CSV/JSON export, cached responses for re-runs

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
│   └── starter_eval.ipynb        # ← MAIN NOTEBOOK: config-driven, works with any agents
├── _test_pack/
│   ├── create_dataset.py         # generates eval JSONL from agents.yaml
│   └── eval_dataset_template.jsonl
├── .copilot/skills/              # 6 Copilot skills (auto-discovered)
├── examples/
│   ├── financial-agents/         # example: document summarization agents (v1-v4)
│   └── azure-vm-agents/         # example: Azure infra management agents
├── docs/                         # evaluation guide, walkthrough, talking points
├── .env.template
├── requirements.txt
└── README.md
```

---

## 📓 Notebooks

| Notebook | Location | Purpose |
|----------|----------|---------|
| **`starter_eval.ipynb`** | `notebooks/` | **Start here** — reads `agents.yaml`, evaluates any agents, generates dashboard |
| Financial agents (v1–v4) | `examples/financial-agents/` | Reference: document summarization evaluation evolution |
| Azure VM agents | `examples/azure-vm-agents/` | Reference: infra agent evaluation with RBAC + tool checks |

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
| [EVALUATION_GUIDE.md](docs/EVALUATION_GUIDE.md) | Detailed explanation of the evaluation pipeline |
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
