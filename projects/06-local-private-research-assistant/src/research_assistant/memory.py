from __future__ import annotations

import json
from pathlib import Path

from research_assistant.models import MemoryEntry
from research_assistant.retrieval import tokenize


class ResearchMemory:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.entries = self._load()

    def add(self, text: str, tags: list[str]) -> MemoryEntry:
        entry = MemoryEntry(id=f"mem-{len(self.entries) + 1}", text=text, tags=tags)
        self.entries.append(entry)
        self._save()
        return entry

    def search(self, query: str, limit: int = 3) -> list[MemoryEntry]:
        query_terms = tokenize(query)
        scored = []
        for entry in self.entries:
            terms = tokenize(" ".join([entry.text, *entry.tags]))
            score = len(query_terms & terms)
            if score:
                scored.append((score, entry))
        return [entry for _, entry in sorted(scored, key=lambda item: item[0], reverse=True)[:limit]]

    def _load(self) -> list[MemoryEntry]:
        if not self.path.exists():
            return []
        payload = json.loads(self.path.read_text(encoding="utf-8"))
        return [MemoryEntry(id=item["id"], text=item["text"], tags=item.get("tags", [])) for item in payload]

    def _save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = [entry.__dict__ for entry in self.entries]
        self.path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
