# Data Team Guidelines

Working documentation for the 30-40 data team members processing Thai LLM datasets.

## Documents in This Folder

1. **[DATASET_SOURCES.md](DATASET_SOURCES.md)** - Overview of the four input sources (THAILLM, SEAPILE, The Stack V2, FineMath), their characteristics, sizes, and language compositions.

2. **[PREPROCESSING_PIPELINE.md](PREPROCESSING_PIPELINE.md)** - Step-by-step guide to the data cleaning and normalization pipeline, including Unicode handling, language detection, PII redaction, and quality filtering.

3. **[SHARD_MANAGEMENT.md](SHARD_MANAGEMENT.md)** - How to work with dataset shards, naming conventions, how to load/save JSONL files, and shard validation procedures.

4. **[VALIDATION_CHECKLIST.md](VALIDATION_CHECKLIST.md)** - Quality assurance criteria for each pipeline stage: document completeness, token count accuracy, language detection results, and downstream task readiness.

5. **[TOKENIZATION_STRATEGY.md](TOKENIZATION_STRATEGY.md)** - Thai-specific tokenization approach, handling of mixed-language content, token estimation formulas, and how to count tokens correctly for the 20B target.

## Using These Docs

- **New team members:** Start with DATASET_SOURCES.md, then SHARD_MANAGEMENT.md
- **Preprocessing work:** Reference PREPROCESSING_PIPELINE.md and VALIDATION_CHECKLIST.md
- **Token counting:** See TOKENIZATION_STRATEGY.md for formulas and tools
- **Questions?** Ask in the #data-team Slack channel or open an issue on GitHub

## Updates

These guidelines are living documents. If you find an error, ambiguity, or discover a better practice, submit a PR or create an issue.
