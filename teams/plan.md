# MVP Data Plan - Lowest Effort, Model Gets Data Fast

**Goal:** Get clean data to Model team as fast as possible using only SSD datasets.  
**Constraint:** SSD only - no scraping, no downloading, no HuggingFace pulls.  
**Target handoff:** T+2h30m

---

## The MVP Rule

> Pick ONE dataset. Get it clean. Hand it off. Then do the rest.

Do not wait for all 4 datasets to finish before handing off anything.  
Model team can start tokenizer training on partial data (even 1 dataset is enough to begin).

---

## Dataset Priority (Easiest to Process First)

| Priority | Dataset | Why first |
|----------|---------|-----------|
| 1 - START HERE | **THAILLM** | Thai web, cleanest format, biggest Thai token yield |
| 2 | **FineMath** | Small size, math text, very uniform schema |
| 3 | **The Stack V2** | Code only, no Thai NLP needed, straightforward |
| 4 - LAST | **SEAPILE** | Needs Thai-subset extraction, highest effort |

**Do THAILLM first. Hand it off. Then continue with the rest.**

---

## MVP Steps (Per Dataset, One Worker)

Skip anything that takes more than 5 minutes to set up.

```
1. python validator.py  ./data/<source>/shard_000.jsonl.gz
   -> if PASS, go to step 2
   -> if FAIL, log error and skip that shard (do not fix, move on)

2. python convert_to_schema.py \
     --source <source> \
     --input  ./data/<source>/shard_NNN.jsonl.gz \
     --output ./shards/<source>/shard_NNN.jsonl.gz
   (spam filter runs automatically)

3. python validator.py  ./shards/<source>/shard_NNN.jsonl.gz
   -> PASS = done, log row in Google Sheet
   -> FAIL = skip, mark FAIL in sheet, move to next shard

4. Log: shard name, n_docs, n_spam, validator result
```

That is the entire pipeline. Do not add steps.

---

## What to Skip in MVP Mode

These are real steps in the full plan. Skip them now, do them after handoff if time permits.

| Step | Skip reason |
|------|-------------|
| Cross-dataset dedup (SEAPILE x THAILLM) | Costs 20-30 min, small quality gain for MVP |
| Human spot-check 50 docs | Skip for first batch; do for later batches |
| SHA256SUMS generation | Do at end, not per shard |
| Thai char ratio analysis | Team 03 task, not blocking |
| .stats.json sidecars | Nice to have, not required for model training |

---

## Handoff Trigger (Do Not Wait)

Hand off to Model team when you have **any one of these**:

- [ ] All THAILLM shards converted and validated (preferred)
- [ ] Any 2 datasets done (if THAILLM is slow)
- [ ] ~5B tokens estimated (minimum viable for tokenizer training to start)

Do not wait for all 4 datasets. Call Calvin when you hit any trigger above.

---

## Minimal Handoff Package

Three things only:

```
1. shards/<source>/shard_000.jsonl.gz  (at least one validated source)
2. HANDOFF_batch1.md                   (path list + n_docs + token estimate)
3. Verbal confirm to Model team: "schema is X, no pre-segmentation"
```

Template for HANDOFF_batch1.md:

```markdown
# Handoff Batch 1

Time: T+_____
Prepared by: ______

| Source | Shards | n_docs | tokens_est | Path |
|--------|--------|--------|------------|------|
| thaillm | 12 | 600,000 | 2.4B | /mnt/ssd/shards/thaillm/ |

Schema: id, source, license, text, n_chars, n_words, quality_flags, dup_group, domain
Format: JSONL.gz, UTF-8, NFC
Tokenizer note: SentencePiece UNIGRAM, DO NOT pre-segment Thai.
Validator: PASS on all shards listed.
```

---

## Time Targets (MVP)

| Time | Goal |
|------|------|
| T+0:15 | First worker starts converting THAILLM shard_000 |
| T+0:30 | First shard PASS, logged in sheet |
| T+1:00 | 5+ shards PASS (enough to confirm pipeline works) |
| T+2:00 | THAILLM done or near-done |
| T+2:30 | HANDOFF_batch1.md sent to Model team |
| T+2:30 - T+4:00 | Continue remaining datasets (FineMath, Stack V2, SEAPILE) |

---

## If Something Breaks

| Problem | MVP response |
|---------|-------------|
| Shard won't open / corrupt file | Skip it, log SKIP, move to next shard |
| validator.py FAIL on output | Log FAIL, do not send to Model team, continue others |
| convert_to_schema.py crashes | Check terminal error, if not fixable in 5 min - skip shard |
| SEAPILE Thai extraction unclear | Skip SEAPILE entirely in MVP, do after handoff |
| Spam rate > 20% | Log it, escalate to Calvin, but do NOT block on it |

**Rule: never let one broken shard block the pipeline. Skip and move on.**

---

## One-Line Summary for Workers

> Convert THAILLM shards one by one, validator PASS = ship it, log it. That is the job.
