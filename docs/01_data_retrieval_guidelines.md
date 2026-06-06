# 01 — Data Source & Access Guidelines (Thai Foundation LLM)

**Audience:** Data team workers (30–40 people, mixed skill level)  
**Situation:** The camp has pre-provisioned a **600 GB SSD** with all datasets. You do NOT scrape the internet. Your job is to **access, understand, validate, and prepare** these four datasets for the preprocessing team.

> **No fresh scraping needed.** All source data is already on the SSD or the camp's shared HuggingFace/GitHub account. Read this doc to understand what we have, where it is, and what format to expect.

---

## 1. What We Have (The Four Datasets)

| Dataset | Domain | Lang | Approx. Size | Location |
|---------|--------|------|-------------|----------|
| **SEAPILE** | Web text (Southeast Asia) | Thai + multilingual | ~100–200 GB (Thai subset) | SSD: `./data/seapile/` |
| **THAILLM** | Thai web corpus | Thai | ~100–200 GB | SSD: `./data/thaillm/` or camp GitHub repo |
| **The Stack V2** | Source code (all languages) | Code (multilingual) | ~100–200 GB | SSD: `./data/thestack_v2/` |
| **FineMath** | Math text & problems | English + multilingual | ~50–100 GB | SSD: `./data/finemath/` |

> **Day 1 task:** Confirm actual paths on the SSD with MLDevOps (Jems/Pong/D). Fill in the table above with exact sizes and paths in the shared Google Sheet.

---

## 2. About Each Dataset

### 2.1 SEAPILE
- A multilingual Southeast Asian web corpus. Contains Thai, English, and other SEA languages.
- **Your job:** Extract the Thai-language subset only (`lang == "th"` or `language == "th"`).
- Quality level: web-crawl quality — needs filtering, but the camp data may already be filtered.
- License: Check per-source attribution (usually CC0 / research use). Log in provenance sheet.
- Key fields to expect: `text`, `url`, `language`, `source`

```python
# Quick check: how many Thai docs are in SEAPILE?
import json, gzip
thai_count = 0
with gzip.open("./data/seapile/seapile_shard_000.jsonl.gz", "rt") as f:
    for line in f:
        doc = json.loads(line)
        if doc.get("language") == "th" or doc.get("lang") == "th":
            thai_count += 1
print(f"Thai docs: {thai_count}")
```

### 2.2 THAILLM Repository
- A Thai-language web corpus, likely derived from Common Crawl / Thai web sources.
- This is our primary Thai text source — treat as high priority.
- Check the camp's GitHub repo for documentation on its exact composition.
- Expected fields: `text`, `url`, `source`, `license` (or similar)

```bash
# Check first record
zcat ./data/thaillm/shard_000.jsonl.gz | head -1 | python -m json.tool
```

### 2.3 The Stack V2
- Source code dataset from BigCode (HuggingFace: `bigcode/the-stack-v2`).
- Contains code in 600+ programming languages — Python, JavaScript, SQL, etc.
- **Why include it:** Helps the foundation model understand code structure and reasoning.
- You do NOT need to filter by language — use all languages or follow Researcher team guidance.
- Expected fields: `content`, `lang` (programming language), `size`, `license`

```python
# Count by programming language (top 10)
from collections import Counter
import json, gzip

lang_counts = Counter()
with gzip.open("./data/thestack_v2/shard_000.jsonl.gz", "rt") as f:
    for line in f:
        doc = json.loads(line)
        lang_counts[doc.get("lang", "unknown")] += 1
print(lang_counts.most_common(10))
```

### 2.4 FineMath
- Math-focused text dataset (HuggingFace: `HuggingFaceTB/finemath`).
- Contains mathematical problems, proofs, and reasoning text.
- **Why include it:** Strengthens the model's mathematical reasoning ability.
- Expected fields: `text`, `source`, `score` (quality score if available)

---

## 3. Submission Requirements

> **IMPORTANT: Submit only to the camp's designated accounts.**  
> Announced at Role Orientation — confirm with PM team (Bob/Aj.Jerm) on Day 1.

- **HuggingFace:** Upload processed shards to the camp's shared HuggingFace organization/repo only.
- **GitHub:** Push code, configs, and manifests to the camp's shared GitHub repo only.
- **Do NOT use personal accounts** for any camp deliverables.

---

## 4. Data Access Checklist (Do This First on Day 1)

- [ ] Get SSD access from MLDevOps (Jems/Pong/D) — confirm mount path
- [ ] Run `ls -lh ./data/` to see all four dataset directories
- [ ] For each dataset: record actual path, file count, total size in Google Sheet
- [ ] Open one shard from each dataset, check field names with `zcat shard.jsonl.gz | head -1 | python -m json.tool`
- [ ] Confirm you can access camp HuggingFace org (login with camp token)
- [ ] Confirm you can push to camp GitHub repo

---

## 5. Handoff to Preprocessing Team

Your deliverable: a **source inventory sheet** (Google Sheet row per dataset) with:

| Field | Example |
|-------|---------|
| dataset_name | SEAPILE |
| shard_path | ./data/seapile/ |
| shard_count | 47 |
| total_size_gb | 142 |
| thai_doc_count | ~2.1M |
| schema_fields | text, url, language, source |
| license | CC0 / web crawl |
| notes | Thai subset only; filter lang==th |

Pass this to the preprocessing squad so they know exactly what to expect.

---

## 6. Per-Worker Day 1 Checklist

- [ ] SSD mounted and readable
- [ ] Four dataset directories confirmed
- [ ] One shard from each dataset successfully opened
- [ ] Field names documented in Google Sheet
- [ ] Camp HuggingFace + GitHub access confirmed
- [ ] Source inventory sheet filled

---

*See `02_data_preprocessing_guidelines.md` for what happens to this data next.*  
*See `05_master_10h_sprint_plan.md` for the timed sprint schedule.*
