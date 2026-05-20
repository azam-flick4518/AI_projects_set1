from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Document:
    id: str
    path: str
    title: str
    text: str


@dataclass(frozen=True)
class Chunk:
    id: str
    document_id: str
    source_path: str
    title: str
    text: str


@dataclass(frozen=True)
class RetrievedChunk:
    chunk: Chunk
    score: float
    matched_terms: list[str]


@dataclass(frozen=True)
class MemoryEntry:
    id: str
    text: str
    tags: list[str]


@dataclass(frozen=True)
class ResearchAnswer:
    question: str
    answer: str
    citations: list[str]
    memories_used: list[str]
    assumptions: list[str]

    def to_markdown(self) -> str:
        lines = [
            "# Research Assistant Answer",
            "",
            f"Question: {self.question}",
            "",
            "## Answer",
            "",
            self.answer,
            "",
            "## Citations",
            "",
        ]
        lines.extend(f"- {citation}" for citation in self.citations)
        lines.extend(["", "## Memories Used", ""])
        if self.memories_used:
            lines.extend(f"- {memory}" for memory in self.memories_used)
        else:
            lines.append("- None")
        lines.extend(["", "## Assumptions", ""])
        lines.extend(f"- {assumption}" for assumption in self.assumptions)
        return "\n".join(lines)
