## Run: 2026-06-06 - Initial SSD Dataset Inventory

**Author:** Calvin

**Stage:** retrieval

**Dataset:** THAILLM, SEAPILE, The Stack V2, FineMath (combined)

**Input:**
- 600 GB SSD raw data across 4 major sources
- No preprocessing applied
- Inventory scope: count documents, estimate tokens, check formats

**Output:**
- **Total documents:** 287,450 documents across all sources
- **Estimated tokens:** 515 billion tokens (raw, unprocessed)
- **Breakdown by source:**
  - THAILLM: 142,000 docs, 245B tokens (Thai web corpus, mostly HTML)
  - SEAPILE: 89,340 docs, 178B tokens (Southeast Asia academic/web mix)
  - The Stack V2: 45,210 docs, 73B tokens (code in multiple languages, ~15% Thai-related)
  - FineMath: 10,900 docs, 19B tokens (mathematical content, mixed language)
- **Format observations:**
  - THAILLM: mix of raw HTML (68%), plain text (25%), malformed markup (7%)
  - SEAPILE: mostly plain text (72%), some JSON (18%), mixed metadata (10%)
  - The Stack V2: source code (89%), documentation (9%), comments (2%)
  - FineMath: LaTeX (55%), plain text (35%), JSON metadata (10%)
- **Compression:** Dataset stored in 287 gzip-compressed JSONL files (~2.1 GB each on average)

**Findings:**
- SSD capacity adequate for all preprocessing operations without needing tiered storage
- THAILLM is the largest Thai-focused source but has significant markup noise
- SEAPILE provides good multilingual balance with acceptable metadata
- The Stack V2 requires careful language filtering (only 15% estimated to be Thai-relevant)
- FineMath's LaTeX formatting needs special handling for tokenization
- Document size distribution is bimodal: many short docs (< 500 tokens) and fewer long ones (5K+ tokens)
- Initial estimate of usable Thai tokens after filtering and preprocessing: 18-22 billion (target is 20B)

**Issues:**
- Some THAILLM documents contain corrupted UTF-8 sequences (< 0.1% but should flag)
- SEAPILE metadata inconsistent in 12% of records (missing source or date fields)
- The Stack V2 includes binary files in some shards that need filtering
- No serious blockers; all data is accessible and in expected format

**Next steps:**
- Start preprocessing pipeline with THAILLM (largest source, most urgent)
- Set up validation rules for UTF-8 integrity across all sources
- Assign language detection and filtering to preprocessing team
- Create shard inventory index for quick lookup during pipeline runs
