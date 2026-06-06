"""Converts a raw dataset shard into the Thai Foundation LLM unified schema."""

from __future__ import annotations

import argparse
import gzip
import json
import sys
import unicodedata
from pathlib import Path
from typing import Any, Iterator

from tqdm import tqdm

# ------------------------------------------------------------------
# Constants
# ------------------------------------------------------------------

VALID_SOURCES: set[str] = {"seapile", "thaillm", "thestack_v2", "finemath"}

SOURCE_DOMAIN_MAP: dict[str, str] = {
    "seapile": "web",
    "thaillm": "web",
    "thestack_v2": "code",
    "finemath": "math",
}

ZERO_WIDTH_CHARS: str = "​‌‍﻿"

# ------------------------------------------------------------------
# Text cleaning
# ------------------------------------------------------------------


def clean_text(raw: str) -> str:
    """Apply NFC normalization and strip zero-width characters."""
    cleaned = unicodedata.normalize("NFC", raw)
    cleaned = cleaned.translate(str.maketrans("", "", ZERO_WIDTH_CHARS))
    return cleaned


def extract_text(doc: dict[str, Any]) -> str | None:
    """Extract raw text from a doc using known field names across sources."""
    for field in ("text", "content"):
        value = doc.get(field)
        if isinstance(value, str):
            return value
    return None


# ------------------------------------------------------------------
# Schema builder
# ------------------------------------------------------------------


def build_schema_doc(
    raw_doc: dict[str, Any],
    source: str,
    stem: str,
    index: int,
) -> dict[str, Any] | None:
    """Map a raw document to the unified schema. Returns None to skip."""
    raw_text = extract_text(raw_doc)
    if raw_text is None:
        return None

    text = clean_text(raw_text)

    if not text.strip():
        return None

    n_chars = len(text)
    n_words = len(text.split())

    return {
        "id": f"{source}_{stem}_{index:06d}",
        "source": source,
        "license": raw_doc.get("license", "unknown"),
        "text": text,
        "n_chars": n_chars,
        "n_words": n_words,
        "quality_flags": raw_doc.get("quality_flags", []),
        "dup_group": raw_doc.get("dup_group", None),
        "domain": SOURCE_DOMAIN_MAP[source],
        "meta": {k: v for k, v in raw_doc.items() if k not in ("text", "content", "license")},
    }


# ------------------------------------------------------------------
# I/O helpers
# ------------------------------------------------------------------


def iter_jsonl_gz(path: Path) -> Iterator[dict[str, Any]]:
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


def write_jsonl_gz(path: Path, docs: list[dict[str, Any]]) -> None:
    """Write documents as JSONL.gz to path."""
    with gzip.open(path, "wt", encoding="utf-8") as fh:
        for doc in docs:
            fh.write(json.dumps(doc, ensure_ascii=False) + "\n")


# ------------------------------------------------------------------
# CLI
# ------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    """Build argument parser."""
    parser = argparse.ArgumentParser(
        description="Convert a raw shard to the Thai Foundation LLM unified schema."
    )
    parser.add_argument(
        "--source",
        required=True,
        choices=sorted(VALID_SOURCES),
        help="Dataset source identifier.",
    )
    parser.add_argument("--input", required=True, type=Path, help="Path to raw .jsonl.gz shard.")
    parser.add_argument("--output", required=True, type=Path, help="Path for output .jsonl.gz shard.")
    return parser


def main() -> int:
    """Entry point."""
    args = build_parser().parse_args()

    input_path: Path = args.input
    output_path: Path = args.output
    source: str = args.source

    if not input_path.exists():
        print(f"ERROR: input not found: {input_path}", file=sys.stderr)
        return 1

    output_path.parent.mkdir(parents=True, exist_ok=True)
    stem = input_path.stem.replace(".jsonl", "")

    total = 0
    skipped = 0
    kept_docs: list[dict[str, Any]] = []

    print(f"Converting {input_path.name} (source={source}) ...")

    for raw_doc in tqdm(iter_jsonl_gz(input_path), desc="docs", unit="doc"):
        total += 1
        schema_doc = build_schema_doc(raw_doc, source, stem, total)
        if schema_doc is None:
            skipped += 1
            continue
        kept_docs.append(schema_doc)

    write_jsonl_gz(output_path, kept_docs)

    kept = len(kept_docs)
    print(f"\nSummary")
    print(f"  Input docs   : {total:,}")
    print(f"  Skipped      : {skipped:,}  (empty or no text field)")
    print(f"  Written      : {kept:,}")
    print(f"  Output path  : {output_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
