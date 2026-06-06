"""Preprocess SEAPILE parquet files -> unified schema parquet.

SEAPILE is a multilingual Southeast-Asian web corpus. This script:
  1. Reads raw parquet shards from the SSD
  2. Filters to Thai-language rows only (thai_ratio >= 0.3)
  3. Applies text cleaning + spam filter
  4. Writes clean unified-schema parquet + spam sidecar

Usage:
    python preprocess_seapile.py --input /mnt/ssd/data/seapile/ --output /mnt/ssd/shards/seapile/
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from tqdm import tqdm

from parquet_utils import (
    build_doc,
    iter_parquet_files,
    read_parquet,
    thai_ratio,
    write_parquet,
)
from spam_filter import filter_batch

SOURCE = "seapile"
MIN_THAI_RATIO = 0.3   # drop rows that aren't predominantly Thai
MIN_TEXT_LEN   = 50    # drop very short docs


def process_shard(raw_path: Path, out_path: Path, spam_path: Path) -> dict:
    rows = read_parquet(raw_path)
    stem = raw_path.stem

    docs = []
    skipped_lang = 0
    skipped_short = 0

    for i, row in enumerate(rows):
        # SEAPILE field names: text or content
        text = row.get("text") or row.get("content") or ""
        if not isinstance(text, str):
            text = str(text) if text else ""

        if len(text) < MIN_TEXT_LEN:
            skipped_short += 1
            continue

        if thai_ratio(text) < MIN_THAI_RATIO:
            skipped_lang += 1
            continue

        doc = build_doc(
            text=text,
            source=SOURCE,
            shard_id=stem,
            index=i,
            license_str=str(row.get("license", "unknown")),
            extra={"url": row.get("url", ""), "lang": row.get("lang", "")},
        )
        docs.append(doc)

    clean_docs, spam_docs = filter_batch(docs, url_field="meta.url" if docs and "meta" in docs[0] else "url")

    write_parquet(clean_docs, out_path)
    if spam_docs:
        write_parquet(spam_docs, spam_path)

    return {
        "shard":         raw_path.name,
        "rows_in":       len(rows),
        "skipped_lang":  skipped_lang,
        "skipped_short": skipped_short,
        "spam":          len(spam_docs),
        "clean":         len(clean_docs),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Preprocess SEAPILE parquet shards.")
    parser.add_argument("--input",  required=True, type=Path, help="Raw SEAPILE directory on SSD")
    parser.add_argument("--output", required=True, type=Path, help="Output directory for clean shards")
    args = parser.parse_args()

    files = iter_parquet_files(args.input)
    if not files:
        print(f"ERROR: no parquet files found in {args.input}", file=sys.stderr)
        return 1

    args.output.mkdir(parents=True, exist_ok=True)
    total = {"rows_in": 0, "skipped_lang": 0, "skipped_short": 0, "spam": 0, "clean": 0}

    for raw_path in tqdm(files, desc="seapile shards"):
        out_path  = args.output / raw_path.name
        spam_path = args.output / raw_path.name.replace(".parquet", ".spam.parquet")
        stats = process_shard(raw_path, out_path, spam_path)
        for k in total:
            total[k] += stats[k]

    print(f"\nSEAPILE Summary")
    print(f"  Shards       : {len(files)}")
    print(f"  Rows in      : {total['rows_in']:,}")
    print(f"  Skipped lang : {total['skipped_lang']:,}  (thai_ratio < {MIN_THAI_RATIO})")
    print(f"  Skipped short: {total['skipped_short']:,}  (< {MIN_TEXT_LEN} chars)")
    print(f"  Spam filtered: {total['spam']:,}")
    print(f"  Clean out    : {total['clean']:,}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
