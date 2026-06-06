"""Preprocess The Stack V2 parquet files -> unified schema parquet.

The Stack V2 is a source-code corpus. This script:
  1. Reads raw parquet shards (field: content or text)
  2. Optionally filters to specific programming languages
  3. Drops empty files and very large files (>1 MB — likely auto-generated)
  4. Applies cleaning (NFC, zero-width strip) -- no Thai spam filter (code domain)
  5. Writes clean unified-schema parquet

Usage:
    python preprocess_thestack_v2.py --input /mnt/ssd/data/thestack_v2/ --output /mnt/ssd/shards/thestack_v2/

    # Filter to specific languages (optional, comma-separated):
    python preprocess_thestack_v2.py --input ... --output ... --langs python,javascript,typescript
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from tqdm import tqdm

from parquet_utils import build_doc, iter_parquet_files, read_parquet, write_parquet

SOURCE = "thestack_v2"
MIN_TEXT_LEN  = 30       # code files can be very short; keep tiny snippets
MAX_TEXT_CHARS = 1_000_000  # 1 MB text - skip auto-generated/minified blobs

# Languages to keep. Empty set = keep all.
DEFAULT_LANGS: set[str] = set()


def process_shard(
    raw_path: Path,
    out_path: Path,
    keep_langs: set[str],
) -> dict:
    rows = read_parquet(raw_path)
    stem = raw_path.stem

    docs = []
    skipped_empty    = 0
    skipped_too_big  = 0
    skipped_lang     = 0

    for i, row in enumerate(rows):
        # Stack V2 field names: content or text; lang field: programming_language or lang
        text = row.get("content") or row.get("text") or ""
        if not isinstance(text, str):
            text = str(text) if text else ""

        if len(text.strip()) < MIN_TEXT_LEN:
            skipped_empty += 1
            continue

        if len(text) > MAX_TEXT_CHARS:
            skipped_too_big += 1
            continue

        lang = str(row.get("programming_language") or row.get("lang") or "unknown")
        if keep_langs and lang.lower() not in keep_langs:
            skipped_lang += 1
            continue

        doc = build_doc(
            text=text,
            source=SOURCE,
            shard_id=stem,
            index=i,
            license_str=str(row.get("license", "unknown")),
            extra={
                "lang":     lang,
                "filename": str(row.get("filename") or row.get("max_stars_repo_name", "")),
                "size":     row.get("size", len(text)),
            },
        )
        docs.append(doc)

    # No spam filter for code - spam filter is Thai/gambling specific
    write_parquet(docs, out_path)

    return {
        "shard":            raw_path.name,
        "rows_in":          len(rows),
        "skipped_empty":    skipped_empty,
        "skipped_too_big":  skipped_too_big,
        "skipped_lang":     skipped_lang,
        "clean":            len(docs),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Preprocess The Stack V2 parquet shards.")
    parser.add_argument("--input",  required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument(
        "--langs",
        default="",
        help="Comma-separated programming languages to keep. Default: all.",
    )
    args = parser.parse_args()

    keep_langs: set[str] = (
        {l.strip().lower() for l in args.langs.split(",") if l.strip()}
        if args.langs else set()
    )

    files = iter_parquet_files(args.input)
    if not files:
        print(f"ERROR: no parquet files found in {args.input}", file=sys.stderr)
        return 1

    args.output.mkdir(parents=True, exist_ok=True)
    total = {"rows_in": 0, "skipped_empty": 0, "skipped_too_big": 0, "skipped_lang": 0, "clean": 0}

    for raw_path in tqdm(files, desc="thestack_v2 shards"):
        out_path = args.output / raw_path.name
        stats = process_shard(raw_path, out_path, keep_langs)
        for k in total:
            total[k] += stats[k]

    print(f"\nThe Stack V2 Summary")
    print(f"  Shards         : {len(files)}")
    print(f"  Rows in        : {total['rows_in']:,}")
    print(f"  Skipped empty  : {total['skipped_empty']:,}")
    print(f"  Skipped too big: {total['skipped_too_big']:,}  (> {MAX_TEXT_CHARS // 1000}k chars)")
    print(f"  Skipped lang   : {total['skipped_lang']:,}  (lang filter active: {bool(keep_langs)})")
    print(f"  Clean out      : {total['clean']:,}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
