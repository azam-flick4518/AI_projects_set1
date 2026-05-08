from __future__ import annotations

from dataclasses import dataclass, field


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
class Entity:
    id: str
    name: str
    kind: str


@dataclass(frozen=True)
class Relationship:
    source: str
    target: str
    kind: str
    evidence: str
    document_id: str


@dataclass(frozen=True)
class GraphFact:
    source: Entity
    relationship: str
    target: Entity
    evidence: str
    document_id: str


@dataclass(frozen=True)
class RetrievedChunk:
    chunk: Chunk
    score: float
    matched_terms: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class Answer:
    question: str
    summary: str
    citations: list[str]
    graph_facts: list[GraphFact]
    assumptions: list[str]

    def to_markdown(self) -> str:
        lines = [
            "# Knowledge Graph RAG Answer",
            "",
            f"Question: {self.question}",
            "",
            "## Answer",
            "",
            self.summary,
            "",
            "## Graph Facts",
            "",
        ]
        lines.extend(
            f"- {fact.source.name} --{fact.relationship}--> {fact.target.name} "
            f"({fact.document_id})"
            for fact in self.graph_facts
        )
        lines.extend(["", "## Citations", ""])
        lines.extend(f"- {citation}" for citation in self.citations)
        lines.extend(["", "## Assumptions", ""])
        lines.extend(f"- {assumption}" for assumption in self.assumptions)
        return "\n".join(lines)
