# 04 — Worker Workflow & QA Playbook (Data Team)

> **Who this is for:** the 30-40 Data team workers + the Lead/TA (Calvin).
> **What this is:** the operations manual for how we organize people, split the work, track progress, and guarantee quality before we hand a clean Thai corpus to the Model team.
> **Mission:** build a clean, deduplicated, license-clear Thai corpus of **10-50B tokens** to train a >1B-parameter Thai Foundation LLM.
> **One rule above all:** *No shard reaches the Model team unless it PASSES the automated validator AND the human sampling review.* Quality beats quantity. A dirty token is worse than a missing one.

---

## 0. SPRINT REALITY: 10-Hour Deadline — Data Must Deliver in 2h30m

> **The Model team needs our data by T+2h30m** so they have 7+ hours to train. Read this box before anything else.

**The camp has pre-provisioned everything.** No scraping, no downloading. The 600 GB SSD already has:
- **THAILLM** — Thai web corpus (`./data/thaillm/`)
- **SEAPILE** — SEA web corpus, Thai subset (`./data/seapile/`)
- **The Stack V2** — Code (`./data/thestack_v2/`)
- **FineMath** — Math (`./data/finemath/`)

**Your job in 2h30m:**
1. **T+0:15** — Confirm SSD paths with MLDevOps, assign squads, start `validator_input.py` on first shard of each dataset
2. **T+0:15–T+1:30** — 4 squads in parallel: `convert_to_schema.py` → unified JSONL.gz output
3. **T+1:30–T+2:15** — Cross-dedup (SEAPILE x THAILLM), run `validator.py` on all output shards, human spot-check
4. **T+2:15** — runs `corpus_stats.py` + generates `manifest.json` + `SHA256SUMS`
5. **T+2:30** — Sign and hand off `HANDOFF_batch1.md` to Model team

**Submit to:** Camp HuggingFace org + GitHub repo ONLY (announced at Role Orientation).

See `05_master_10h_sprint_plan.md` for the full hour-by-hour war plan (all 156 people, all 7 teams).

---

## 0. The Big Picture (read this first, 2 min)

We are one of several teams in the org:

```
   ┌──────────┐   clean corpus   ┌────────────┐   model    ┌────────────┐
   │ DATA (us)│ ───────────────► │ MODEL team │ ─────────► │ EVALUATOR  │
   └──────────┘   (shards +      └────────────┘            └────────────┘
        ▲          HANDOFF.md)         ▲                          │
        │                              │                          │
   ┌──────────┐                  ┌────────────┐            ┌────────────┐
   │ MLDevOps │ (infra/storage)  │ RESEARCHER │ (recipes)  │    PM      │
   └──────────┘                  └────────────┘            └────────────┘
```

Our output is the **fuel**. If our data is dirty, the whole 1B model is wasted compute. That is why half this document is about QA.

**The pipeline, in one line:**

```
SOURCE → SCRAPE → CLEAN/NORMALIZE → QUALITY FILTER → DEDUP → VALIDATE (gate) → HUMAN REVIEW (gate) → HANDOFF
```

---

## 1. Team Structure — Squads & Pods

We split ~35 people into **5 squads**. Each squad has a **Pod Lead** (senior, owns delivery), **ICs** (do the work), and **Reviewers** (QA the output of others — never your own work).

### Sample headcount allocation (~35)

| Squad | Headcount | Pod Lead | What they own |
|---|---|---|---|
| **1. Sourcing / Scraping** | **12** | 1 lead + 1 deputy | Get raw data per source. Per-source owners. |
| **2. Preprocessing / Cleaning** | **9** | 1 lead | Normalize, clean, quality-filter raw → clean text. |
| **3. Dedup & Quality** | **5** | 1 lead | Exact + near-dup removal, quality scoring, shard packing. |
| **4. QA / Validation** | **6** | 1 lead | Run validator, human sampling review, sign-off. Independent. |
| **5. Tooling / Infra support** | **3** | 1 lead | Shared scripts, schema, storage layout, validator maintenance. |
| **Lead / TA (Calvin)** | 1 | — | Cross-squad coordination, escalation, Model/PM sync. |
| **Total** | **~36** | | |

### Sourcing squad — per-source owners (12 people)

Each source = one owner (Tier 2/3) + 1 helper (Tier 1). Owner is accountable for that source end-to-end up to raw handoff.

| Source bucket | Owner | Helper | Notes |
|---|---|---|---|
| Web crawl (CommonCrawl / OSCAR Thai slice) | 1 | 1 | Biggest volume, most noise. |
| Wikipedia / Wikisource (TH) | 1 | — | Clean license (CC BY-SA), easy win — give to a junior to build confidence. |
| Government / open data (.go.th, RTG gazette) | 1 | 1 | License must be checked per page. |
| Forums (Pantip-style, Reddit TH, public) | 1 | 1 | High PII risk, heavy boilerplate. |
| News (public archives, RSS) | 1 | 1 | Watch copyright; prefer permissive/abstracts. |
| Books / long-form (public domain, open ebooks) | 1 | — | High quality, low volume — prioritize. |
| Deputy lead (floats to bottleneck source) | 1 | — | |

> **Rule:** the **QA/Validation squad is independent** and reports to the Lead, not to the squad whose work they check. A reviewer must never sign off their own shard.

### Roles defined

- **Pod Lead** (Tier 3): owns the squad's deliverable and deadline, unblocks ICs, reviews edge cases, reports weekly numbers. Owns one pipeline *stage*.
- **IC worker** (Tier 1-2): picks up tickets from the backlog, does the unit of work, marks status.
- **Reviewer** (Tier 2-3, in QA squad): samples and validates other squads' output, logs defects, gives PASS/FAIL.

---

## 2. Skill-Tiering — match the task to the person

Nobody should ever be blocked because a task is above their level, and no senior should waste time on a junior task. Self-declare your tier on Day 1; the Lead confirms.

| Tier | Who | Can do | Typical tasks |
|---|---|---|---|
| **Tier 1 — Junior** | New, non-coder or beginner | Run scripts with given commands, manual checks, labeling, license logging | Run a provided scraper, fill the manifest, sample-read 50 docs and log defects, tag language, eyeball garbled text |
| **Tier 2 — Coder** | Can write Python | Modify/write scripts, build a source scraper from a template, write filters | Build a new source scraper, write a cleaning rule, run + debug the validator, near-dup tuning |
| **Tier 3 — Senior** | Experienced | Own a whole pipeline stage, design schema, make quality trade-offs | Pod lead, own dedup pipeline, design the schema, final sign-off, escalation decisions |

**Task → tier map (so juniors are never blocked):**

| Task | Min tier |
|---|---|
| Run an existing scraper script for a source | T1 |
| Fill provenance/license manifest | T1 |
| Human sampling review (read N docs, log defects) | T1 |
| Run the validator on a shard, read PASS/FAIL | T1 |
| Write/modify a scraper for a new source | T2 |
| Write a cleaning/quality-filter rule | T2 |
| Debug a failing validator / fix schema mismatch | T2 |
| Own dedup pipeline / shard packing | T3 |
| Design schema, set acceptance thresholds | T3 |
| Final batch sign-off / handoff to Model | T3 (Pod Lead) |

> **Pairing rule:** every Tier 1 is paired with a Tier 2/3 buddy for their first week. Ask in your squad channel before staying stuck >30 min.

---

## 3. Work Breakdown — make progress measurable

### Definition of "Unit of Work" (UoW)

> **One Unit of Work = one SHARD.**
> A **shard** = a single `.jsonl.gz` file containing **up to 50,000 documents** (or ~250-500MB compressed), from **one source**, that flows through the whole pipeline as one trackable item.

Why shards? Because "scrape the whole web" is unmeasurable, but "100 of 400 shards Done" is. Progress = `shards Done / shards total`.

**Granularity rules:**
- **One source = one or more tickets** (a big source like web-crawl is split into many shards/tickets; a small source like a book set may be one).
- **One shard = one ticket = one row in the tracking sheet.**
- A shard passes through stages owned by different squads, but stays **one ticket** with a changing `stage` field.

### Document schema (the contract — Tooling squad owns this)

Every document (one JSON line) MUST have:

```json
{
  "id": "web_crawl-000123-0000045",
  "text": "เนื้อหาภาษาไทยที่สะอาดแล้ว ...",
  "source": "web_crawl",
  "url": "https://example.go.th/page",
  "lang": "th",
  "license": "CC-BY-SA-4.0",
  "collected_at": "2026-06-01",
  "shard_id": "web_crawl-000123",
  "meta": { "quality_score": 0.87, "n_chars": 1423 }
}
```

### Sample Task Ticket template

```
TICKET: TASK-0123
─────────────────────────────────────────────
Title:        web_crawl shard 000123 — scrape → clean → dedup
Source:       web_crawl
Shard ID:     web_crawl-000123
Squad/Stage:  Sourcing  (then Preprocessing, then Dedup, then QA)
Owner:        @somchai (T2)
Reviewer:     @nида (QA squad)
Est. size:    ~45,000 docs
─────────────────────────────────────────────
Acceptance criteria:
  [ ] Raw scraped to /raw/web_crawl/000123/
  [ ] License logged in manifest
  [ ] Cleaned + NFC normalized → /clean/...
  [ ] Quality filter applied
  [ ] Deduped, dup-rate logged
  [ ] validator.py → PASS
  [ ] Human sample review → defect rate < 2%
  [ ] HANDOFF row filled
─────────────────────────────────────────────
Blocker:      (none)
Notes:
```

---

## 4. Task Tracking

### Recommended tool

> **Use a shared Google Sheet for the task tracker + a Trello/Notion board for the Kanban view.**
> Rationale for a student/club context: zero setup cost, everyone already has Google, real-time, sortable, easy to compute rollups with formulas. GitHub Projects is fine *if* the whole team is comfortable with GitHub — but with 30-40 mixed-skill people, the Sheet has the lowest friction. **Code lives in Git; task state lives in the Sheet.**

### Tracking Sheet schema (copy these column headers exactly)

| Column | Meaning | Example |
|---|---|---|
| `task_id` | Unique ticket id | `TASK-0123` |
| `source` | Source bucket | `web_crawl` |
| `owner` | Current responsible person | `@somchai` |
| `stage` | Pipeline stage now | `Preprocessing` |
| `status` | Kanban status | `In Progress` |
| `n_docs` | Document count in shard | `44982` |
| `n_tokens_est` | Estimated tokens after cleaning | `18.2M` |
| `license` | License of the source | `CC-BY-SA-4.0` |
| `qa_status` | Validator + review result | `PASS` / `FAIL` / `pending` |
| `blocker` | What's blocking, if any | `scraper banned` |
| `notes` | Free text | `re-run after proxy fix` |

> **Token estimate quick rule (Thai):** Thai is not space-segmented, so estimate tokens ≈ `n_chars / 3` as a rough planning number, or use the Model team's tokenizer once available. Always note which method in `notes`.

### Kanban column flow

```
Backlog ─► Assigned ─► In Progress ─► In Review ─► Done
   ▲                                     │
   └──────────────── Blocked ◄───────────┘  (any stage can drop to Blocked)
```

- **Backlog** — ticket created, unowned.
- **Assigned** — has an owner, not started.
- **In Progress** — owner actively working.
- **In Review** — handed to QA squad (validator + human review running).
- **Done** — passed both gates, row in HANDOFF filled.
- **Blocked** — stuck; `blocker` column filled; pinged in channel. Pod Lead owns unblocking.

---

## 5. Daily / Weekly Cadence

### Daily standup (async, 5 min, in squad channel)

Each IC posts 3 lines by a fixed time:
```
Yesterday: finished TASK-0119 (PASS), started TASK-0123
Today:     dedup on TASK-0123
Blockers:  none   (or: scraper for news source rate-limited → @lead)
```

### Weekly rhythm

| Day | Event | Who |
|---|---|---|
| Mon | Squad planning — pull tickets from backlog | Pod Leads + ICs |
| Wed | Mid-week QA sync — review defect trends | QA squad + Pod Leads |
| Fri | **Cross-team sync with Model + PM** — report rollup, get feedback | Lead + Pod Leads |
| Fri | Weekly metrics rollup published | Lead |

### Weekly metrics rollup (publish every Friday)

```
=== DATA TEAM WEEKLY ROLLUP — Week N ===
Target:                 10-50B tokens   (committed: 20B)
Tokens (clean, PASSED): 6.4B            ████████░░░░░░░░  32%
Docs collected (raw):   210M
Docs after cleaning:    122M            (-42%)
Docs after dedup:       88M             (-28% dup)
Shards Done / total:    164 / 520       (32%)
Shards Blocked:         7
Avg defect rate (QA):   1.3%            (threshold <2%  ✅)
Top blocker:            news scraper banned (3 shards)
This-week delta:        +1.1B tokens
```

### Progress dashboard layout (one screen)

```
┌────────────────────────┬───────────────────────────┐
│  TOKENS vs TARGET       │  SHARDS BY STATUS          │
│  [progress bar 32%]     │  Backlog 280 | Prog 60     │
│  6.4B / 20B             │  Review 16 | Done 164 |    │
│                         │  Blocked 7                 │
├────────────────────────┼───────────────────────────┤
│  TOKENS BY SOURCE       │  QA HEALTH                 │
│  web 3.1B | wiki 0.9B   │  Avg defect 1.3% ✅        │
│  gov 0.6B | news 0.8B   │  Shards failed gate: 12    │
│  forum 0.5B | books .5B │  Validator pass rate 94%   │
└────────────────────────┴───────────────────────────┘
```

---

## 6. QA Checklist & Gates ⭐ (the most important section)

A unit of work (shard) cannot move to **Done** until it passes **two gates**:

1. **Gate A — Automated validator** (`validator.py` → PASS), and
2. **Gate B — Human sampling review** (defect rate < 2%, see §7).

### Copy-paste checklists

**Retrieval QA (Sourcing squad, before handing to Preprocessing):**
```
[ ] License identified and logged in manifest (and is permissive enough to use)
[ ] Provenance/manifest filled: source, url, collected_at, collector
[ ] Language-ID run → shard is genuinely Thai (>90% th docs)
[ ] Encoding is UTF-8 (no mojibake / mixed encodings)
[ ] Schema valid (all required fields present per §3)
[ ] Raw stored in /raw/<source>/<shard_id>/
```

**Preprocessing QA (Preprocessing squad, before handing to Dedup):**
```
[ ] Text NFC-normalized (Thai composed correctly)
[ ] No zero-width / control chars (ZWSP, ZWNJ, BOM stripped)
[ ] PII redacted — spot-check (phone, ID card, email patterns)
[ ] Quality filter applied (drop too-short, too-symbol-heavy, non-Thai-heavy)
[ ] NO artificial space-pre-segmentation of Thai words (Thai has no word spaces — do NOT insert them)
[ ] Boilerplate/menu/nav stripped
[ ] Schema still valid
```

**Dedup QA (Dedup squad, before handing to QA squad):**
```
[ ] Exact-dup removal done (hash)
[ ] Near-dup removal done (MinHash/SimHash) — dup rate logged & sane (typically 10-40%)
[ ] Dup rate not absurd (>80% dup → investigate, likely a scrape bug)
[ ] NO cross-shard leakage: docs reserved for val/test set are NOT in any train shard
[ ] Shard packed to ≤50k docs, named correctly
```

### Automated validator — `validator.py` (the gate)

> Tooling squad owns and maintains this. **Every shard must PASS before review.** Run: `python validator.py path/to/shard.jsonl.gz`

```python
#!/usr/bin/env python3
"""validator.py — automated QA gate for a single JSONL.gz shard.

Checks: file readable & UTF-8, valid JSON lines, required schema fields,
NFC normalization, no zero-width/control chars, provenance fields present,
language tag is 'th'. Prints a PASS/FAIL report and exits non-zero on FAIL.

Usage: python validator.py shard.jsonl.gz [--max-bad 0]
"""
import sys, gzip, json, unicodedata, argparse

REQUIRED_FIELDS = ["id", "text", "source", "url", "lang",
                   "license", "collected_at", "shard_id"]
PROVENANCE_FIELDS = ["source", "url", "license", "collected_at"]

# Zero-width / problematic invisible chars we never want in clean Thai text.
ZERO_WIDTH = {"​", "‌", "‍", "﻿", "­", "⁠"}

def has_zero_width(s: str) -> bool:
    return any(ch in ZERO_WIDTH for ch in s)

def has_control(s: str) -> bool:
    # allow common whitespace (\t \n \r); flag other C0/C1 control chars
    return any(unicodedata.category(ch) == "Cc" and ch not in "\t\n\r" for ch in s)

def validate(path: str, max_bad: int) -> bool:
    errors = []          # fatal issues (any => FAIL)
    n = 0
    n_th = 0
    seen_ids = set()

    try:
        f = gzip.open(path, "rt", encoding="utf-8")
    except OSError as e:
        print(f"[FATAL] cannot open {path}: {e}")
        return False

    with f:
        for lineno, line in enumerate(f, 1):
            n += 1
            # 1) valid JSON?
            try:
                doc = json.loads(line)
            except (json.JSONDecodeError, UnicodeDecodeError) as e:
                errors.append(f"line {lineno}: bad JSON/encoding: {e}")
                continue
            # 2) required fields present?
            missing = [k for k in REQUIRED_FIELDS if k not in doc or doc[k] in (None, "")]
            if missing:
                errors.append(f"line {lineno}: missing fields {missing}")
            # 3) provenance present?
            prov_missing = [k for k in PROVENANCE_FIELDS if not doc.get(k)]
            if prov_missing:
                errors.append(f"line {lineno}: missing provenance {prov_missing}")
            # 4) duplicate id within shard?
            doc_id = doc.get("id")
            if doc_id in seen_ids:
                errors.append(f"line {lineno}: duplicate id {doc_id}")
            seen_ids.add(doc_id)
            # 5) text checks
            text = doc.get("text", "")
            if isinstance(text, str):
                if unicodedata.normalize("NFC", text) != text:
                    errors.append(f"line {lineno}: text not NFC-normalized")
                if has_zero_width(text):
                    errors.append(f"line {lineno}: zero-width char in text")
                if has_control(text):
                    errors.append(f"line {lineno}: control char in text")
            # 6) language tally
            if doc.get("lang") == "th":
                n_th += 1

    th_ratio = (n_th / n) if n else 0.0

    # ---- report ----
    print(f"=== VALIDATOR REPORT: {path} ===")
    print(f"docs:            {n}")
    print(f"thai ratio:      {th_ratio:.1%}")
    print(f"schema errors:   {len(errors)}")
    for e in errors[:20]:
        print("   -", e)
    if len(errors) > 20:
        print(f"   ... and {len(errors) - 20} more")

    fail = (n == 0) or (len(errors) > max_bad) or (th_ratio < 0.90)
    if n == 0:
        print("[FAIL] empty shard")
    if th_ratio < 0.90:
        print(f"[FAIL] thai ratio {th_ratio:.1%} < 90%")
    print("RESULT:", "FAIL" if fail else "PASS")
    return not fail

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("shard")
    ap.add_argument("--max-bad", type=int, default=0,
                    help="max tolerated schema errors before FAIL (default 0)")
    args = ap.parse_args()
    ok = validate(args.shard, args.max_bad)
    sys.exit(0 if ok else 1)
```

> **Gate rule:** validator exit code `0` = PASS, `1` = FAIL. CI/the sheet should only let `qa_status` go green after a PASS. Tier 1 workers can run this — no coding needed.

---

## 7. Sampling-Based Human Review Protocol

The validator catches *structural* problems. Humans catch *meaning* problems (garbled but valid Thai, subtle PII, boilerplate). Both gates required.

### How to sample

- For each shard, randomly sample **N = max(50, 0.5% of docs)** documents.
  - e.g. 45,000-doc shard → review ~225 docs; small shard → minimum 50.
- Use a fixed random seed so the sample is reproducible.
- **A reviewer never reviews their own shard.** QA squad does this.

### What to look for (per doc, mark OK or defect)

| Defect type | What it looks like |
|---|---|
| **Garbled text** | Mojibake, broken Thai vowels/tone marks, HTML tags left in |
| **Wrong language** | English/Chinese/etc. tagged as `th`, or empty |
| **PII leak** | Phone numbers, Thai ID (13-digit), emails, full names + address |
| **Boilerplate** | "คลิกที่นี่", cookie notices, nav menus, repeated footers |
| **Too short / junk** | < 1-2 sentences, lists of links, pure numbers |
| **License/provenance wrong** | url/license obviously inconsistent with content |

### Defect log format (one row per defect, in a `defects` tab)

```
shard_id | doc_id | defect_type | severity(1-3) | reviewer | note
web_crawl-000123 | ...0045 | PII | 3 | @nida | phone number visible
web_crawl-000123 | ...0210 | garbled | 2 | @nida | broken sara-am
```

### Acceptance threshold

> **PASS the human gate if defect rate < 2%** of sampled docs **AND zero severity-3 PII leaks.**
> - `defect_rate = defective_docs / sampled_docs`
> - **Any severity-3 PII defect → automatic FAIL**, even if overall rate is under 2%. Bounce the shard back to Preprocessing.
> - 2-5% → fixable: send back with the defect log, re-filter, re-review.
> - \>5% → systemic problem in the source/cleaner; escalate to Pod Lead, fix the pipeline not just the shard.

---

## 8. Communication & Handoff (Data → Model)

### Where files live (storage layout)

```
/datasets/
  raw/        <source>/<shard_id>/...        (scraped, untouched)
  clean/      <source>/<shard_id>.jsonl.gz   (normalized + filtered)
  final/      batch_<NN>/                     (PASSED shards, ready for Model)
     batch_07/
        web_crawl-000123.jsonl.gz
        wiki-000004.jsonl.gz
        HANDOFF.md
        checksums.sha256
```

### Naming convention

- Shard file: `<source>-<6digit_shard_number>.jsonl.gz` → `web_crawl-000123.jsonl.gz`
- Batch folder: `batch_<NN>` → `batch_07`
- Doc id: `<source>-<shard#>-<doc#>` → `web_crawl-000123-0000045`

### Per-batch `HANDOFF.md` (dataset README) — required

```markdown
# HANDOFF — batch_07
Date: 2026-06-05    Prepared by: @lead    Sign-off: @qa_lead (T3)

## Contents
- Shards: 18
- Docs: 740,221
- Tokens (est): 2.1B
- Sources: web_crawl, wiki, gov

## Quality
- All shards: validator PASS ✅
- Human review: avg defect 1.1% (threshold <2%) ✅
- Dedup: cross-shard + cross-batch checked, no val-set leakage ✅

## Licenses
- web_crawl: CC-BY (per-doc license field)
- wiki: CC-BY-SA-4.0
- gov: Open Government License

## Known caveats
- news source excluded this batch (license review pending)

## Checksums
See checksums.sha256

## Sign-off
[x] Validator PASS on every shard
[x] Human review PASS
[x] Dedup / no leakage
[x] HANDOFF complete
Signed: @qa_lead  2026-06-05
```

### Sign-off process

1. Dedup squad packs shards into `/final/batch_NN/`.
2. QA squad runs validator on **all** shards + human review.
3. QA Lead (T3) fills and signs `HANDOFF.md`.
4. Lead posts in the Model team channel: "batch_07 ready, N tokens, HANDOFF linked."
5. Model team acknowledges receipt. Only then are those tickets truly **Done**.

### Definition of Done — whole dataset

> The dataset is **DONE** when:
> - **≥ committed token target** (e.g. 20B) of clean, PASSED tokens delivered across batches.
> - **100% of delivered shards** passed validator (Gate A) and human review (Gate B).
> - Every shard has logged license + provenance; no unknown/incompatible licenses included.
> - Dedup verified across the *full* corpus; held-out val/test set has **zero leakage** into train.
> - Every batch has a signed `HANDOFF.md` + checksums.
> - Model team has acknowledged receipt of all batches.

---

## 9. Onboarding Quickstart — New Worker Day 1

```
DAY 1 CHECKLIST
─────────────────────────────────────────────
[ ] Get added to: team chat, the Tracking Sheet, the Trello board
[ ] Read this doc (§0, §3, §6) + the schema in §3
[ ] Declare your tier (1/2/3) to your Pod Lead; get a buddy if T1
[ ] Install tools:
      [ ] Python 3.10+
      [ ] git
      [ ] pip install -r requirements.txt   (validator deps, scrapers)
[ ] Clone the repo:
      git clone <data-team-repo-url>
[ ] Run the validator on the SAMPLE shard to confirm setup:
      python validator.py samples/sample_shard.jsonl.gz   → should print PASS
[ ] Pick your FIRST task:
      - T1: grab a "human review" ticket OR run an existing scraper ticket
      - T2: grab a "write a cleaning rule" or "build scraper" ticket
      - T3: meet your Pod Lead, take ownership of a stage
[ ] Move your ticket Backlog → Assigned → In Progress in the board
[ ] Post in standup: what you're starting
─────────────────────────────────────────────
Stuck > 30 min? Ask your buddy or squad channel. Asking is encouraged.
```

**Good first tasks by tier:** T1 → review a Wikipedia shard (cleanest source, builds confidence). T2 → add a quality-filter rule. T3 → own a source end-to-end.

---

## 10. Risk / Escalation

| Failure mode | Symptom | Who handles | Action |
|---|---|---|---|
| **Scraper banned / rate-limited** | 403/429, IP blocked | Source owner → Sourcing Lead | Back off, rotate user-agent/proxy (within ToS), pause ticket → `Blocked`, log in sheet. Don't hammer. |
| **Bad / unknown license** | Source license unclear or incompatible | Source owner → Lead → PM | Quarantine shard, do NOT include. Lead decides with PM/Researcher. When in doubt, leave it out. |
| **Disk full / storage out** | Writes failing, jobs die | Anyone → Tooling/Infra → MLDevOps | Ping MLDevOps for storage; clean `/raw` of already-promoted shards. |
| **Schema drift** | Validator suddenly fails many shards | Tooling Lead | Freeze schema, announce change, version it (`schema_v2`), update validator, re-validate affected shards. |
| **High defect rate (>5%)** | Human review keeps failing a source | QA Lead → Preprocessing Lead | Stop that source's shards, fix the cleaning rule at the root, then re-run. |
| **PII leak found in delivered batch** | Model team reports PII | QA Lead → Lead (URGENT) | Pull the batch, re-redact, re-review, re-handoff. Treat as P0. |
| **Dedup leakage into val set** | Eval team sees train/val overlap | Dedup Lead → Lead | Re-run dedup against the held-out set, re-pack, re-sign HANDOFF. |
| **Worker blocked / inactive** | Ticket stale in `In Progress` | Pod Lead | Reassign after 2 days idle; check in with worker. |

### Escalation ladder

```
IC  ─►  Pod Lead  ─►  Data Lead/TA (Calvin)  ─►  PM / Model / MLDevOps / Researcher
       (technical)        (cross-squad,             (cross-team decisions:
                           priorities)               license, infra, eval)
```

- **Technical block** (script broken, source down) → Pod Lead.
- **Cross-squad / priority** (which source first, headcount) → Data Lead.
- **Cross-team** (license legality, storage, eval leakage, schema contract with Model) → Data Lead escalates to the relevant team via PM.
- **P0 (PII leak, legal license problem)** → straight to Data Lead, now.

---

> **Remember:** We are the fuel for a 1B-parameter Thai model. Every shard you clean and every defect you catch directly makes the model smarter. Quality over quantity, always. A shard is only **Done** when it has passed the validator AND a human review AND been signed into a HANDOFF. Let's build the best Thai corpus there is. 🇹🇭
