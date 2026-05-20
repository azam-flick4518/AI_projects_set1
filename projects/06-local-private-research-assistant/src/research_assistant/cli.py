from __future__ import annotations

import argparse
import json
from dataclasses import asdict

from research_assistant.pipeline import ResearchAssistantPipeline


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run a local private research assistant.")
    parser.add_argument("--docs", required=True, help="Directory containing markdown research docs.")
    parser.add_argument("--question", required=True, help="Research question to answer.")
    parser.add_argument("--memory", default="data/memory/research_memory.json", help="Path to memory JSON.")
    parser.add_argument("--remember", help="Optional memory text to store before answering.")
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    pipeline = ResearchAssistantPipeline(args.docs, args.memory)
    if args.remember:
        pipeline.memory.add(args.remember, tags=["cli", "research"])
    answer = pipeline.answer(args.question)
    if args.format == "json":
        print(json.dumps(asdict(answer), indent=2))
    else:
        print(answer.to_markdown())


if __name__ == "__main__":
    main()
