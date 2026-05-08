from __future__ import annotations

import re
from typing import Protocol

from kg_rag.models import Answer, GraphFact, RetrievedChunk


class AnswerSynthesizer(Protocol):
    def synthesize(
        self,
        question: str,
        chunks: list[RetrievedChunk],
        graph_facts: list[GraphFact],
    ) -> Answer:
        """Create a cited answer from retrieved chunks and graph facts."""


class DeterministicAnswerSynthesizer:
    def synthesize(
        self,
        question: str,
        chunks: list[RetrievedChunk],
        graph_facts: list[GraphFact],
    ) -> Answer:
        question_terms = self._terms(question)
        target_dependencies = {
            fact.target.name.lower()
            for fact in graph_facts
            if fact.relationship == "depends_on" and fact.target.name.lower() in question_terms
        }
        dependents = sorted(
            {
                fact.source.name
                for fact in graph_facts
                if fact.relationship == "depends_on"
                and (not target_dependencies or fact.target.name.lower() in target_dependencies)
            }
        )
        policies = sorted(
            {
                fact.target.name
                for fact in graph_facts
                if fact.relationship == "governed_by"
            }
        )

        parts = []
        if target_dependencies and dependents:
            parts.append(
                f"Services that depend on {', '.join(sorted(target_dependencies))}: "
                f"{', '.join(dependents)}."
            )
        elif dependents:
            parts.append(f"Services with dependency relationships: {', '.join(dependents)}.")
        if policies:
            parts.append(f"Policies found: {', '.join(policies)}.")
        if not parts and chunks:
            parts.append(self._fallback_summary(chunks))
        if not parts:
            parts.append("No supported answer was found in the retrieved knowledge base.")

        citations = []
        for item in chunks:
            citation = f"{item.chunk.source_path}#{item.chunk.id} ({item.chunk.title})"
            if citation not in citations:
                citations.append(citation)

        return Answer(
            question=question,
            summary=" ".join(parts),
            citations=citations,
            graph_facts=graph_facts,
            assumptions=[
                "The local demo uses deterministic keyword and graph retrieval.",
                "The answer is limited to retrieved chunks and extracted graph facts.",
                "A production LLM should preserve citations and reject unsupported claims.",
            ],
        )

    def _fallback_summary(self, chunks: list[RetrievedChunk]) -> str:
        top = chunks[0].chunk
        first_line = next((line.strip() for line in top.text.splitlines() if line.strip()), top.title)
        return f"Most relevant source is {top.title}: {first_line}"

    def _terms(self, value: str) -> set[str]:
        return set(re.findall(r"[a-z0-9][a-z0-9-]*", value.lower()))


class LLMAnswerSynthesizer:
    def __init__(self, model_name: str) -> None:
        self.model_name = model_name

    def synthesize(
        self,
        question: str,
        chunks: list[RetrievedChunk],
        graph_facts: list[GraphFact],
    ) -> Answer:
        prompt_package = self.build_prompt_package(question, chunks, graph_facts)
        raise NotImplementedError(
            "Connect this boundary to an LLM provider, parse the structured answer, "
            f"and validate citations against {len(prompt_package['chunks'])} retrieved chunks."
        )

    def build_prompt_package(
        self,
        question: str,
        chunks: list[RetrievedChunk],
        graph_facts: list[GraphFact],
    ) -> dict[str, object]:
        return {
            "model": self.model_name,
            "task": "Answer the question using only the supplied chunks and graph facts.",
            "question": question,
            "constraints": [
                "Do not use outside knowledge.",
                "Cite every claim with a source chunk.",
                "Use graph facts to connect systems, teams, policies, and data.",
                "Say when the retrieved context is insufficient.",
                "Return a response matching the Answer schema.",
            ],
            "chunks": [
                {
                    "id": item.chunk.id,
                    "title": item.chunk.title,
                    "source_path": item.chunk.source_path,
                    "score": item.score,
                    "text": item.chunk.text,
                }
                for item in chunks
            ],
            "graph_facts": [
                {
                    "source": fact.source.name,
                    "relationship": fact.relationship,
                    "target": fact.target.name,
                    "evidence": fact.evidence,
                    "document_id": fact.document_id,
                }
                for fact in graph_facts
            ],
        }
