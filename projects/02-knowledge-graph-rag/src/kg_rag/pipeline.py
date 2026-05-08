from __future__ import annotations

from pathlib import Path

from kg_rag.graph import KnowledgeGraphBuilder
from kg_rag.loader import DocumentLoader
from kg_rag.models import Answer, Chunk
from kg_rag.retrieval import GraphRetriever
from kg_rag.synthesizer import AnswerSynthesizer, DeterministicAnswerSynthesizer


class KnowledgeGraphRagPipeline:
    def __init__(self, docs_path: str | Path, synthesizer: AnswerSynthesizer | None = None) -> None:
        self.loader = DocumentLoader()
        self.documents = self.loader.load_directory(docs_path)
        self.chunks: list[Chunk] = [
            chunk
            for document in self.documents
            for chunk in self.loader.chunk(document)
        ]
        self.graph = KnowledgeGraphBuilder().build(self.documents)
        self.retriever = GraphRetriever(self.chunks, self.graph)
        self.synthesizer = synthesizer or DeterministicAnswerSynthesizer()

    def answer(self, question: str) -> Answer:
        chunks, graph_facts = self.retriever.retrieve(question)
        return self.synthesizer.synthesize(question, chunks, graph_facts)
