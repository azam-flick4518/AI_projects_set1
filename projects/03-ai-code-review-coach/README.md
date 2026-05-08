# AI Code Review & Architecture Coach

A local code review assistant that scans a repository, finds risky implementation patterns, suggests focused tests, and produces structured review notes with an LLM-ready review boundary.

## What It Is For

Developer teams need faster feedback on pull requests, but useful review requires more than style comments. This project demonstrates a review pipeline that combines static checks, architecture rules, test suggestions, and grounded review output.

## AI Capabilities Demonstrated

- Repository scanning
- Rule-based risk detection
- Architecture boundary checks
- Test recommendation generation
- Structured review findings
- Deterministic local review for tests
- LLM-ready review synthesis boundary

## Quick Start

```powershell
cd C:\Dev\AI_5projects_set1\projects\03-ai-code-review-coach
$env:PYTHONPATH="src"
C:\Dev\AI_5projects_set1\.venv\Scripts\python.exe -m code_review_coach.cli --repo data/sample_repo
```

Run tests:

```powershell
$env:PYTHONPATH="src"
C:\Dev\AI_5projects_set1\.venv\Scripts\python.exe -m unittest discover -s tests
```

## Production Fit

In production, the deterministic analyzer can feed findings, file snippets, dependency metadata, and changed-file context into an LLM reviewer. The model should explain tradeoffs and propose review comments, but the system should keep deterministic rules for security-sensitive checks and regression tests.
