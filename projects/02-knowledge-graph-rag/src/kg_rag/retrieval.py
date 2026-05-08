from __future__ import annotations

import re

from kg_rag.graph import KnowledgeGraph
from kg_rag.models import Chunk, GraphFact, RetrievedChunk


TOKEN_PATTERN = re.compile(r"[a-z0-9][a-z0-9-]*")
STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "for",
    "how",
    "is",
    "of",
    "on",
    "the",
    "to",
    "what",
    "which",
}


def tokenize(value: str) -> set[str]:
    return {
        token
        for token in TOKEN_PATTERN.findall(value.lower())
        if token not in STOPWORDS and len(token) > 1
    }


class GraphRetriever:
    def __init__(self, chunks: list[Chunk], graph: KnowledgeGraph) -> None:
        self.chunks = chunks
        self.graph = graph

    def retrieve(self, question: str, limit: int = 5) -> tuple[list[RetrievedChunk], list[GraphFact]]:
        query_terms = tokenize(question)
        graph_facts = self.graph.facts_for_terms(query_terms)
        expanded_terms = query_terms | tokenize(" ".join(self.graph.related_entity_names(query_terms)))

        scored = []
        for chunk in self.chunks:
            chunk_terms = tokenize(" ".join([chunk.title, chunk.text]))
            matches = sorted(expanded_terms & chunk_terms)
            if not matches:
                continue
            base_score = len(matches) / max(len(query_terms), 1)
            citation_boost = 0.25 if chunk.document_id in {fact.document_id for fact in graph_facts} else 0.0
            scored.append(
                RetrievedChunk(
                    chunk=chunk,
                    score=round(min(1.0, base_score + citation_boost), 3),
                    matched_terms=matches,
                )
            )

        return sorted(scored, key=lambda item: item.score, reverse=True)[:limit], graph_facts
