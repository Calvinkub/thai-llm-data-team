---
name: Data Quality Report
about: Report data quality issues found during spot-check or validation
title: '[QUALITY] '
labels: data-quality, validation
assignees: ''

---

## Dataset and Location

**Dataset:** (THAILLM / SEAPILE / The Stack V2 / FineMath)

**Shard:** 

**Document ID:** 

## Issue Type

Which type of quality issue did you find?

- [ ] Wrong language detected or contained
- [ ] PII detected (personal identifiable information)
- [ ] Garbled text, encoding errors, or corruption
- [ ] Incomplete/truncated document
- [ ] Duplicate content
- [ ] Invalid format for pipeline
- [ ] Other: _________

## Sample Text

Paste the problematic text (first 200-300 characters or line):

```
[Sample text here]
```

## Severity

How urgent is this issue?

- [ ] **Severity 1 (Critical):** Blocks pipeline or affects large portion of data
- [ ] **Severity 2 (High):** Affects 10+ documents or impacts quality significantly
- [ ] **Severity 3 (Medium):** Isolated issue, manageable in next batch

## Description

Explain what went wrong and why it matters:

## How to Reproduce

Steps to find and verify this issue:

1. [Step 1]
2. [Step 2]
3. [Step 3]

## Estimated Impact

- Number of affected documents (if known):
- Estimated token loss:
- Affects downstream tasks: (Yes / No / Unknown)

## Suggested Fix

How should this be handled?

## Additional Context

- Related logs from `logs/` folder:
- Related issues:
- Links to related discussions:

---

**Note:** Do not paste raw data that contains PII. Use a sanitized excerpt or describe the issue in general terms.
