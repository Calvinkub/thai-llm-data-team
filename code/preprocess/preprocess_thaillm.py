"""Preprocess THAILLM parquet files -> unified schema parquet.

THAILLM is a Thai web corpus - expect high Thai character ratio.
This script:
  1. Reads raw parquet shards
  2. Drops empty / very short docs
  3. Applies text cleaning + spam filter
  4. Writes clean unified-schema parquet + spam sidecar

Usage:
    python preprocess_thaillm.py --input /mnt/ssd/data/thaillm/ --output /mnt/ssd/shards/thaillm/
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from tqdm import tqdm

from parquet_utils import build_doc, iter_parquet_files, read_parquet, write_parquet
from spam_filter import filter_batch

SOURCE = "thaillm"
MIN_TEXT_LEN = 50


def process_shard(raw_path: Path, out_path: Path, spam_path: Path) -> dict:
    rows = read_parquet(raw_path)
    stem = raw_path.stem

    docs = []
    skipped = 0

    for i, row in enumerate(rows):
        # THAILLM field names: text, content, or body
        text = row.get("text") or row.get("content") or row.get("body") or ""
        if not isinstance(text, str):
            text = str(text) if text else ""

        if len(text.strip()) < MIN_TEXT_LEN:
            skipped += 1
            continue

        doc = build_doc(
            text=text,
            source=SOURCE,
            shard_id=stem,
            index=i,
            license_str=str(row.get("license", "unknown")),
            extra={"url": row.get("url", ""), "domain": row.get("domain", "")},
        )
        docs.append(doc)

    clean_docs, spam_docs = filter_batch(docs)

    write_parquet(clean_docs, out_path)
    if spam_docs:
        write_parquet(spam_docs, spam_path)

    return {
        "shard":   raw_path.name,
        "rows_in": len(rows),
        "skipped": skipped,
        "spam":    len(spam_docs),
        "clean":   len(clean_docs),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Preprocess THAILLM parquet shards.")
    parser.add_argument("--input",  required=True, type=Path, help="Raw THAILLM directory on SSD")
    parser.add_argument("--output", required=True, type=Path, help="Output directory for clean shards")
    args = parser.parse_args()

    files = iter_parquet_files(args.input)
    if not files:
        print(f"ERROR: no parquet files found in {args.input}", file=sys.stderr)
        return 1

    args.output.mkdir(parents=True, exist_ok=True)
    total = {"rows_in": 0, "skipped": 0, "spam": 0, "clean": 0}

    for raw_path in tqdm(files, desc="thaillm shards"):
        out_path  = args.output / raw_path.name
        spam_path = args.output / raw_path.name.replace(".parquet", ".spam.parquet")
        stats = process_shard(raw_path, out_path, spam_path)
        for k in total:
            total[k] += stats[k]

    print(f"\nTHAILLM Summary")
    print(f"  Shards       : {len(files)}")
    print(f"  Rows in      : {total['rows_in']:,}")
    print(f"  Skipped short: {total['skipped']:,}  (< {MIN_TEXT_LEN} chars)")
    print(f"  Spam filtered: {total['spam']:,}")
    print(f"  Clean out    : {total['clean']:,}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
