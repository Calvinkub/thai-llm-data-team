# 02 — Data Preprocessing Guidelines (Thai Foundation LLM)

**Audience:** Preprocessing/Cleaning workers (mixed skill level)  
**Situation:** The 600 GB SSD data is **already cleaned by the camp**. Your job is:
1. **Validate** the data matches the agreed schema
2. **Format-convert** to the standard output schema if needed
3. **Cross-dataset dedup check** (deduplicate across SEAPILE + THAILLM, since they may overlap)
4. **Hand off** clean, validated shards to the Model team

> **No heavy cleaning pipeline needed.** The camp pre-processed the data. Focus on validation, format consistency, and dedup across sources.

---

## 1. Pipeline Overview

```
SSD Raw Data (4 datasets, ~600 GB)
         |
         v
[Stage 1] Schema Validation
  - Check all required fields present
  - Check UTF-8 encoding
  - Check NFC normalization (quick scan)
  - For SEAPILE: confirm Thai-only rows extracted
         |
         v
[Stage 2] Format Standardization
  - Convert to unified JSONL.gz output schema
  - Normalize field names (text, source, license, id, ...)
  - Re-shard to standard 50k docs / ~256 MB
         |
         v
[Stage 2.5] Spam & Adult Content Filter  ← NEW, runs automatically inside convert_to_schema.py
  - Blocks Thai gambling keywords: บาคาร่า, หวยออนไลน์, แทงบอล, คาสิโนออนไลน์, สล็อตออนไลน์ + 15 more
  - Blocks adult/gambling domains (stored as prxxxhub.com style in logs)
  - Flagged docs go to .spam.jsonl.gz sidecar — NOT silently deleted
  - quality_flags gets "spam_filter" tag on flagged docs
         |
         v
[Stage 3] Cross-Dataset Dedup
  - Exact dedup (sha256) across ALL four datasets combined
  - Remove exact duplicates between SEAPILE and THAILLM (high overlap risk)
         |
         v
[Stage 4] Validator Gate
  - Run validator.py — must PASS
  - Human spot-check 50 docs per shard (<2% defect)
         |
         v
HANDOFF → Model Team
```

---

## 2. Output Schema (Unified)

Every shard you produce must follow this schema exactly. One JSON object per line.

```json
{
  "id":            "seapile_000_00042",
  "source":        "seapile",
  "license":       "cc0",
  "text":          "...(Thai or code or math text)...",
  "n_chars":       1234,
  "n_words":       210,
  "quality_flags": [],
  "dup_group":     null,
  "domain":        "web"
}
```

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `id` | string | YES | `<source>_<shard>_<index>`, must be unique |
| `source` | string | YES | one of: `seapile`, `thaillm`, `thestack_v2`, `finemath` |
| `license` | string | YES | from source metadata, or `"unknown"` with note |
| `text` | string | YES | the actual text content |
| `n_chars` | int | YES | `len(text)` |
| `n_words` | int | YES | rough word count (split by whitespace for code/math; PyThaiNLP newmm for Thai) |
| `quality_flags` | list | YES | empty list `[]` if no issues, else tag like `["short_doc"]` |
| `dup_group` | string or null | YES | sha256 of text if dup found, else null |
| `domain` | string | YES | one of: `web`, `code`, `math` |

---

## 3. Stage 1: Schema Validation

Run this on every raw shard before doing anything else.

```python
# validator_input.py — check raw shard fields
import json, gzip, sys

REQUIRED_FIELDS = {"text"}  # minimum required in raw data
path = sys.argv[1]

errors = 0
with gzip.open(path, "rt", encoding="utf-8") as f:
    for i, line in enumerate(f):
        doc = json.loads(line)
        if "text" not in doc or not doc["text"].strip():
            print(f"Line {i}: missing or empty text")
            errors += 1
        if len(doc["text"]) < 50:
            print(f"Line {i}: suspiciously short ({len(doc['text'])} chars)")

print(f"\nTotal errors: {errors}")
print("PASS" if errors == 0 else "FAIL")
```

```bash
python validator_input.py ./data/thaillm/shard_000.jsonl.gz
```

---

## 4. Stage 2: Format Standardization

Convert each dataset's native format to the unified output schema.

```python
# convert_to_schema.py
import json, gzip, hashlib, sys
from pathlib import Path

SOURCE = sys.argv[1]        # e.g. "thaillm"
INPUT = sys.argv[2]         # e.g. ./data/thaillm/shard_000.jsonl.gz
OUTPUT = sys.argv[3]        # e.g. ./shards/thaillm/shard_000.jsonl.gz
DOMAIN_MAP = {
    "seapile": "web",
    "thaillm": "web",
    "thestack_v2": "code",
    "finemath": "math",
}

Path(OUTPUT).parent.mkdir(parents=True, exist_ok=True)
domain = DOMAIN_MAP.get(SOURCE, "web")

with gzip.open(INPUT, "rt", encoding="utf-8") as fin, \
     gzip.open(OUTPUT, "wt", encoding="utf-8") as fout:
    for i, line in enumerate(fin):
        raw = json.loads(line)
        text = raw.get("text") or raw.get("content") or ""
        if not text.strip():
            continue
        doc = {
            "id":            f"{SOURCE}_{Path(INPUT).stem}_{i:06d}",
            "source":        SOURCE,
            "license":       raw.get("license", "unknown"),
            "text":          text,
            "n_chars":       len(text),
            "n_words":       len(text.split()),
            "quality_flags": [],
            "dup_group":     None,
            "domain":        domain,
        }
        fout.write(json.dumps(doc, ensure_ascii=False) + "\n")

print(f"Done: {OUTPUT}")
```

---

## 4.5 Stage 2.5: Spam and Adult Content Filter

> **This runs automatically** when you call `convert_to_schema.py`. You do not need to run it separately. Read this section so you understand what it does and what to do when it flags something.

### What it filters

The filter catches two categories of unwanted content:

**Thai gambling / spam keywords** (keyword density check — a news article mentioning gambling once is fine; a spam page stuffed with these is dropped):

| Thai keyword | English meaning |
|---|---|
| บาคาร่า / บาคาร่าออนไลน์ | Baccarat / online baccarat |
| หวยออนไลน์ / หวยลาว / หวยฮานอย | Online lottery |
| แทงบอล / แทงบอลออนไลน์ | Football betting |
| คาสิโนออนไลน์ | Online casino |
| สล็อตออนไลน์ / สล็อตแตกง่าย | Online slots |
| พนันออนไลน์ | Online gambling |
| แจกเครดิตฟรี / กดรับโบนัส | Free credit / bonus spam |
| เว็บพนัน / โปรโมชั่นสล็อต | Gambling site / slot promotions |
| + 8 more Thai spam phrases | |

**Blocked domains** (any document whose source URL or body text contains these):

| Displayed in logs | Category |
|---|---|
| prxxxhub.com | Adult |
| xvixxxos.com | Adult |
| xhxxxster.com | Adult |
| livejxxxin.com | Adult |
| chaxxxate.com | Adult |
| onlyfxxx.com | Adult |
| gcxxx.com, bxtflix.co, uxxa.bet | Thai gambling sites |
| saxame.com, vexxx168.com | Thai gambling sites |

> Blocked sites are **censored in all logs and reports** so this document and codebase are safe to share publicly.

### What happens to flagged documents

Flagged docs are **NOT silently deleted**. Instead:

```
shard_000.jsonl.gz          <- clean docs only (goes to Model team)
shard_000.spam.jsonl.gz     <- flagged docs with reasons (for your audit)
```

Each flagged doc in the sidecar has two extra fields:
```json
{
  "quality_flags": ["spam_filter"],
  "_spam_reasons": ["spam_keywords"],
  "_spam_matches": ["kw:บxxxาร่า", "kw:แxxxบอล", "kw:คxxxโน"]
}
```

### Worker action required

After running `convert_to_schema.py`, check if a `.spam.jsonl.gz` was produced:

```bash
# Check how many docs were flagged
zcat ./shards/thaillm/shard_000.spam.jsonl.gz | wc -l
```

- **Spam rate < 5%:** normal, no action needed. Log the count in the Google Sheet.
- **Spam rate 5-20%:** spot-check 10 flagged docs. If correct, log and move on.
- **Spam rate > 20%:** escalate to Calvin. The source shard may have a systematic issue.

```python
# Quick spot-check of flagged docs
import json, gzip

with gzip.open("./shards/thaillm/shard_000.spam.jsonl.gz", "rt") as f:
    for i, line in enumerate(f):
        doc = json.loads(line)
        print(f"--- Doc {i} ---")
        print(f"Reasons : {doc['_spam_reasons']}")
        print(f"Matches : {doc['_spam_matches']}")   # already censored
        print(f"Text    : {doc['text'][:120]}")
        print()
        if i >= 9:
            break
```

### Running the filter standalone (optional)

```python
from spam_filter import check_spam

result = check_spam(
    text="บาคาร่าออนไลน์ สมัครรับโบนัสฟรี แทงบอลได้เลย",
    url="https://gclub.com/register"
)
print(result.is_spam)          # True
print(result.reasons)          # ['blocked_source_domain', 'spam_keywords']
print(result.censored_matches) # ['domain:gcxxx.com', 'kw:บxxxาร่า', ...]
```

---

## 5. Stage 3: Cross-Dataset Dedup

SEAPILE and THAILLM both come from Thai web text — they will have exact duplicates. Run this after converting both to the unified schema.

```python
# dedup_exact.py — exact dedup across all shards of all sources
import json, gzip, hashlib
from pathlib import Path
from glob import glob

INPUT_DIRS = ["./shards/seapile/", "./shards/thaillm/"]  # sources likely to overlap
OUTPUT_DIR = "./shards_deduped/"
seen = set()
kept = 0
duped = 0

for input_dir in INPUT_DIRS:
    for shard_path in sorted(glob(f"{input_dir}/*.jsonl.gz")):
        out_path = shard_path.replace(input_dir, OUTPUT_DIR)
        Path(out_path).parent.mkdir(parents=True, exist_ok=True)
        with gzip.open(shard_path, "rt") as fin, \
             gzip.open(out_path, "wt") as fout:
            for line in fin:
                doc = json.loads(line)
                h = hashlib.sha256(doc["text"].encode()).hexdigest()
                if h in seen:
                    doc["dup_group"] = h
                    duped += 1
                    continue  # drop exact dup
                seen.add(h)
                kept += 1
                fout.write(json.dumps(doc, ensure_ascii=False) + "\n")

print(f"Kept: {kept} | Removed: {duped} duplicates")
```

> For The Stack V2 and FineMath, exact dedup within each dataset only (they don't overlap with Thai web text).

---

## 6. Stage 4: Validation Gate

Run on every output shard. Must PASS before handoff.

```python
# validator.py — final output shard validator
import json, gzip, sys, unicodedata

REQUIRED = {"id", "source", "license", "text", "n_chars", "n_words",
            "quality_flags", "dup_group", "domain"}
VALID_SOURCES = {"seapile", "thaillm", "thestack_v2", "finemath"}
VALID_DOMAINS = {"web", "code", "math"}
ZERO_WIDTH = {"​", "‌", "‍", "﻿"}

path = sys.argv[1]
errors = []

with gzip.open(path, "rt", encoding="utf-8") as f:
    for i, line in enumerate(f):
        doc = json.loads(line)
        # Required fields
        missing = REQUIRED - set(doc.keys())
        if missing:
            errors.append(f"Line {i}: missing fields {missing}")
        # UTF-8 + NFC
        if unicodedata.normalize("NFC", doc.get("text","")) != doc.get("text",""):
            errors.append(f"Line {i}: text is not NFC normalized")
        # Zero-width chars
        if any(c in doc.get("text","") for c in ZERO_WIDTH):
            errors.append(f"Line {i}: zero-width chars found")
        # Valid enums
        if doc.get("source") not in VALID_SOURCES:
            errors.append(f"Line {i}: invalid source '{doc.get('source')}'")
        if doc.get("domain") not in VALID_DOMAINS:
            errors.append(f"Line {i}: invalid domain '{doc.get('domain')}'")
        if errors and len(errors) > 20:
            break  # stop early if too many errors

if errors:
    for e in errors[:20]:
        print(e)
    print(f"\nFAIL — {len(errors)} errors found")
    sys.exit(1)
else:
    print("PASS")
```

```bash
python validator.py ./shards_deduped/thaillm/shard_000.jsonl.gz
# Expected: PASS
```

---

## 7. Thai-Specific Notes (SEAPILE + THAILLM)

Since the data is pre-cleaned, you mainly need to verify these properties, not fix them:

- **NFC normalization:** Thai text should be NFC. The validator checks this automatically.
- **No word-boundary spaces:** Thai text has no spaces between words — this is CORRECT. Do NOT add spaces. The Model team's SentencePiece tokenizer handles this.
- **Zero-width characters:** Remove if found (`​`, `‌`, `‍`, `﻿`). The validator flags these.
- **Thai-English code-switching:** Normal and expected — keep mixed docs.

Quick sanity check for a Thai shard:
```python
import json, gzip, re

thai_block = re.compile(r"[฀-๿]")
with gzip.open("./shards/thaillm/shard_000.jsonl.gz", "rt") as f:
    sample = [json.loads(f.readline()) for _ in range(5)]

for doc in sample:
    thai_chars = len(thai_block.findall(doc["text"]))
    ratio = thai_chars / max(len(doc["text"]), 1)
    print(f"Thai ratio: {ratio:.2f} | First 80 chars: {doc['text'][:80]}")
```

---

## 8. Sharding Strategy

Output shards: `./shards/<source>/shard_<NNN>.jsonl.gz`  
Target: **50,000 docs per shard**, max ~256 MB uncompressed.

```bash
# Directory layout after your work:
./shards/
  seapile/
    shard_000.jsonl.gz
    shard_000.stats.json
    shard_001.jsonl.gz
    ...
  thaillm/
    shard_000.jsonl.gz
    ...
  thestack_v2/
    shard_000.jsonl.gz
    ...
  finemath/
    shard_000.jsonl.gz
    ...
  manifest.json       # total counts, token estimates, all sources
  SHA256SUMS          # checksum of every shard
```

Stats sidecar (`.stats.json`):
```json
{
  "shard": "shard_000.jsonl.gz",
  "source": "thaillm",
  "n_docs": 50000,
  "n_chars_total": 125000000,
  "n_tokens_est": 20625000,
  "validator": "PASS"
}
```

---

## 9. Per-Worker Checklist (Run for Every Shard)

- [ ] `validator_input.py` — PASS on raw input shard
- [ ] `convert_to_schema.py` — unified schema output written (spam filter runs automatically)
- [ ] Check spam sidecar: `zcat shard_NNN.spam.jsonl.gz | wc -l` — log count in Google Sheet
- [ ] If spam rate > 20%, escalate to Calvin before continuing
- [ ] `dedup_exact.py` — duplicates removed (for web sources)
- [ ] `validator.py` — PASS on output shard
- [ ] `.stats.json` sidecar written
- [ ] Shard row added to Google Sheet (path, n_docs, n_spam_filtered, n_tokens_est, validator status)
- [ ] Human spot-check: 50 random docs, defect rate < 2%
- [ ] SHA256 checksum added to `SHA256SUMS` file

---

*See `03_data_understanding_for_model_team.md` for what the Model team does with these shards.*  
*See `04_worker_workflow_and_qa.md` for team structure and task assignment.*
