"""Shared utilities for parquet-based preprocessing pipeline."""

from __future__ import annotations

import hashlib
import re
import unicodedata
from pathlib import Path
from typing import Any

ZERO_WIDTH_CHARS: str = "​‌‍﻿"
_THAI_RE = re.compile(r"[฀-๿]")

VALID_SOURCES = {"seapile", "thaillm", "thestack_v2", "finemath"}
SOURCE_DOMAIN: dict[str, str] = {
    "seapile":     "web",
    "thaillm":     "web",
    "thestack_v2": "code",
    "finemath":    "math",
}


def clean_text(text: str) -> str:
    """NFC normalize and strip zero-width characters."""
    text = unicodedata.normalize("NFC", text)
    return text.translate(str.maketrans("", "", ZERO_WIDTH_CHARS))


def thai_ratio(text: str) -> float:
    """Fraction of characters that are Thai script."""
    if not text:
        return 0.0
    return len(_THAI_RE.findall(text)) / len(text)


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def build_doc(
    text: str,
    source: str,
    shard_id: str,
    index: int,
    license_str: str = "unknown",
    quality_flags: list[str] | None = None,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a unified schema document dict."""
    text = clean_text(text)
    doc: dict[str, Any] = {
        "id":            f"{source}_{shard_id}_{index:06d}",
        "source":        source,
        "license":       license_str,
        "text":          text,
        "n_chars":       len(text),
        "n_words":       len(text.split()),
        "quality_flags": quality_flags or [],
        "dup_group":     None,
        "domain":        SOURCE_DOMAIN[source],
    }
    if extra:
        doc["meta"] = extra
    return doc


def iter_parquet_files(directory: Path, glob: str = "*.parquet") -> list[Path]:
    """Return sorted parquet files under directory."""
    files = sorted(directory.glob(glob))
    if not files:
        files = sorted(directory.rglob(glob))
    return files


def write_parquet(docs: list[dict[str, Any]], out_path: Path) -> None:
    """Write list of dicts to a parquet file."""
    import pyarrow as pa
    import pyarrow.parquet as pq

    if not docs:
        return
    out_path.parent.mkdir(parents=True, exist_ok=True)
    table = pa.Table.from_pylist(docs)
    pq.write_table(table, out_path, compression="snappy")


def read_parquet(path: Path) -> list[dict[str, Any]]:
    """Read a parquet file into list of dicts."""
    import pyarrow.parquet as pq
    table = pq.read_table(path)
    return table.to_pylist()
