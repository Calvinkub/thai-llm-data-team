# Contributing to Thai LLM Data Team

Welcome to the data team! This guide explains how to contribute to the repository during Super AI SS6.

## Getting Started

1. Clone the repository
2. Create a feature branch following the naming convention below
3. Make your changes in a focused, logical commit
4. Open a pull request for review
5. Address feedback and merge

## Branch Naming Convention

Use the format: `data/<your-name>/<task>`

Examples:
- `data/calvin/validator-fix`
- `data/arthur/seapile-preprocessing`
- `data/natalie/language-detection-upgrade`
- `data/james/shard-10-quality-check`

This keeps the repository organized and makes it easy to see who is working on what.

## Commit Message Format

Use one of these prefixes to describe your work:

- `feat:` - New feature or capability (e.g., "feat: add Thai-specific tokenizer")
- `fix:` - Bug fix (e.g., "fix: handle missing UTF-8 sequences in THAILLM")
- `docs:` - Documentation update (e.g., "docs: clarify shard validation steps")
- `analysis:` - Data analysis or experiment (e.g., "analysis: token distribution across sources")

Examples:
```
feat: implement language detection filter for The Stack V2
fix: correct token counting formula for overlapping subwords
docs: update preprocessing pipeline with new edge cases
analysis: compare quality metrics between SEAPILE shards 1-10
```

## Pull Request Checklist

Before submitting your PR:

- [ ] Code runs without errors on sample shard(s)
- [ ] No credentials, API keys, or secrets committed
- [ ] Docstrings added/updated for new functions
- [ ] Validator passes on test data (run: `python validate.py --sample`)
- [ ] Commit messages follow the format above
- [ ] Branch name follows `data/<your-name>/<task>` pattern

## Adding Experiment Logs

After running an experiment, create a log entry:

1. Create a new file: `logs/YYYY-MM-DD-<slug>.md`
2. Use the template from `logs/README.md`
3. Include author, stage, dataset, input, output, findings, issues, next steps
4. Commit with message: `analysis: <brief description of findings>`

Example:
```bash
# After running preprocessing on SEAPILE shards 1-5
# Create: logs/2026-06-08-seapile-batch1-preprocessing.md
# Commit with: git commit -m "analysis: SEAPILE shards 1-5 preprocessing complete, 45.2B tokens"
```

## Code Review

All PRs require at least 1 approval before merging:

- **Calvin** (Lead Data Engineer)
- **Arthur** (Senior Data Specialist)

Reviewers will check:
- Code quality and performance
- Adherence to pipeline standards
- No data or credential leaks
- Validator tests pass
- Impact on downstream tasks

## Questions or Issues?

- Post in the #data-team Slack channel for quick questions
- Open a GitHub issue for bugs or feature requests
- Tag @calvin or @arthur for urgent matters

## Code of Conduct

Respect team members, ask for help when stuck, and share learnings with the team. This is a collaborative learning environment.
