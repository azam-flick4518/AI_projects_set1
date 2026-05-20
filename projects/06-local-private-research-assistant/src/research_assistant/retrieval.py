from __future__ import annotations

import re

from research_assistant.models import Chunk, RetrievedChunk


TOKEN_PATTERN = re.compile(r"[a-z0-9][a-z0-9-]*")
STOPWORDS = {"a", "an", "and", "are", "for", "in", "is", "of", "on", "the", "to", "what"}


def tokenize(value: str) -> set[str]:
    return {
        token
        for token in TOKEN_PATTERN.findall(value.lower())
        if token not in STOPWORDS and len(token) > 1
    }


class ResearchRetriever:
    def __init__(self, chunks: list[Chunk]) -> None:
        self.chunks = chunks

    def retrieve(self, question: str, limit: int = 5) -> list[RetrievedChunk]:
        query_terms = tokenize(question)
        results = []
        for chunk in self.chunks:
            chunk_terms = tokenize(" ".join([chunk.title, chunk.text]))
            matches = sorted(query_terms & chunk_terms)
            if matches:
                score = len(matches) / max(len(query_terms), 1)
                results.append(RetrievedChunk(chunk=chunk, score=round(score, 3), matched_terms=matches))
        return sorted(results, key=lambda item: item.score, reverse=True)[:limit]
