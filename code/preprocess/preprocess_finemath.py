"""Preprocess FineMath parquet files -> unified schema parquet.

FineMath is a mathematics text corpus (proofs, problems, solutions).
This script:
  1. Reads raw parquet shards
  2. Drops empty docs and docs with no math signals (heuristic)
  3. Applies text cleaning
  4. Writes clean unified-schema parquet

Usage:
    python preprocess_finemath.py --input /mnt/ssd/data/finemath/ --output /mnt/ssd/shards/finemath/
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from tqdm import tqdm

from parquet_utils import build_doc, iter_parquet_files, read_parquet, write_parquet

SOURCE = "finemath"
MIN_TEXT_LEN = 30

# Heuristic: at least one of these signals = likely real math content
_MATH_SIGNAL = re.compile(
    r"(\$\$?|\\frac|\\sum|\\int|\\begin\{|=|[0-9]+\s*[\+\-\*/]\s*[0-9]+|theorem|proof|lemma)",
    re.IGNORECASE,
)


def has_math_signal(text: str) -> bool:
    return bool(_MATH_SIGNAL.search(text))


def process_shard(raw_path: Path, out_path: Path) -> dict:
    rows = read_parquet(raw_path)
    stem = raw_path.stem

    docs = []
    skipped_empty = 0
    skipped_no_math = 0

    for i, row in enumerate(rows):
        # FineMath field names: text, problem, solution, content
        text = (
            row.get("text")
            or row.get("problem")
            or row.get("content")
            or ""
        )
        if not isinstance(text, str):
            text = str(text) if text else ""

        # Some FineMath rows have separate problem + solution fields
        solution = row.get("solution") or row.get("answer") or ""
        if solution and isinstance(solution, str):
            text = text + "\n" + solution if text else solution

        if len(text.strip()) < MIN_TEXT_LEN:
            skipped_empty += 1
            continue

        if not has_math_signal(text):
            skipped_no_math += 1
            continue

        doc = build_doc(
            text=text,
            source=SOURCE,
            shard_id=stem,
            index=i,
            license_str=str(row.get("license", "unknown")),
            extra={
                "source_name": str(row.get("source") or row.get("dataset", "")),
                "level":       str(row.get("level") or row.get("difficulty", "")),
            },
        )
        docs.append(doc)

    write_parquet(docs, out_path)

    return {
        "shard":           raw_path.name,
        "rows_in":         len(rows),
        "skipped_empty":   skipped_empty,
        "skipped_no_math": skipped_no_math,
        "clean":           len(docs),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Preprocess FineMath parquet shards.")
    parser.add_argument("--input",  required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    files = iter_parquet_files(args.input)
    if not files:
        print(f"ERROR: no parquet files found in {args.input}", file=sys.stderr)
        return 1

    args.output.mkdir(parents=True, exist_ok=True)
    total = {"rows_in": 0, "skipped_empty": 0, "skipped_no_math": 0, "clean": 0}

    for raw_path in tqdm(files, desc="finemath shards"):
        out_path = args.output / raw_path.name
        stats = process_shard(raw_path, out_path)
        for k in total:
            total[k] += stats[k]

    print(f"\nFineMath Summary")
    print(f"  Shards          : {len(files)}")
    print(f"  Rows in         : {total['rows_in']:,}")
    print(f"  Skipped empty   : {total['skipped_empty']:,}")
    print(f"  Skipped no math : {total['skipped_no_math']:,}  (no math signal found)")
    print(f"  Clean out       : {total['clean']:,}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
