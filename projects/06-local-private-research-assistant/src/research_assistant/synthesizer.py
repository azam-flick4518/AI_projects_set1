from __future__ import annotations

from typing import Protocol

from research_assistant.models import MemoryEntry, ResearchAnswer, RetrievedChunk


class ResearchSynthesizer(Protocol):
    def synthesize(
        self,
        question: str,
        chunks: list[RetrievedChunk],
        memories: list[MemoryEntry],
    ) -> ResearchAnswer:
        """Create a grounded research answer from retrieved context."""


class DeterministicResearchSynthesizer:
    def synthesize(
        self,
        question: str,
        chunks: list[RetrievedChunk],
        memories: list[MemoryEntry],
    ) -> ResearchAnswer:
        if chunks:
            key_points = [self._first_sentence(item.chunk.text) for item in chunks[:3]]
            answer = " ".join(point for point in key_points if point)
        else:
            answer = "No supported answer was found in the local research library."

        if memories:
            answer += " Relevant research memory: " + " ".join(memory.text for memory in memories[:2])

        citations = [
            f"{item.chunk.source_path}#{item.chunk.id} ({item.chunk.title})"
            for item in chunks
        ]
        return ResearchAnswer(
            question=question,
            answer=answer,
            citations=citations,
            memories_used=[memory.id for memory in memories],
            assumptions=[
                "The local demo uses deterministic keyword retrieval.",
                "Answers are limited to retrieved document chunks and stored memories.",
                "A production LLM should preserve citations and reject unsupported claims.",
            ],
        )

    def _first_sentence(self, text: str) -> str:
        cleaned = " ".join(line.strip() for line in text.splitlines() if line.strip() and not line.startswith("#"))
        return cleaned.split(". ")[0].strip() + "." if cleaned else ""


class LLMResearchSynthesizer:
    def __init__(self, model_name: str) -> None:
        self.model_name = model_name

    def synthesize(
        self,
        question: str,
        chunks: list[RetrievedChunk],
        memories: list[MemoryEntry],
    ) -> ResearchAnswer:
        prompt_package = self.build_prompt_package(question, chunks, memories)
        raise NotImplementedError(
            "Connect this boundary to an LLM provider and validate citations against "
            f"{len(prompt_package['chunks'])} retrieved chunks."
        )

    def build_prompt_package(
        self,
        question: str,
        chunks: list[RetrievedChunk],
        memories: list[MemoryEntry],
    ) -> dict[str, object]:
        return {
            "model": self.model_name,
            "task": "Answer the research question using only supplied chunks and memories.",
            "question": question,
            "constraints": [
                "Do not use outside knowledge.",
                "Cite each factual claim with a source chunk.",
                "Use memories only as user/project context.",
                "Say when context is insufficient.",
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
            "memories": [memory.__dict__ for memory in memories],
        }
