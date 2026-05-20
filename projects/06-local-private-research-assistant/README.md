# Local Private AI Research Assistant

A local-first research assistant that ingests notes and markdown documents, builds a searchable research index, answers questions with citations, and keeps a lightweight research memory log.

## What It Is For

Research work often spreads across papers, meeting notes, product docs, and personal observations. This project demonstrates a private assistant pattern where documents stay local, retrieval is explainable, and answers include citations instead of unsupported claims.

## AI Capabilities Demonstrated

- Local document ingestion
- Section chunking
- Keyword retrieval with citation tracking
- Research memory capture
- Grounded answer generation
- Browser UI for demos
- Deterministic local behavior for tests
- LLM-ready answer synthesis boundary

## Quick Start

### Run The Web UI

```powershell
cd C:\Dev\AI_5projects_set1\projects\06-local-private-research-assistant
$env:PYTHONPATH="src"
C:\Dev\AI_5projects_set1\.venv\Scripts\python.exe -m research_assistant.web --docs data/library --memory data/memory/research_memory.json
```

Then open:

```text
http://127.0.0.1:8765
```

The UI lets you ask a research question, optionally add a memory, and view the answer, citations, memories used, and assumptions.

### Run The CLI

```powershell
cd C:\Dev\AI_5projects_set1\projects\06-local-private-research-assistant
$env:PYTHONPATH="src"
C:\Dev\AI_5projects_set1\.venv\Scripts\python.exe -m research_assistant.cli --docs data/library --question "What should a local research assistant optimize for?"
```

To add a memory before answering:

```powershell
C:\Dev\AI_5projects_set1\.venv\Scripts\python.exe -m research_assistant.cli --docs data/library --question "What should a local research assistant optimize for?" --remember "Prefer privacy-first research tools with citations."
```

### Run Tests

```powershell
$env:PYTHONPATH="src"
C:\Dev\AI_5projects_set1\.venv\Scripts\python.exe -m unittest discover -s tests
```

## Production Fit

The local synthesizer is deterministic so the project is easy to run and test. In production, `LLMResearchSynthesizer` can call a model with the retrieved chunks, memory context, and citation constraints. The model should answer only from supplied context and return citations for each claim.
