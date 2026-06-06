# Experiment Logs

This folder records the outcomes, findings, and metrics from every experiment, dataset processing step, and evaluation run across the Thai LLM data pipeline.

## What Goes Here

Each log entry documents:
- **Experiment outcomes**: Results from data retrieval, preprocessing, validation runs
- **Dataset statistics**: Document counts, token estimates, format breakdowns at each pipeline stage
- **Model evaluation results**: Performance metrics, quality assessments, downstream task scores
- **Research findings**: Observations about data quality, patterns, issues, and improvements

## Log Entry Format

Create one `.md` file per experiment named `YYYY-MM-DD-<slug>.md` (e.g., `2026-06-06-initial-dataset-inventory.md`).

Use this template:

```markdown
## Run: YYYY-MM-DD - <short descriptive title>

**Author:** <your name>

**Stage:** [retrieval / preprocessing / training / evaluation]

**Dataset:** <which source(s): THAILLM, SEAPILE, The Stack V2, FineMath, or combination>

**Input:** 
- <what data/configuration went in>
- <size, shard range, parameters>

**Output:** 
- <what came out: doc counts, shard count, token count estimate>
- <format and structure details>

**Findings:** 
- <what you observed during this run>
- <patterns, quality observations>
- <unexpected behaviors or successes>

**Issues:** 
- <any problems encountered>
- <errors, edge cases, warnings>
- <leave blank if none>

**Next steps:** 
- <what should happen next>
- <who should pick this up>
- <any blockers to mention>
```

## Guidelines

- Keep entries concise but complete
- Include numeric metrics (counts, percentages, token estimates)
- Link to related issues or PRs when relevant
- If an experiment is part of a series, reference the previous log
- Update timestamps to when the run completed, not when you wrote it up

## Browsing Logs

Logs are organized by date. Use the commit history to track evolution of datasets and pipelines over time.
