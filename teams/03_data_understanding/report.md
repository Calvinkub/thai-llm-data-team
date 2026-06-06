# Team 03 - Data Understanding & Model Team Liaison Report

**Team:** Data Understanding / Model Liaison  
**Date:** _______________  
**Lead / TA contact:** Calvin  
**Model team contacts:** Boss, New, Iccue  

---

## Corpus Composition (Final)

Fill in from Step 1-2 of the notebook.

| Source | n_docs | n_tokens (est) | Actual mix % | Target mix % | Delta | Status |
|--------|--------|----------------|--------------|--------------|-------|--------|
| thaillm | | | | 35% | | OK/REVIEW |
| seapile | | | | 25% | | OK/REVIEW |
| thestack_v2 | | | | 25% | | OK/REVIEW |
| finemath | | | | 15% | | OK/REVIEW |
| **TOTAL** | | | **100%** | **100%** | | |

**Chinchilla target:** ~20B tokens for 1B parameter model  
**Actual total tokens:** ___B  
**Gap from target:** ___B tokens (___ %)

---

## Thai Character Ratio Check

| Source | Sample size | Avg Thai ratio | Min | Max | Status |
|--------|-------------|---------------|-----|-----|--------|
| thaillm | | | | | (expect > 0.5) |
| seapile | | | | | (expect > 0.3) |

---

## Model Team Confirmation

Record the verbal/written confirmation from Model team that the format is acceptable.

| Check | Confirmed by | Time | Notes |
|-------|-------------|------|-------|
| JSONL.gz format loadable | | | |
| Schema fields correct | | | |
| Tokenizer note understood (no pre-segmentation) | | | |
| Mixing ratios agreed | | | |
| Shard path shared | | | |

**Final mix ratios confirmed with Model team:** YES / NO

If NO - write adjusted ratios here and reason:

- 

---

## Mixing Ratio Decision

If actual mix deviates significantly from target, document the agreed adjustment:

| Source | Agreed final weight | Reason for change |
|--------|--------------------|--------------------|
| thaillm | % | |
| seapile | % | |
| thestack_v2 | % | |
| finemath | % | |

---

## Handoff Data Card

- [ ] `logs/handoff_data_card.json` generated and committed
- [ ] Model team received shard paths + SHA256SUMS
- [ ] `docs/03_data_understanding_for_model_team.md` up to date with actual numbers
- [ ] Calvin notified of handoff completion

**Handoff complete at:** T+_____ (sprint time)

---

## Issues and Notes

- 

---

*Submit this report to: `teams/03_data_understanding/report.md` (commit + push)*
