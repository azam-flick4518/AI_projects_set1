from __future__ import annotations

import argparse
import json
from dataclasses import asdict

from eval_governance.evaluator import Evaluator
from eval_governance.loader import load_cases


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run local LLM evaluation and governance checks.")
    parser.add_argument("--cases", required=True, help="Path to eval cases JSON.")
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    report = Evaluator().run(load_cases(args.cases))
    if args.format == "json":
        print(json.dumps(asdict(report), indent=2))
    else:
        print(report.to_markdown())


if __name__ == "__main__":
    main()
