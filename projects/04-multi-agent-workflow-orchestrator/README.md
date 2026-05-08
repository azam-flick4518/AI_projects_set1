# Multi-Agent Workflow Orchestrator

A local multi-agent orchestration demo that plans work, routes tasks to specialized agents, enforces approval gates, and produces an auditable execution report.

## What It Is For

Agentic AI systems are useful when work requires planning, tool use, review, and human approval. This project demonstrates those concepts locally without external APIs.

## AI Capabilities Demonstrated

- Planner, worker, reviewer, and approval agent roles
- Task routing based on required capability
- Tool boundary enforcement
- Human approval gates for risky actions
- Audit log generation
- Deterministic local execution for tests
- LLM-ready planner boundary for production

## Quick Start

```powershell
cd C:\Dev\AI_5projects_set1\projects\04-multi-agent-workflow-orchestrator
$env:PYTHONPATH="src"
C:\Dev\AI_5projects_set1\.venv\Scripts\python.exe -m agent_orchestrator.cli --workflow data/sample_workflow.json
```

Run tests:

```powershell
$env:PYTHONPATH="src"
C:\Dev\AI_5projects_set1\.venv\Scripts\python.exe -m unittest discover -s tests
```

## Production Fit

Production agent systems need more than a prompt. They need role boundaries, tool permissions, approval policies, observability, replayable audit logs, and evaluation suites. This project models those pieces in a small local workflow.
