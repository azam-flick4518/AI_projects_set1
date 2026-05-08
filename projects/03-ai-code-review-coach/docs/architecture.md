# Architecture Notes

## System Shape

```mermaid
flowchart LR
    Repo["Repository"] --> Scanner["Repo scanner"]
    Scanner --> Analyzer["Static analyzer"]
    Analyzer --> Synth["Review synthesizer"]
    Synth --> Report["Review report"]
```

## Production Fit

The local analyzer provides deterministic findings for security, reliability, and maintainability risks. A production LLM can sit behind `LLMReviewSynthesizer` to turn those grounded findings into polished review comments, architecture notes, and test recommendations.

The important boundary is that the model should not invent file paths, line numbers, or risks. It should explain and prioritize findings supplied by the scanner and analyzer.
