# Master 10-Hour Sprint Plan — Thai Foundation LLM (156 People)

**Total headcount:** 156 people across 7 teams  
**Hard deadline:** Model training must START by T+3h; checkpoint ready by T+10h  
**Critical path:** Data team hands first clean batch to Model team by **T+2h30m**

### Key Difference from Original Plan

> The camp has pre-provisioned a **600 GB SSD** with four datasets already cleaned:
> **SEAPILE** (Thai web), **THAILLM** (Thai web corpus), **The Stack V2** (code), **FineMath** (math).
>
> **There is NO scraping.** The Data team's job is validate + format-convert + dedup + hand off.  
> This makes the T+2h30m handoff **realistic and achievable.**

---

## Org Structure & Headcount

| Team | Lead(s) | Size | Sprint Role |
|------|---------|------|-------------|
| Data | Poom, Pete, Calvin (TA), Arthur | 30–40 | Validate + convert + dedup 600 GB SSD data → hand off |
| Model | Boss, New Committee, Iccue | 15–20 | Tokenizer training → pretraining → checkpoint |
| MLDevOps | Jems, Pong, D | 10–15 | SSD access, storage, GPU cluster, monitoring |
| Evaluator | Poom, Pete | 5–10 | Eval harness, Thai benchmarks, perplexity checks |
| Researcher | Jimmy, P'Art, New, Peem | 5–10 | Architecture config, hyperparams, mixing weights |
| PM | Bob, Aj.Jerm, Folk, Benz | 8–10 | Coordination, hourly syncs, blockers |
| F1 | Nano, Pun | 10–16 | QA support, format conversion overflow, tooling |
| Follow-Up | Chen, Aj.Jerm, Folk | remainder | Ad-hoc support, documentation |

---

## Hour-by-Hour War Plan

### T+0:00 — Kickoff (15-minute all-hands sync, PM team runs it)

- [ ] **PM:** Share Google Sheet tracking board with all 156 people
- [ ] **MLDevOps:** Confirm SSD is mounted, paths accessible (`./data/seapile/`, `./data/thaillm/`, `./data/thestack_v2/`, `./data/finemath/`)
- [ ] **Data TA (Calvin):** Assign squads (see Phase 1 below), confirm camp HuggingFace + GitHub access
- [ ] **Model team:** Confirm GPU cluster allocated, HuggingFace token ready
- [ ] **Researcher:** Confirm architecture is locked (1B params, seq_len 2048)
- [ ] **All:** Join `#thai-llm-sprint` Slack/LINE channel

---

### T+0:15 — T+1:30 | Phase 1: Parallel Dataset Validation

**Data team (30–40 workers) splits into 4 source squads + 1 infra squad immediately.**

#### Data Squad Assignment (~35 people)

| Squad | Dataset | Task | People |
|-------|---------|------|--------|
| Squad 1 | THAILLM | Validate + format-convert + dedup | 10 |
| Squad 2 | SEAPILE (Thai subset) | Validate + extract Thai + format-convert | 8 |
| Squad 3 | The Stack V2 | Validate + format-convert | 8 |
| Squad 4 | FineMath | Validate + format-convert | 5 |
| Squad 5 | Cross-dataset dedup (SEAPILE x THAILLM) | Run dedup_exact.py across web sources | 4 |

**Each squad:**
```bash
# Step 1: Check your dataset is accessible
ls -lh ./data/<your_source>/
zcat ./data/<your_source>/shard_000.jsonl.gz | head -1 | python -m json.tool

# Step 2: Run input validator on first shard
python validator_input.py ./data/<your_source>/shard_000.jsonl.gz

# Step 3: Convert to unified schema
python convert_to_schema.py <source> ./data/<source>/shard_NNN.jsonl.gz ./shards/<source>/shard_NNN.jsonl.gz

# Step 4: Run output validator
python validator.py ./shards/<source>/shard_NNN.jsonl.gz
```

**Assign shards in the Google Sheet:** each worker takes rows, marks In Progress → Done.

#### MLDevOps (T+0:15 onward)
- [ ] Confirm shared `./shards/` write path works for all Data workers
- [ ] Reserve GPU nodes for Model team (minimum 4 GPUs)
- [ ] Set up wandb or simple training logger

#### Model Team (T+0:15 onward)
- [ ] Prepare SentencePiece training config (UNIGRAM, 48k vocab, byte_fallback=True)
- [ ] Prepare pretraining config (1B, seq_len=2048, batch size, lr schedule)
- [ ] **Wait** for Data team's first batch (T+2:30)

#### Researcher Team (T+0:15 onward)
- [ ] Lock final architecture to file `architecture.md`
- [ ] Confirm mixing weights: THAILLM 35%, SEAPILE 25%, The Stack V2 25%, FineMath 15%
- [ ] Confirm training hyperparams

#### Evaluator Team (T+0:15 onward)
- [ ] Set up lm-eval-harness or custom eval
- [ ] Identify Thai benchmarks (XQuAD-th, Thai ONET, TyDi QA-th)
- [ ] Prepare held-out Thai Wikipedia sample for perplexity eval

---

### T+1:30 — T+2:30 | Phase 2: QA Gate + Handoff Prep

**Data team:** All squads finish converting their shards, run validators, do human spot-checks.

**QA gate (both required before any shard is "Done"):**
1. `python validator.py ./shards/<source>/shard_NNN.jsonl.gz` → must print `PASS`
2. Human spot-check: reviewer samples 50 docs from shard, logs defects. Accept if defect rate < 2%.

**Squad 5 (cross-dedup):** Run `dedup_exact.py` across all SEAPILE + THAILLM shards to remove exact duplicates between the two Thai web sources.

**By T+2:15:** Calvin runs `corpus_stats.py` to get total doc count + token estimate for the handoff manifest.

```bash
# Generate manifest
python corpus_stats.py > corpus_stats.txt
python generate_manifest.py > ./shards/manifest.json
sha256sum ./shards/**/*.jsonl.gz > ./shards/SHA256SUMS
```

---

### T+2:30 — DATA HANDOFF (Milestone 1 — Non-Negotiable)

**Calvin signs and hands off to Model team.**

Handoff package in `./shards/`:
```
HANDOFF_batch1.md     ← Calvin signs this
manifest.json         ← total docs, token estimates per source, licenses
SHA256SUMS            ← checksum of every shard
seapile/              ← all QA-passed shards
thaillm/
thestack_v2/
finemath/
```

`HANDOFF_batch1.md` must state:
- Total shards and total estimated tokens
- Sources: SEAPILE (Thai), THAILLM, The Stack V2, FineMath
- All validator PASS; human defect rate < 2%
- Signed by: Calvin | Received by: Model team lead (Boss/New)
- Submission location: camp HuggingFace org / GitHub repo

---

### T+2:30 — T+9:00 | Phase 3: Model Training + Continued Data Work

**Model team and Data team work in parallel.**

#### Model Team Timeline

| Time | Task |
|------|------|
| T+2:30 | Receive handoff, verify checksums, load first shard |
| T+2:30–T+3:30 | Train SentencePiece tokenizer on ~10GB sample |
| T+3:30 | Tokenizer ready → begin pretraining run |
| T+3:30–T+9:00 | Training on GPU cluster; monitor loss every 15 min |
| T+5:00 | Intermediate checkpoint → Evaluator runs perplexity check |
| T+7:00 | Second checkpoint → Evaluator runs benchmark subset |
| T+9:00 | Final checkpoint saved, uploaded to camp HuggingFace |

#### Data Team (T+2:30 — T+5:00, stretch)
- Process any remaining shards not in batch 1
- Begin HANDOFF_batch2 when 5B+ additional tokens QA-passed
- Start pushing final processed data to camp HuggingFace repo

#### MLDevOps
- Monitor GPU utilization, disk, network continuously
- Auto-delete raw `./data/<source>/` AFTER shards are QA-passed and handed off (to free disk)
- Checkpoint every 30 min to safe storage

---

### T+9:00 — T+10:00 | Phase 4: Final Eval + Wrap

- [ ] Model team: final checkpoint → upload to camp HuggingFace
- [ ] Evaluator: full benchmark suite → write `eval_results.md`
- [ ] Data team: finalize `manifest.json`, push all shards to camp GitHub/HuggingFace
- [ ] Researcher: write model card draft
- [ ] PM: collect all deliverables, sprint retrospective

---

## Key Numbers Everyone Must Know

| Metric | Value |
|--------|-------|
| SSD data | ~600 GB, 4 datasets, pre-cleaned |
| Estimated tokens | ~20B (fill in from `corpus_stats.py` after processing) |
| Shard size | 50,000 docs / ~256 MB |
| Data → Model handoff | **T+2h30m** |
| Model training start | **T+3h** |
| Tokenizer | SentencePiece UNIGRAM, vocab=48k |
| Sequence length | 2048 tokens |
| Submit to | Camp HuggingFace org + GitHub repo ONLY |

---

## Escalation Table

| Risk | Who notices | Escalate to | Fix |
|------|------------|-------------|-----|
| SSD not accessible / wrong path | Any Data worker | MLDevOps | MLDevOps remounts / fixes path |
| Validator FAIL on a shard | Squad worker | Squad lead → Calvin | Fix schema issue, re-run conversion |
| Cross-dedup removes too many docs (>30%) | Squad 5 | Calvin + Researcher | Adjust Jaccard threshold; confirm both sources are needed |
| GPU node down | Model team | MLDevOps | Spin up backup immediately |
| Camp HuggingFace push fails | Data team | MLDevOps | Fix auth token; re-push |
| Model loss diverges | Model team | Researcher | Reduce LR, restart from checkpoint |
| PM gets no status update > 1h | PM | Calvin + Model lead | Check `#thai-llm-sprint` channel |

---

## Communication Channels

| Channel | Who uses it | Purpose |
|---------|------------|---------|
| `#thai-llm-sprint` | All 156 | Blockers, handoff announcements, major updates |
| `#data-team` | Calvin's 30–40 workers | Shard assignments, validator issues |
| `#model-team` | Model + Researcher | Training updates, loss curves |
| `#mldevops` | MLDevOps | Infra alerts |
| Google Sheet | All | Task tracking, shard progress, token counts |
| Hourly PM sync (10 min) | PM + team leads | Status rollup, blocker resolution |

---

## PM Hourly Metrics Template

```
[T+Xh STATUS]
Data team:
  - Shards converted + QA-passed: ___ / total ___
  - Estimated tokens in batch 1: ___B
  - Batch 1 handoff: [DONE at T+___] / [ETA T+___]
  - Blockers: ___

Model team:
  - Status: [waiting / tokenizer training / pretraining step ___]
  - Loss: ___
  - ETA final checkpoint: T+___

Submission status (HuggingFace / GitHub):
  - Shards pushed: ___
  - Blockers: ___
```

---

*Maintained by: Calvin (Data TA) + PM team | Updated: 2026-06-06*
