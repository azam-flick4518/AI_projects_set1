# Enterprise Knowledge Graph RAG Platform

A local knowledge graph RAG project that ingests enterprise-style markdown documents, extracts entities and relationships, expands retrieval through the graph, and generates cited answers from grounded context.

The project is intentionally runnable without external services. It uses deterministic extraction and synthesis for local demos and tests, with a clean `LLMAnswerSynthesizer` boundary for production model calls.

## What It Is For

Enterprise teams often have policies, architecture notes, service docs, and ownership details spread across many places. Plain semantic search can miss important relationships, such as which service owns a system, which policy applies, or which dependency is involved.

This project demonstrates how graph-aware retrieval can improve RAG by connecting documents through entities and relationships before producing a cited answer.

## AI Capabilities Demonstrated

- Document ingestion and chunking
- Entity and relationship extraction
- Knowledge graph construction
- Graph-expanded retrieval
- Citation-backed answer generation
- Deterministic local synthesis for testing
- LLM-ready synthesis boundary for production
- Evaluation fixture for expected answer behavior

## Quick Start

From this project folder:

```powershell
$env:PYTHONPATH="src"
C:\Dev\AI_5projects_set1\.venv\Scripts\python.exe -m kg_rag.cli --docs data/corpus --query "Which services depend on payments-api and what policy applies to customer data?"
```

Run tests:

```powershell
$env:PYTHONPATH="src"
C:\Dev\AI_5projects_set1\.venv\Scripts\python.exe -m unittest discover -s tests
```

## Demo Question

```text
Which services depend on payments-api and what policy applies to customer data?
```

The system should retrieve service docs, policy docs, and architecture notes, then answer with citations from the source files.

## Where The LLM Fits

```text
Markdown documents
        |
        v
DocumentLoader
        |
        v
KnowledgeGraphBuilder
        |
        v
GraphRetriever
        |
        v
AnswerSynthesizer
        |-- DeterministicAnswerSynthesizer for local tests
        |-- LLMAnswerSynthesizer for production model calls
        v
Cited answer
```

The production model should receive only the retrieved chunks, graph facts, constraints, and expected answer schema. It should cite sources and avoid claims that are not supported by retrieved context.
