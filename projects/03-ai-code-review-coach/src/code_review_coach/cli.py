from __future__ import annotations

import argparse
import json
from dataclasses import asdict

from code_review_coach.pipeline import CodeReviewPipeline


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run a local AI-ready code review coach.")
    parser.add_argument("--repo", required=True, help="Path to repository or code folder to review.")
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    report = CodeReviewPipeline().review(args.repo)
    if args.format == "json":
        print(json.dumps(asdict(report), indent=2))
    else:
        print(report.to_markdown())


if __name__ == "__main__":
    main()
