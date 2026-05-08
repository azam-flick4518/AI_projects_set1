from __future__ import annotations

import argparse
import json
from dataclasses import asdict

from agent_orchestrator.loader import load_workflow
from agent_orchestrator.orchestrator import WorkflowOrchestrator


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run a local multi-agent workflow.")
    parser.add_argument("--workflow", required=True, help="Path to workflow JSON.")
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    report = WorkflowOrchestrator().run(load_workflow(args.workflow))
    if args.format == "json":
        print(json.dumps(asdict(report), indent=2))
    else:
        print(report.to_markdown())


if __name__ == "__main__":
    main()
