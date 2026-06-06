"""Validates a JSONL.gz shard against the Thai Foundation LLM unified schema."""

from __future__ import annotations

import argparse
import gzip
import json
import sys
import unicodedata
from collections import defaultdict
from pathlib import Path
from typing import Any

# ------------------------------------------------------------------
# Constants
# ------------------------------------------------------------------

REQUIRED_FIELDS: set[str] = {
    "id",
    "source",
    "license",
    "text",
    "n_chars",
    "n_words",
    "quality_flags",
    "dup_group",
    "domain",
}

VALID_SOURCES: set[str] = {"seapile", "thaillm", "thestack_v2", "finemath"}
VALID_DOMAINS: set[str] = {"web", "code", "math"}

ZERO_WIDTH_CHARS: set[str] = {"​", "‌", "‍", "﻿"}


# ------------------------------------------------------------------
# Validation helpers
# ------------------------------------------------------------------


def check_required_fields(doc: dict[str, Any], errors: list[str]) -> None:
    """Append errors for any missing required fields."""
    for field in REQUIRED_FIELDS:
        if field not in doc:
            errors.append(f"missing_field:{field}")


def check_text(doc: dict[str, Any], errors: list[str]) -> None:
    """Validate text encoding, NFC normalization, and zero-width chars."""
    text = doc.get("text")
    if not isinstance(text, str):
        errors.append("text_not_string")
        return

    # UTF-8 round-trip check
    try:
        text.encode("utf-8").decode("utf-8")
    except UnicodeDecodeError:
        errors.append("text_not_utf8")

    # NFC normalization check
    if unicodedata.normalize("NFC", text) != text:
        errors.append("text_not_nfc")

    # Zero-width char check
    for ch in ZERO_WIDTH_CHARS:
        if ch in text:
            errors.append(f"zero_width_char:U+{ord(ch):04X}")


def check_source(doc: dict[str, Any], errors: list[str]) -> None:
    """Validate source enum value."""
    source = doc.get("source")
    if source not in VALID_SOURCES:
        errors.append(f"invalid_source:{source!r}")


def check_domain(doc: dict[str, Any], errors: list[str]) -> None:
    """Validate domain enum value."""
    domain = doc.get("domain")
    if domain not in VALID_DOMAINS:
        errors.append(f"invalid_domain:{domain!r}")


def check_n_chars(doc: dict[str, Any], errors: list[str]) -> None:
    """Validate that n_chars matches len(text)."""
    text = doc.get("text")
    n_chars = doc.get("n_chars")
    if not isinstance(text, str) or not isinstance(n_chars, int):
        return
    actual = len(text)
    if actual != n_chars:
        errors.append(f"n_chars_mismatch:declared={n_chars},actual={actual}")


def validate_doc(doc: dict[str, Any]) -> list[str]:
    """Run all checks on a single document, return list of error strings."""
    errors: list[str] = []
    check_required_fields(doc, errors)
    check_text(doc, errors)
    check_source(doc, errors)
    check_domain(doc, errors)
    check_n_chars(doc, errors)
    return errors


# ------------------------------------------------------------------
# Shard reader
# ------------------------------------------------------------------


def iter_shard(path: Path):
    """Yield (line_number, doc_dict) from a JSONL.gz file."""
    with gzip.open(path, "rt", encoding="utf-8") as fh:
        for lineno, raw in enumerate(fh, start=1):
            raw = raw.strip()
            if not raw:
                continue
            try:
                yield lineno, json.loads(raw)
            except json.JSONDecodeError as exc:
                yield lineno, {"__parse_error__": str(exc)}


# ------------------------------------------------------------------
# CLI
# ------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser."""
    parser = argparse.ArgumentParser(
        description="Validate a Thai LLM JSONL.gz shard against the unified schema."
    )
    parser.add_argument("--shard", required=True, type=Path, help="Path to shard.jsonl.gz")
    parser.add_argument(
        "--source",
        choices=sorted(VALID_SOURCES),
        help="Expected source (optional cross-check).",
    )
    return parser


def print_summary_table(
    total: int,
    error_count: int,
    error_types: dict[str, int],
    passed: bool,
) -> None:
    """Print a clean summary table to stdout."""
    status_str = "PASS" if passed else "FAIL"
    sep = "-" * 52
    print(sep)
    print(f"  Validation result : {status_str}")
    print(f"  Total documents   : {total:,}")
    print(f"  Documents with errors: {error_count:,}")
    dup_rate = error_count / total * 100 if total else 0.0
    print(f"  Error rate        : {dup_rate:.2f}%")
    if error_types:
        print(sep)
        print("  Error breakdown:")
        for etype, cnt in sorted(error_types.items(), key=lambda x: -x[1]):
            print(f"    {etype:<40s} {cnt:>6,}")
    print(sep)


def main() -> int:
    """Entry point; returns exit code."""
    args = build_parser().parse_args()
    shard_path: Path = args.shard

    if not shard_path.exists():
        print(f"ERROR: shard not found: {shard_path}", file=sys.stderr)
        return 1

    total = 0
    error_count = 0
    error_types: dict[str, int] = defaultdict(int)

    for lineno, doc in iter_shard(shard_path):
        total += 1

        if "__parse_error__" in doc:
            error_count += 1
            error_types[f"json_parse_error:line={lineno}"] += 1
            continue

        # Optional source cross-check
        if args.source and doc.get("source") != args.source:
            error_types[f"source_mismatch:expected={args.source}"] += 1

        doc_errors = validate_doc(doc)
        if doc_errors:
            error_count += 1
            for err in doc_errors:
                error_types[err] += 1

    passed = error_count == 0
    print_summary_table(total, error_count, dict(error_types), passed)
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
