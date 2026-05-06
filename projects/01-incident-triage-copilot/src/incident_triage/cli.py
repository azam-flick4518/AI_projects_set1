from __future__ import annotations

import argparse
import json
from dataclasses import asdict

from incident_triage.io import load_alert, load_deploys, load_logs, load_runbooks
from incident_triage.triage import TriageEngine


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate an evidence-backed incident triage report.")
    parser.add_argument("--alert", required=True, help="Path to alert JSON.")
    parser.add_argument("--logs", required=True, help="Path to log events JSON.")
    parser.add_argument("--runbooks", required=True, help="Path to runbooks JSON.")
    parser.add_argument("--deploys", required=True, help="Path to deploy events JSON.")
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    alert = load_alert(args.alert)
    engine = TriageEngine(
        logs=load_logs(args.logs),
        runbooks=load_runbooks(args.runbooks),
        deploys=load_deploys(args.deploys),
    )
    report = engine.triage(alert)

    if args.format == "json":
        print(json.dumps(asdict(report), indent=2))
    else:
        print(report.to_markdown())


if __name__ == "__main__":
    main()
