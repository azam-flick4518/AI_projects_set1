# AI Incident Triage Copilot

An AI-ready incident triage system that turns alerts, logs, runbooks, and deploy metadata into a concise incident brief with suspected root causes, supporting evidence, recommended actions, and escalation guidance.

This project is intentionally small enough to run locally, but structured like a production service: clear domain models, deterministic retrieval, model/tool abstraction points, tests, eval fixtures, and architecture notes.

## Why This Project Matters

Incident response is a high-value AI use case because responders need fast synthesis across noisy systems. A useful system has to design for trust: grounded evidence, confidence scoring, repeatable evals, safe recommendations, and human-in-the-loop workflows.

## Capabilities Demonstrated

- Retrieval over heterogeneous operational data
- Evidence-backed incident summaries
- Runbook-aware recommended actions
- Confidence scoring with explicit assumptions
- Deterministic local synthesizer for tests and demos
- Explicit LLM synthesizer boundary for production integration
- Evaluation fixtures for regression testing
- Production notes for observability, safety, and governance

## Quick Start

From this project folder:

```powershell
python -m incident_triage.cli --alert data/sample_alert.json --logs data/sample_logs.json --runbooks data/runbooks.json --deploys data/deploys.json
```

Or run tests from the same folder:

```powershell
python -m unittest discover -s tests
```

If you prefer not to modify `PYTHONPATH`, run commands through the source path:

```powershell
$env:PYTHONPATH="src"; python -m incident_triage.cli --alert data/sample_alert.json --logs data/sample_logs.json --runbooks data/runbooks.json --deploys data/deploys.json
```

## Demo Scenario

The sample data models a checkout API incident:

- Alert: checkout error rate is above threshold
- Logs: elevated 500s from payment token validation
- Deploy: recent checkout release changed payment token handling
- Runbooks: checkout and payments incident playbooks

The copilot retrieves the most relevant context and produces a structured triage report that a responder could paste into an incident channel.

## Project Structure

```text
projects/01-incident-triage-copilot/
  data/                  Sample operational data
  docs/                  Architecture and implementation notes
  evals/                 Regression cases for model behavior
  src/incident_triage/   Application code
  tests/                 Unit tests
```

## Where The LLM Fits

The current implementation uses `DeterministicSynthesizer` so local runs and tests are repeatable. Production code can swap in `LLMSynthesizer` without changing retrieval, evidence ranking, input models, or the CLI contract.

```text
Alert + Logs + Runbooks + Deploys
        ↓
ContextRetriever
        ↓
Grounded evidence package
        ↓
ReportSynthesizer
        ├─ DeterministicSynthesizer for local tests
        └─ LLMSynthesizer for production model calls
        ↓
TriageReport
```

In production, the LLM layer would receive the grounded prompt package from `LLMSynthesizer.build_prompt_package()` and can use tools for:

- log search
- metrics queries
- deploy lookup
- ownership lookup
- runbook retrieval
- incident ticket creation

The important design choice is that the LLM is not the whole system. It is a replaceable synthesis layer constrained by retrieved evidence, runbook steps, structured output, and validation checks.
