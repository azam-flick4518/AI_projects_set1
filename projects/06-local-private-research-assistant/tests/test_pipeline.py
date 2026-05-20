import tempfile
import unittest
from pathlib import Path

from research_assistant.pipeline import ResearchAssistantPipeline
from research_assistant.synthesizer import LLMResearchSynthesizer


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class ResearchAssistantPipelineTests(unittest.TestCase):
    def test_answers_with_citations_and_memory(self) -> None:
        memory_path = PROJECT_ROOT / "data" / "memory" / "research_memory.json"
        pipeline = ResearchAssistantPipeline(PROJECT_ROOT / "data" / "library", memory_path)

        answer = pipeline.answer("What should a local research assistant optimize for?")

        self.assertIn("privacy", answer.answer.lower())
        self.assertGreaterEqual(len(answer.citations), 1)
        self.assertIn("mem-1", answer.memories_used)

    def test_memory_add_and_search(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            memory_path = Path(temp_dir) / "memory.json"
            pipeline = ResearchAssistantPipeline(PROJECT_ROOT / "data" / "library", memory_path)

            entry = pipeline.memory.add("Remember citation quality for research projects.", ["citations"])
            matches = pipeline.memory.search("citation quality")

            self.assertEqual(entry.id, "mem-1")
            self.assertEqual(matches[0].id, "mem-1")

    def test_llm_prompt_package_is_grounded(self) -> None:
        pipeline = ResearchAssistantPipeline(
            PROJECT_ROOT / "data" / "library",
            PROJECT_ROOT / "data" / "memory" / "research_memory.json",
        )
        chunks = pipeline.retriever.retrieve("privacy citations")
        memories = pipeline.memory.search("privacy")
        prompt = LLMResearchSynthesizer("production-model").build_prompt_package(
            "What matters for local research?",
            chunks,
            memories,
        )

        self.assertEqual(prompt["model"], "production-model")
        self.assertGreaterEqual(len(prompt["chunks"]), 1)
        self.assertTrue(any("Do not use outside knowledge" in item for item in prompt["constraints"]))


if __name__ == "__main__":
    unittest.main()
