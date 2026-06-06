# Team 02 - Data Preprocessing Report

**Team:** Data Preprocessing  
**Date:** _______________  
**Lead / TA contact:** Calvin  

---

## Assignment

| Item | Value |
|------|-------|
| Dataset assigned | _thaillm / seapile / thestack_v2 / finemath_ |
| Shard range | _e.g. shard_000 - shard_009_ |
| Worker name(s) | |

---

## Per-Shard Log

Copy one row per shard processed. Also paste into the shared Google Sheet.

| Shard | n_docs (in) | n_spam | n_docs (out) | Spam rate | validator.py | Defect rate | SHA256 (first 16) | Notes |
|-------|-------------|--------|--------------|-----------|-------------|-------------|-------------------|-------|
| shard_000 | | | | | PASS/FAIL | | | |
| shard_001 | | | | | PASS/FAIL | | | |
| shard_002 | | | | | PASS/FAIL | | | |
| | | | | | | | | |

---

## Spam Filter Summary

| Metric | Value |
|--------|-------|
| Total shards processed | |
| Total docs input | |
| Total docs spam-flagged | |
| Overall spam rate | |
| Shards with spam rate > 20% (escalated) | |

**Escalations raised to Calvin:**

- 

---

## Issues Found

List any conversion failures, schema mismatches, or unexpected content:

- 

---

## Dedup Stats (SEAPILE + THAILLM only)

| Metric | Value |
|--------|-------|
| Total docs before dedup | |
| Exact duplicates removed | |
| Docs after dedup | |
| Estimated dedup rate | |

---

## Handoff to Team 03

- [ ] All assigned shards converted and validated (PASS)
- [ ] Spam sidecars logged
- [ ] SHA256SUMS file updated
- [ ] Dedup run on web sources (seapile + thaillm)
- [ ] Google Sheet fully filled
- [ ] Team 03 notified with shard paths

**Ready for data understanding review:** YES / NO

---

*Submit this report to: `teams/02_data_preprocessing/report.md` (commit + push)*
