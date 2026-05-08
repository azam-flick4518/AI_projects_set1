# LLM Evaluation & Governance Studio

A local evaluation and governance harness for testing model outputs against expected content, citation requirements, forbidden claims, and policy checks.

## What It Is For

Production AI systems need repeatable quality checks. This project demonstrates how teams can evaluate model behavior before release, catch regressions, and enforce governance rules locally.

## AI Capabilities Demonstrated

- Eval case loading
- Model/provider abstraction
- Deterministic local model fixture
- Expected-content scoring
- Citation and groundedness checks
- Policy violation detection
- Regression-style evaluation reports
- LLM-provider-ready boundary

## Quick Start

```powershell
cd C:\Dev\AI_5projects_set1\projects\05-llm-evaluation-governance-studio
$env:PYTHONPATH="src"
C:\Dev\AI_5projects_set1\.venv\Scripts\python.exe -m eval_governance.cli --cases data/eval_cases.json
```

Run tests:

```powershell
$env:PYTHONPATH="src"
C:\Dev\AI_5projects_set1\.venv\Scripts\python.exe -m unittest discover -s tests
```

## Production Fit

The local fixture model makes the harness runnable without network access. In production, `LLMProvider` can call a real model, while the evaluator and policy checks remain stable quality gates in CI.
