from __future__ import annotations

from pathlib import Path

from research_assistant.loader import DocumentLoader
from research_assistant.memory import ResearchMemory
from research_assistant.models import Chunk, ResearchAnswer
from research_assistant.retrieval import ResearchRetriever
from research_assistant.synthesizer import DeterministicResearchSynthesizer, ResearchSynthesizer


class ResearchAssistantPipeline:
    def __init__(
        self,
        docs_path: str | Path,
        memory_path: str | Path,
        synthesizer: ResearchSynthesizer | None = None,
    ) -> None:
        self.loader = DocumentLoader()
        self.documents = self.loader.load_directory(docs_path)
        self.chunks: list[Chunk] = [
            chunk
            for document in self.documents
            for chunk in self.loader.chunk(document)
        ]
        self.retriever = ResearchRetriever(self.chunks)
        self.memory = ResearchMemory(memory_path)
        self.synthesizer = synthesizer or DeterministicResearchSynthesizer()

    def answer(self, question: str) -> ResearchAnswer:
        chunks = self.retriever.retrieve(question)
        memories = self.memory.search(question)
        return self.synthesizer.synthesize(question, chunks, memories)
