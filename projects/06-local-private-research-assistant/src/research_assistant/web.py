from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from research_assistant.pipeline import ResearchAssistantPipeline


PROJECT_ROOT = Path(__file__).resolve().parents[2]
STATIC_ROOT = PROJECT_ROOT / "web"


class ResearchAssistantHandler(BaseHTTPRequestHandler):
    docs_path: Path
    memory_path: Path

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/":
            self._serve_static("index.html", "text/html; charset=utf-8")
            return
        if parsed.path == "/app.css":
            self._serve_static("app.css", "text/css; charset=utf-8")
            return
        if parsed.path == "/app.js":
            self._serve_static("app.js", "text/javascript; charset=utf-8")
            return
        if parsed.path == "/api/answer":
            query = parse_qs(parsed.query)
            question = query.get("question", [""])[0].strip()
            remember = query.get("remember", [""])[0].strip()
            self._answer(question, remember)
            return
        self.send_error(HTTPStatus.NOT_FOUND, "Not found")

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path != "/api/answer":
            self.send_error(HTTPStatus.NOT_FOUND, "Not found")
            return
        content_length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(content_length).decode("utf-8")
        payload = json.loads(body or "{}")
        self._answer(str(payload.get("question", "")).strip(), str(payload.get("remember", "")).strip())

    def _answer(self, question: str, remember: str) -> None:
        if not question:
            self._json({"error": "Question is required."}, status=HTTPStatus.BAD_REQUEST)
            return

        pipeline = ResearchAssistantPipeline(self.docs_path, self.memory_path)
        if remember:
            pipeline.memory.add(remember, tags=["ui", "research"])
        answer = pipeline.answer(question)
        self._json(asdict(answer))

    def _serve_static(self, filename: str, content_type: str) -> None:
        path = STATIC_ROOT / filename
        if not path.exists():
            self.send_error(HTTPStatus.NOT_FOUND, "Static file not found")
            return
        payload = path.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def _json(self, payload: dict[str, object], status: HTTPStatus = HTTPStatus.OK) -> None:
        encoded = json.dumps(payload, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def log_message(self, format: str, *args: object) -> None:
        return


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the local private research assistant web UI.")
    parser.add_argument("--docs", default="data/library", help="Directory containing markdown research docs.")
    parser.add_argument("--memory", default="data/memory/research_memory.json", help="Path to memory JSON.")
    parser.add_argument("--host", default="127.0.0.1", help="Host for the local server.")
    parser.add_argument("--port", type=int, default=8765, help="Port for the local server.")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    ResearchAssistantHandler.docs_path = Path(args.docs)
    ResearchAssistantHandler.memory_path = Path(args.memory)
    server = ThreadingHTTPServer((args.host, args.port), ResearchAssistantHandler)
    print(f"Research assistant UI running at http://{args.host}:{args.port}")
    print("Press Ctrl+C to stop.")
    server.serve_forever()


if __name__ == "__main__":
    main()
