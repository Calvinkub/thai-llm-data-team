"""Exact deduplication of Thai LLM JSONL.gz shards via SHA-256 of text."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import sys
from pathlib import Path
from typing import Iterator

from tqdm import tqdm

# ------------------------------------------------------------------
# I/O helpers
# ------------------------------------------------------------------


def iter_jsonl_gz(path: Path) -> Iterator[dict]:
    """Yield parsed JSON objects from a JSONL.gz file."""
    with gzip.open(path, "rt", encoding="utf-8") as fh:
        for raw in fh:
            raw = raw.strip()
            if not raw:
                continue
            try:
                yield json.loads(raw)
            except json.JSONDecodeError:
                continue


def collect_shards(dirs: list[Path]) -> list[Path]:
    """Return sorted list of all *.jsonl.gz files under given directories."""
    shards: list[Path] = []
    for directory in dirs:
        shards.extend(sorted(directory.rglob("*.jsonl.gz")))
    return shards


def sha256_of_text(text: str) -> str:
    """Return hex SHA-256 digest of UTF-8 encoded text."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


# ------------------------------------------------------------------
# Dedup logic
# ------------------------------------------------------------------


def dedup_shards(
    shards: list[Path],
    output_dir: Path,
) -> tuple[int, int, int]:
    """
    Deduplicate across shards; write clean shards to output_dir.

    Returns (total_docs, duplicates_removed, kept_docs).
    """
    seen_hashes: set[str] = set()
    total = 0
    duplicates = 0

    output_dir.mkdir(parents=True, exist_ok=True)

    for shard_path in tqdm(shards, desc="shards", unit="shard"):
        kept_docs: list[dict] = []

        for doc in iter_jsonl_gz(shard_path):
            total += 1
            text = doc.get("text")
            if not isinstance(text, str) or not text.strip():
                duplicates += 1
                continue

            digest = sha256_of_text(text)
            if digest in seen_hashes:
                duplicates += 1
                # Annotate dup_group with hash for tracing
                doc["dup_group"] = digest
                continue

            seen_hashes.add(digest)
            doc["dup_group"] = digest
            kept_docs.append(doc)

        # Mirror directory structure under output_dir
        rel = shard_path.name
        out_path = output_dir / rel
        with gzip.open(out_path, "wt", encoding="utf-8") as fh:
            for kept in kept_docs:
                fh.write(json.dumps(kept, ensure_ascii=False) + "\n")

    kept = total - duplicates
    return total, duplicates, kept


# ------------------------------------------------------------------
# CLI
# ------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    """Build argument parser."""
    parser = argparse.ArgumentParser(
        description="Exact deduplication of JSONL.gz shards using SHA-256 of text."
    )
    parser.add_argument(
        "--input-dirs",
        nargs="+",
        required=True,
        type=Path,
        metavar="DIR",
        help="One or more directories containing *.jsonl.gz shards.",
    )
    parser.add_argument(
        "--output-dir",
        required=True,
        type=Path,
        help="Directory to write deduplicated shards.",
    )
    return parser


def main() -> int:
    """Entry point."""
    args = build_parser().parse_args()

    input_dirs: list[Path] = args.input_dirs
    output_dir: Path = args.output_dir

    for d in input_dirs:
        if not d.is_dir():
            print(f"ERROR: not a directory: {d}", file=sys.stderr)
            return 1

    shards = collect_shards(input_dirs)
    if not shards:
        print("ERROR: no *.jsonl.gz shards found in input dirs.", file=sys.stderr)
        return 1

    print(f"Found {len(shards)} shard(s) across {len(input_dirs)} director(y/ies).")
    total, duplicates, kept = dedup_shards(shards, output_dir)

    dup_rate = duplicates / total * 100 if total else 0.0

    print("\nDeduplication summary")
    print(f"  Total docs processed : {total:,}")
    print(f"  Duplicates removed   : {duplicates:,}")
    print(f"  Kept docs            : {kept:,}")
    print(f"  Duplicate rate       : {dup_rate:.2f}%")
    print(f"  Output directory     : {output_dir}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
