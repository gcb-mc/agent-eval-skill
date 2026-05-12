#!/usr/bin/env python3
"""
Generate an evaluation dataset from agents.yaml configuration.

Usage:
    python _test_pack/create_dataset.py
    python _test_pack/create_dataset.py --config path/to/agents.yaml
    python _test_pack/create_dataset.py --rows 10
"""

import argparse
import json
import yaml
import sys
from pathlib import Path


def find_repo_root() -> Path:
    """Find repo root by looking for agents.yaml or .git"""
    cwd = Path.cwd()
    for p in [cwd, cwd.parent]:
        if (p / "agents.yaml").exists() or (p / ".git").exists():
            return p
    return cwd


def generate_rows_for_agent(agent_name: str, agent_info: dict, num_rows: int) -> list[dict]:
    """
    Generate template eval rows for a single agent.
    These are TEMPLATE rows — users should customize with real test cases.
    """
    role = agent_info.get("role", "assistant")
    description = agent_info.get("description", "")
    input_type = agent_info.get("input_type", "text")
    output_type = agent_info.get("output_type", "response")
    sample = agent_info.get("sample_prompt", "")

    rows = []

    # Always include the sample prompt if provided
    if sample:
        rows.append({
            "query": sample,
            "context": f"Testing {agent_name} ({role}): {description}",
            "ground_truth": f"[TODO: Add expected {output_type} for this query]",
            "target_agent": agent_name,
        })

    # Generate template rows based on agent role and input type
    templates = _get_templates(role, input_type, output_type, agent_name)

    for i, tmpl in enumerate(templates):
        if len(rows) >= num_rows:
            break
        rows.append(tmpl)

    # Pad with generic rows if needed
    while len(rows) < num_rows:
        idx = len(rows) + 1
        rows.append({
            "query": f"[TODO: Test case {idx} for {agent_name}] — describe a realistic {input_type} input",
            "context": f"Context for test case {idx}. Provide relevant background information.",
            "ground_truth": f"[TODO: Expected {output_type} for test case {idx}]",
            "target_agent": agent_name,
        })

    return rows[:num_rows]


def _get_templates(role: str, input_type: str, output_type: str, agent_name: str) -> list[dict]:
    """Return role-appropriate template rows."""

    role_templates = {
        "summarizer": [
            {"query": "Please summarize the following document in 3-5 key points.", "context": "A multi-page document about quarterly performance.", "ground_truth": "[TODO: Expected summary points]"},
            {"query": "What are the main takeaways from this report?", "context": "An annual review document.", "ground_truth": "[TODO: Expected takeaways]"},
            {"query": "Condense this information into an executive briefing.", "context": "Detailed technical specification document.", "ground_truth": "[TODO: Expected briefing]"},
            {"query": "Summarize the action items from this meeting.", "context": "Meeting transcript with multiple discussion topics.", "ground_truth": "[TODO: Expected action items]"},
        ],
        "clarifier": [
            {"query": "I need help with my account.", "context": "Ambiguous request that could mean billing, settings, or access.", "ground_truth": "[TODO: Expected clarifying questions]"},
            {"query": "The system is not working.", "context": "Vague error report with no details.", "ground_truth": "[TODO: Expected diagnostic questions]"},
            {"query": "Can you update the thing?", "context": "Unclear reference to 'the thing'.", "ground_truth": "[TODO: Expected clarifying response]"},
            {"query": "I want to change my plan.", "context": "Could refer to subscription, project, or schedule.", "ground_truth": "[TODO: Expected clarification]"},
        ],
        "reporter": [
            {"query": "Generate a status report for this project.", "context": "Project data with milestones, tasks, and timelines.", "ground_truth": "[TODO: Expected report format and content]"},
            {"query": "Create a weekly summary from these updates.", "context": "Collection of daily updates and metrics.", "ground_truth": "[TODO: Expected weekly summary]"},
            {"query": "Produce an analysis report on these trends.", "context": "Time-series data showing patterns.", "ground_truth": "[TODO: Expected trend analysis]"},
            {"query": "Write a findings report based on this investigation.", "context": "Investigation notes and evidence.", "ground_truth": "[TODO: Expected findings report]"},
        ],
        "responder": [
            {"query": "How do I reset my password?", "context": "User account management system.", "ground_truth": "[TODO: Expected step-by-step instructions]"},
            {"query": "What are your business hours?", "context": "Customer service for a retail company.", "ground_truth": "[TODO: Expected business hours response]"},
            {"query": "I'd like a refund for my recent purchase.", "context": "E-commerce platform with 30-day return policy.", "ground_truth": "[TODO: Expected refund process response]"},
            {"query": "Can I upgrade my subscription?", "context": "SaaS platform with multiple tiers.", "ground_truth": "[TODO: Expected upgrade options]"},
        ],
        "reviewer": [
            {"query": "Review this code change for potential issues.", "context": "A pull request diff modifying authentication logic.", "ground_truth": "[TODO: Expected review comments]"},
            {"query": "Check this configuration for security concerns.", "context": "Infrastructure-as-code template.", "ground_truth": "[TODO: Expected security findings]"},
            {"query": "Evaluate this API design for best practices.", "context": "REST API specification document.", "ground_truth": "[TODO: Expected design feedback]"},
            {"query": "Review this documentation for accuracy.", "context": "Technical documentation draft.", "ground_truth": "[TODO: Expected accuracy feedback]"},
        ],
        "advisor": [
            {"query": "What product would you recommend for my needs?", "context": "Customer looking for a mid-range solution.", "ground_truth": "[TODO: Expected product recommendation]"},
            {"query": "Which plan is best for a small team?", "context": "Team of 5-10 people, moderate usage.", "ground_truth": "[TODO: Expected plan recommendation]"},
            {"query": "Should I upgrade or stay on my current plan?", "context": "Current usage patterns and growth trajectory.", "ground_truth": "[TODO: Expected advice]"},
            {"query": "What's the best approach for this scenario?", "context": "Complex decision with multiple trade-offs.", "ground_truth": "[TODO: Expected strategic advice]"},
        ],
        "analyst": [
            {"query": "What trends do you see in this data?", "context": "Time-series dataset with seasonal patterns.", "ground_truth": "[TODO: Expected trend analysis]"},
            {"query": "Identify anomalies in these metrics.", "context": "Performance metrics with some outliers.", "ground_truth": "[TODO: Expected anomaly report]"},
            {"query": "Compare these two datasets and highlight differences.", "context": "Two related datasets from different time periods.", "ground_truth": "[TODO: Expected comparison analysis]"},
            {"query": "What insights can you extract from this information?", "context": "Mixed qualitative and quantitative data.", "ground_truth": "[TODO: Expected insights]"},
        ],
    }

    # Get role-specific templates or fall back to generic
    templates = role_templates.get(role, [])

    if not templates:
        templates = [
            {"query": f"Process this {input_type} and provide a {output_type}.", "context": f"Test context for {agent_name}.", "ground_truth": f"[TODO: Expected {output_type}]"},
            {"query": f"Given the following {input_type}, what is your {output_type}?", "context": f"Additional context for {agent_name} evaluation.", "ground_truth": f"[TODO: Expected {output_type}]"},
            {"query": f"Analyze this {input_type} and respond with a detailed {output_type}.", "context": f"Comprehensive test context for {agent_name}.", "ground_truth": f"[TODO: Expected {output_type}]"},
            {"query": f"Handle this {input_type} request appropriately.", "context": f"Realistic scenario for {agent_name}.", "ground_truth": f"[TODO: Expected {output_type}]"},
        ]

    # Add target_agent to all templates
    for t in templates:
        t["target_agent"] = agent_name

    return templates


def main():
    parser = argparse.ArgumentParser(description="Generate eval dataset from agents.yaml")
    parser.add_argument("--config", type=str, help="Path to agents.yaml (default: repo_root/agents.yaml)")
    parser.add_argument("--rows", type=int, help="Rows per agent (overrides agents.yaml setting)")
    parser.add_argument("--output", type=str, help="Output path (overrides agents.yaml setting)")
    args = parser.parse_args()

    repo_root = find_repo_root()
    config_path = Path(args.config) if args.config else repo_root / "agents.yaml"

    if not config_path.exists():
        print(f"❌ Config not found: {config_path}")
        print("   Copy agents.yaml.template to agents.yaml and fill in your agents.")
        sys.exit(1)

    with open(config_path) as f:
        config = yaml.safe_load(f)

    agents = config.get("agents", {})
    if not agents:
        print("❌ No agents defined in agents.yaml")
        sys.exit(1)

    rows_per_agent = args.rows or config.get("dataset", {}).get("rows_per_agent", 5)
    output_path = Path(args.output) if args.output else repo_root / config.get("dataset", {}).get("path", "eval_dataset.jsonl")

    print(f"📋 Generating dataset for {len(agents)} agents ({rows_per_agent} rows each)")

    all_rows = []
    for agent_name, agent_info in agents.items():
        rows = generate_rows_for_agent(agent_name, agent_info, rows_per_agent)
        all_rows.extend(rows)
        print(f"   ✅ {agent_name} ({agent_info.get('role', '?')}): {len(rows)} rows")

    with open(output_path, "w") as f:
        for row in all_rows:
            f.write(json.dumps(row) + "\n")

    print(f"\n✅ Dataset written to {output_path} ({len(all_rows)} total rows)")
    print(f"   ⚠️  Review and customize the [TODO] entries with real test cases!")


if __name__ == "__main__":
    main()
