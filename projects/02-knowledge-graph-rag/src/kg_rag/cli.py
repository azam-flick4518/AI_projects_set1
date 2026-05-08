from __future__ import annotations

import argparse
import json
from dataclasses import asdict

from kg_rag.pipeline import KnowledgeGraphRagPipeline


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run graph-aware retrieval over local markdown docs.")
    parser.add_argument("--docs", required=True, help="Directory containing markdown documents.")
    parser.add_argument("--query", required=True, help="Question to answer.")
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    answer = KnowledgeGraphRagPipeline(args.docs).answer(args.query)
    if args.format == "json":
        print(json.dumps(asdict(answer), indent=2))
    else:
        print(answer.to_markdown())


if __name__ == "__main__":
    main()
