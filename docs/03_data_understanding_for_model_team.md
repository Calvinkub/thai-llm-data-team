# 03 — Data Understanding & Handoff Spec (Thai Foundation LLM 1B+)

**Author:** Data Team (Calvin TA)  
**Audience:** Model Team (Boss, New Committee, Iccue) + Researcher Team  
**Status:** Handoff / Data Card v1  
**Scope:** Pretraining corpus for a >1B parameter Thai-dominant foundation model

> This is the authoritative data card and handoff spec. A training engineer should be able to read this, load the data, train a tokenizer, and start pretraining without asking the Data team follow-up questions.

---

## 1. Dataset Overview

| Property | Value |
|----------|-------|
| Total corpus size | ~600 GB raw on SSD; ~Xh after processing (fill in after Stage 4 validation) |
| Primary language | Thai (SEAPILE + THAILLM) |
| Additional domains | Source code (The Stack V2), Mathematics (FineMath) |
| Intended use | Pretraining a >1B parameter Thai Foundation LLM |
| Data state | Pre-cleaned by camp; validated + format-standardized by Data team |
| License | Mixed — see per-source table below |

### Source Composition

| Source | Domain | Language | Approx Token Share | License |
|--------|--------|----------|-------------------|---------|
| THAILLM | Web text | Thai | ~35% | Web crawl / research |
| SEAPILE (Thai subset) | Web text | Thai | ~25% | CC0 / research |
| The Stack V2 | Code | Multilingual code | ~25% | Apache 2.0 / MIT / various |
| FineMath | Mathematics | English + multilingual | ~15% | Research / CC-BY |

> Actual percentages: fill in from `manifest.json` after Data team processing completes.

### Known Limitations & Biases
- Thai text skews toward web (forums, news, general text) — formal/academic Thai may be underrepresented.
- Code domain: all programming languages included; Python/JS/SQL will dominate.
- Thai-English code-switching is present and intentional — do not filter out.
- No Thai speech, audio, or image descriptions in this corpus.

---

## 2. Data Format Spec

### File format
- **JSONL.gz** — UTF-8 encoded, one JSON object per line, gzip compressed
- **NFC normalized** — all text is Unicode NFC
- **No zero-width characters** — `​`, `‌`, `‍`, `﻿` removed

### Schema (one record per document)

```json
{
  "id":            "thaillm_shard_000_000042",
  "source":        "thaillm",
  "license":       "web_crawl",
  "text":          "...",
  "n_chars":       1234,
  "n_words":       210,
  "quality_flags": [],
  "dup_group":     null,
  "domain":        "web"
}
```

| Field | Type | Notes |
|-------|------|-------|
| `id` | string | Unique. Format: `<source>_<shard>_<index>` |
| `source` | string | `seapile` / `thaillm` / `thestack_v2` / `finemath` |
| `license` | string | Per-source license string |
| `text` | string | The actual pretraining text. Do NOT pre-segment Thai with spaces. |
| `n_chars` | int | Character count |
| `n_words` | int | Whitespace-split word count (rough) |
| `quality_flags` | list | Empty = clean. Tags like `["short_doc"]` if any. |
| `dup_group` | str/null | null if unique; sha256 if near-dup kept |
| `domain` | string | `web` / `code` / `math` |

### Directory layout

```
./shards/
  seapile/        shard_000.jsonl.gz, shard_000.stats.json, ...
  thaillm/        shard_000.jsonl.gz, shard_000.stats.json, ...
  thestack_v2/    shard_000.jsonl.gz, shard_000.stats.json, ...
  finemath/       shard_000.jsonl.gz, shard_000.stats.json, ...
  manifest.json
  SHA256SUMS
  HANDOFF_batch1.md
```

### Loading the data

```python
# Stream all shards with HuggingFace datasets (recommended)
from datasets import load_dataset

ds = load_dataset(
    "json",
    data_files={
        "thai": ["./shards/thaillm/*.jsonl.gz", "./shards/seapile/*.jsonl.gz"],
        "code": ["./shards/thestack_v2/*.jsonl.gz"],
        "math": ["./shards/finemath/*.jsonl.gz"],
    },
    streaming=True,
)

for example in ds["thai"].take(3):
    print(example["id"], example["text"][:80])
```

```python
# Raw Python (no HuggingFace)
import json, gzip
from glob import glob

for path in sorted(glob("./shards/thaillm/*.jsonl.gz")):
    with gzip.open(path, "rt", encoding="utf-8") as f:
        for line in f:
            doc = json.loads(line)
            # process doc["text"]
```

### Verify integrity

```bash
# Verify checksums
sha256sum -c SHA256SUMS

# Count total docs
for f in ./shards/**/*.jsonl.gz; do
  zcat "$f" | wc -l
done | awk '{s+=$1} END {print "Total docs:", s}'
```

---

## 3. Recommended Mixing Weights for Training

Apply these sampling ratios when interleaving sources during training. Do NOT duplicate documents — use `interleave_datasets` with `probabilities`.

| Source | Domain | Recommended Weight | Rationale |
|--------|--------|--------------------|-----------|
| THAILLM | Thai web | 35% | Primary Thai text — highest coverage |
| SEAPILE Thai | Thai web | 25% | Additional Thai diversity |
| The Stack V2 | Code | 25% | Code reasoning, structure |
| FineMath | Math | 15% | Mathematical reasoning |

```python
from datasets import interleave_datasets

mixed = interleave_datasets(
    [thai_ds, seapile_ds, code_ds, math_ds],
    probabilities=[0.35, 0.25, 0.25, 0.15],
    seed=42,
)
```

**Epochs note:** At 20B training tokens total with a ~15-20B token corpus, you will see ~1-1.5 epochs. Do not over-epoch Thai web text (max ~2 epochs for web, ~3-4 for curated sources like FineMath).

---

## 4. Tokenizer Considerations for Thai (CRITICAL)

### Why Thai is different

Thai has **no spaces between words**. The sentence `ฉันกินข้าว` ("I eat rice") has no whitespace — a byte-pair or subword tokenizer must learn syllable/word boundaries from statistics alone. This is fundamentally different from English.

### What you MUST NOT do

**Do NOT pre-segment Thai text with spaces** (e.g. using PyThaiNLP `word_tokenize` and joining with spaces before tokenizer training). This will:
- Corrupt the natural Thai character sequence
- Inflate the vocabulary with whitespace-prefixed Thai tokens
- Reduce token efficiency (worse fertility)

The text in the shards has NO artificial spacing — keep it this way.

### Recommended tokenizer configuration

```python
import sentencepiece as spm

spm.SentencePieceTrainer.train(
    input="./tokenizer_train_sample.txt",  # 10-20GB sample of all domains
    model_prefix="thai_llm_tokenizer",
    vocab_size=48000,           # 48k for Thai-dominant model (range: 48k-64k)
    model_type="unigram",       # UNIGRAM preferred over BPE for Thai
    byte_fallback=True,         # CRITICAL: never OOV on rare Thai clusters
    character_coverage=0.9995,  # must cover rare Thai chars
    pad_id=3,
    unk_id=0,
    bos_id=1,
    eos_id=2,
    num_threads=16,
    shuffle_input_sentence=True,
    input_sentence_size=5000000,
)
```

**Why UNIGRAM over BPE:** UNIGRAM probabilistic model handles Thai syllable clusters more naturally; BPE can create odd splits on Thai combining characters.

**Why byte_fallback=True:** Thai has many combining marks (สระ, วรรณยุกต์). Without byte fallback, rare combinations become `<unk>`. Byte fallback ensures 0 `<unk>` tokens.

**Vocab size 48k:** Thai needs ~15-20k tokens for good character/syllable/word coverage. Additional 28k+ covers code, math, English, and common multilingual text.

### Measuring tokenizer quality

```python
# Check fertility (tokens per character) on Thai text
import sentencepiece as spm

sp = spm.SentencePieceProcessor(model_file="thai_llm_tokenizer.model")

thai_samples = [
    "ฉันกินข้าวผัดกระเพราที่ร้านอาหารไทย",
    "รัฐบาลประกาศนโยบายใหม่เกี่ยวกับการศึกษา",
    "Bangkok is the capital of Thailand กรุงเทพมหานครเป็นเมืองหลวง",
]

for text in thai_samples:
    tokens = sp.encode(text)
    fertility = len(tokens) / len(text)
    print(f"Fertility: {fertility:.2f} | Tokens: {tokens[:10]}... | Text: {text[:40]}")

# Expected: Thai fertility ~0.4-0.7 tokens/char (better than English ~0.25)
# If fertility > 1.0, tokenizer may be splitting Thai chars badly — check training data
```

---

## 5. Corpus Statistics Script

Run this to generate the full statistics report from the delivered shards.

```python
# corpus_stats.py
import json, gzip, re
from glob import glob
from collections import defaultdict

thai_block = re.compile(r"[฀-๿]")
stats = defaultdict(lambda: {"docs": 0, "chars": 0, "words": 0})

for path in sorted(glob("./shards/**/*.jsonl.gz", recursive=True)):
    source = path.split("/")[2]  # e.g. "thaillm"
    with gzip.open(path, "rt", encoding="utf-8") as f:
        for line in f:
            doc = json.loads(line)
            stats[source]["docs"] += 1
            stats[source]["chars"] += doc["n_chars"]
            stats[source]["words"] += doc["n_words"]

print(f"{'Source':<20} {'Docs':>10} {'Chars (B)':>12} {'Est Tokens (B)':>15}")
print("-" * 60)
total_tokens = 0
for source, s in stats.items():
    # Thai: ~0.165B tokens/GB raw ≈ 1 token per 3-4 chars in clean text
    est_tokens = s["chars"] / 3.5 / 1e9
    total_tokens += est_tokens
    print(f"{source:<20} {s['docs']:>10,} {s['chars']/1e9:>12.2f} {est_tokens:>15.2f}B")
print("-" * 60)
print(f"{'TOTAL':<20} {'':>10} {'':>12} {total_tokens:>15.2f}B")
```

```bash
python corpus_stats.py
```

---

## 6. Sequence Packing & Context Length

- **Recommended max sequence length:** 2048 tokens (optionally extend to 4096 in a later context-extension phase)
- **Packing strategy:** Pack multiple documents per sequence using `<EOS>` separators. Do NOT pad to max length — pack greedily.
- **EOS/BOS handling:** Prepend `<BOS>` at the start of each sequence; append `<EOS>` at end of each document before packing.
- **Loss masking:** Mask `<PAD>` tokens from loss. Do NOT mask across document boundaries — treat each document independently.

---

## 7. Train / Val / Test Split

| Split | Size | Notes |
|-------|------|-------|
| Train | ~97% | All sources, mixed by domain weights |
| Validation | ~2% | Sample from ALL sources for representative perplexity |
| Test | ~1% | Held-out — do NOT use during training |

**Critical:** Assign splits by `dup_group` (or `id` if no dup_group) to prevent any leakage. Documents that share the same `dup_group` must all be in the same split.

```python
# Assign splits deterministically by id hash
import hashlib

def assign_split(doc_id: str) -> str:
    h = int(hashlib.md5(doc_id.encode()).hexdigest(), 16) % 100
    if h < 97:
        return "train"
    elif h < 99:
        return "val"
    else:
        return "test"
```

---

## 8. Quality & Risk Notes

| Risk | Severity | Mitigation |
|------|----------|-----------|
| PII residue (IDs, phones) in Thai web text | Medium | Data team ran redaction; spot-check in val set |
| License constraints (web crawl, Stack V2) | Medium | Log all licenses; do not redistribute raw data |
| Domain imbalance (too much web) | Low-Medium | Enforce mixing weights; do not over-epoch web text |
| Thai fertility unexpectedly high | High | Check tokenizer training; ensure no pre-segmentation in input |
| Split leakage via duplicates | High | Always split by dup_group, never by shard |
| Code/math in Thai model | Low | Intended — improves reasoning; monitor Thai benchmark regression |

---

*Maintained by: Calvin (Data TA) | Updated: 2026-06-06*  
*Cross-reference: `01_data_retrieval_guidelines.md`, `02_data_preprocessing_guidelines.md`, `05_master_10h_sprint_plan.md`*
