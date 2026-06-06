"""Generate a manifest.json and SHA256SUMS file for Thai LLM JSONL.gz shards."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

from tqdm import tqdm

# ------------------------------------------------------------------
# Constants
# ------------------------------------------------------------------

TOKENS_PER_CHAR: float = 1 / 3.5

# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------


def sha256_file(path: Path, chunk_size: int = 1 << 20) -> str:
    """Return hex SHA-256 digest of a file by streaming in chunks."""
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        while chunk := fh.read(chunk_size):
            h.update(chunk)
    return h.hexdigest()


def collect_shards(root: Path) -> list[Path]:
    """Return sorted list of all *.jsonl.gz files under root."""
    return sorted(root.rglob("*.jsonl.gz"))


def load_stats_sidecar(shard_path: Path) -> dict[str, Any] | None:
    """Load a .stats.json sidecar if present alongside the shard."""
    sidecar = shard_path.with_suffix("").with_suffix(".stats.json")
    if sidecar.exists():
        try:
            return json.loads(sidecar.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return None
    return None


def compute_shard_stats_inline(shard_path: Path) -> dict[str, Any]:
    """Read shard and compute doc_count, total_chars, source counts inline."""
    doc_count = 0
    total_chars = 0
    source_counts: dict[str, int] = {}

    with gzip.open(shard_path, "rt", encoding="utf-8") as fh:
        for raw in fh:
            raw = raw.strip()
            if not raw:
                continue
            try:
                doc = json.loads(raw)
            except json.JSONDecodeError:
                continue
            doc_count += 1
            text = doc.get("text", "")
            total_chars += doc.get("n_chars", len(text))
            src = doc.get("source", "unknown")
            source_counts[src] = source_counts.get(src, 0) + 1

    return {
        "doc_count": doc_count,
        "total_chars": total_chars,
        "source_counts": source_counts,
    }


# ------------------------------------------------------------------
# Manifest builder
# ------------------------------------------------------------------


def build_manifest(shards: list[Path], shards_dir: Path) -> dict[str, Any]:
    """Build the full manifest structure from a list of shard paths."""
    total_docs = 0
    total_chars = 0
    per_source: dict[str, dict[str, int]] = {}
    shard_list: list[dict[str, Any]] = []

    for shard_path in tqdm(shards, desc="shards", unit="shard"):
        sidecar = load_stats_sidecar(shard_path)
        if sidecar:
            stats = sidecar
        else:
            stats = compute_shard_stats_inline(shard_path)

        checksum = sha256_file(shard_path)
        rel_path = str(shard_path.relative_to(shards_dir))
        size_bytes = shard_path.stat().st_size

        doc_count: int = stats.get("doc_count", 0)
        shard_chars: int = stats.get("total_chars", 0)
        source_counts: dict[str, int] = stats.get("source_counts", {})

        total_docs += doc_count
        total_chars += shard_chars

        for src, cnt in source_counts.items():
            if src not in per_source:
                per_source[src] = {"doc_count": 0, "total_chars": 0}
            per_source[src]["doc_count"] += cnt
            # Approximate chars per source proportionally
            if doc_count > 0:
                per_source[src]["total_chars"] += int(shard_chars * cnt / doc_count)

        shard_list.append(
            {
                "path": rel_path,
                "size_bytes": size_bytes,
                "doc_count": doc_count,
                "total_chars": shard_chars,
                "sha256": checksum,
                "source_counts": source_counts,
            }
        )

    # Add estimated_tokens to per_source
    for src in per_source:
        per_source[src]["estimated_tokens"] = int(per_source[src]["total_chars"] * TOKENS_PER_CHAR)

    return {
        "total_docs": total_docs,
        "total_chars": total_chars,
        "estimated_tokens": int(total_chars * TOKENS_PER_CHAR),
        "per_source": per_source,
        "shard_count": len(shard_list),
        "shard_list": shard_list,
    }


def write_sha256sums(shard_list: list[dict[str, Any]], output_dir: Path) -> Path:
    """Write a SHA256SUMS file next to manifest.json."""
    sums_path = output_dir / "SHA256SUMS"
    lines = [f"{s['sha256']}  {s['path']}" for s in shard_list]
    sums_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return sums_path


# ------------------------------------------------------------------
# CLI
# ------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    """Build argument parser."""
    parser = argparse.ArgumentParser(
        description="Generate manifest.json and SHA256SUMS for all JSONL.gz shards."
    )
    parser.add_argument("--shards-dir", required=True, type=Path, help="Root directory of shards.")
    parser.add_argument("--output", required=True, type=Path, help="Path for output manifest.json.")
    return parser


def main() -> int:
    """Entry point."""
    args = build_parser().parse_args()
    shards_dir: Path = args.shards_dir
    output_path: Path = args.output

    if not shards_dir.is_dir():
        print(f"ERROR: not a directory: {shards_dir}", file=sys.stderr)
        return 1

    shards = collect_shards(shards_dir)
    if not shards:
        print("ERROR: no *.jsonl.gz shards found.", file=sys.stderr)
        return 1

    print(f"Found {len(shards)} shard(s). Building manifest ...")

    manifest = build_manifest(shards, shards_dir)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")

    sums_path = write_sha256sums(manifest["shard_list"], output_path.parent)

    print(f"\nManifest summary")
    print(f"  Total docs       : {manifest['total_docs']:,}")
    print(f"  Total chars      : {manifest['total_chars']:,}")
    print(f"  Est. tokens      : {manifest['estimated_tokens']:,}")
    print(f"  Shards           : {manifest['shard_count']}")
    print(f"  manifest.json    : {output_path}")
    print(f"  SHA256SUMS       : {sums_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
