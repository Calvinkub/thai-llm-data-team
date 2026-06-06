"""Compute corpus statistics across all JSONL.gz shards in a directory tree."""

from __future__ import annotations

import argparse
import gzip
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

from tqdm import tqdm

# ------------------------------------------------------------------
# Constants
# ------------------------------------------------------------------

TOKENS_PER_CHAR: float = 1 / 3.5
THAI_CHAR_RANGE = range(0x0E00, 0x0E7F + 1)

# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------


def is_thai(ch: str) -> bool:
    """Return True if character is in the Thai Unicode block."""
    return ord(ch) in THAI_CHAR_RANGE


def thai_char_ratio(text: str) -> float:
    """Return fraction of characters that are Thai."""
    if not text:
        return 0.0
    thai_count = sum(1 for ch in text if is_thai(ch))
    return thai_count / len(text)


def percentile(sorted_values: list[float], p: float) -> float:
    """Return the p-th percentile from a sorted list (0-100)."""
    if not sorted_values:
        return 0.0
    idx = (p / 100) * (len(sorted_values) - 1)
    lo = int(idx)
    hi = min(lo + 1, len(sorted_values) - 1)
    frac = idx - lo
    return sorted_values[lo] * (1 - frac) + sorted_values[hi] * frac


def collect_shards(root: Path) -> list[Path]:
    """Return sorted list of all *.jsonl.gz under root."""
    return sorted(root.rglob("*.jsonl.gz"))


# ------------------------------------------------------------------
# Stats accumulator
# ------------------------------------------------------------------


class SourceStats:
    """Accumulates statistics for a single source."""

    def __init__(self) -> None:
        self.doc_count: int = 0
        self.total_chars: int = 0
        self.domain_counts: dict[str, int] = defaultdict(int)
        self.char_lengths: list[int] = []
        self.thai_ratios: list[float] = []

    def add(self, doc: dict[str, Any]) -> None:
        """Ingest one document into the accumulator."""
        text: str = doc.get("text", "")
        n_chars: int = doc.get("n_chars", len(text))
        domain: str = doc.get("domain", "unknown")

        self.doc_count += 1
        self.total_chars += n_chars
        self.domain_counts[domain] += 1
        self.char_lengths.append(n_chars)

        if domain == "web":
            self.thai_ratios.append(thai_char_ratio(text))

    @property
    def estimated_tokens(self) -> int:
        """Estimated token count using chars/3.5 heuristic."""
        return int(self.total_chars * TOKENS_PER_CHAR)

    def length_percentiles(self) -> dict[str, float]:
        """Return p25/p50/p75/p99 of document character lengths."""
        sv = sorted(self.char_lengths)
        return {
            "p25": percentile(sv, 25),
            "p50": percentile(sv, 50),
            "p75": percentile(sv, 75),
            "p99": percentile(sv, 99),
        }

    def thai_ratio_percentiles(self) -> dict[str, float]:
        """Return p25/p50/p75/p99 of Thai char ratio (web only)."""
        sv = sorted(self.thai_ratios)
        return {
            "p25": percentile(sv, 25),
            "p50": percentile(sv, 50),
            "p75": percentile(sv, 75),
            "p99": percentile(sv, 99),
        }


# ------------------------------------------------------------------
# Table printer
# ------------------------------------------------------------------


def print_ascii_table(per_source: dict[str, SourceStats]) -> None:
    """Print a formatted ASCII table of per-source corpus statistics."""
    col_w = [14, 12, 12, 14, 10]
    headers = ["Source", "Docs", "Chars (B)", "Est. Tokens", "Top Domain"]

    def row_str(cells: list[str]) -> str:
        return "  ".join(c.ljust(w) for c, w in zip(cells, col_w))

    sep = "-" * (sum(col_w) + 2 * len(col_w))
    print(sep)
    print(row_str(headers))
    print(sep)

    total_docs = 0
    total_chars = 0
    total_tokens = 0

    for source, stats in sorted(per_source.items()):
        chars_b = stats.total_chars / 1e9
        tokens_b = stats.estimated_tokens / 1e9
        top_domain = max(stats.domain_counts, key=stats.domain_counts.get, default="n/a")
        print(
            row_str(
                [
                    source,
                    f"{stats.doc_count:,}",
                    f"{chars_b:.3f}",
                    f"{tokens_b:.3f}",
                    top_domain,
                ]
            )
        )
        total_docs += stats.doc_count
        total_chars += stats.total_chars
        total_tokens += int(total_chars * TOKENS_PER_CHAR)

    print(sep)
    print(
        row_str(
            [
                "TOTAL",
                f"{total_docs:,}",
                f"{total_chars / 1e9:.3f}",
                f"{total_tokens / 1e9:.3f}",
                "",
            ]
        )
    )
    print(sep)

    # Doc length distribution
    print("\nDocument length distribution (chars):")
    print(f"  {'Source':<16} {'p25':>8} {'p50':>8} {'p75':>8} {'p99':>8}")
    for source, stats in sorted(per_source.items()):
        pct = stats.length_percentiles()
        print(
            f"  {source:<16} {pct['p25']:>8.0f} {pct['p50']:>8.0f} "
            f"{pct['p75']:>8.0f} {pct['p99']:>8.0f}"
        )

    # Thai ratio distribution for web sources
    web_sources = {s: st for s, st in per_source.items() if st.thai_ratios}
    if web_sources:
        print("\nThai char ratio distribution (web sources only):")
        print(f"  {'Source':<16} {'p25':>8} {'p50':>8} {'p75':>8} {'p99':>8}")
        for source, stats in sorted(web_sources.items()):
            pct = stats.thai_ratio_percentiles()
            print(
                f"  {source:<16} {pct['p25']:>8.3f} {pct['p50']:>8.3f} "
                f"{pct['p75']:>8.3f} {pct['p99']:>8.3f}"
            )


# ------------------------------------------------------------------
# CLI
# ------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    """Build argument parser."""
    parser = argparse.ArgumentParser(
        description="Compute corpus statistics across all JSONL.gz shards."
    )
    parser.add_argument("--shards-dir", required=True, type=Path, help="Root directory of shards.")
    parser.add_argument("--output", type=Path, default=None, help="Optional path to save stats.json.")
    return parser


def main() -> int:
    """Entry point."""
    args = build_parser().parse_args()
    shards_dir: Path = args.shards_dir
    output_path: Path | None = args.output

    if not shards_dir.is_dir():
        print(f"ERROR: not a directory: {shards_dir}", file=sys.stderr)
        return 1

    shards = collect_shards(shards_dir)
    if not shards:
        print("ERROR: no *.jsonl.gz shards found.", file=sys.stderr)
        return 1

    print(f"Found {len(shards)} shard(s) under {shards_dir}")

    per_source: dict[str, SourceStats] = defaultdict(SourceStats)

    for shard_path in tqdm(shards, desc="shards", unit="shard"):
        with gzip.open(shard_path, "rt", encoding="utf-8") as fh:
            for raw in fh:
                raw = raw.strip()
                if not raw:
                    continue
                try:
                    doc = json.loads(raw)
                except json.JSONDecodeError:
                    continue
                source = doc.get("source", "unknown")
                per_source[source].add(doc)

    print()
    print_ascii_table(dict(per_source))

    if output_path:
        result: dict[str, Any] = {}
        for source, stats in per_source.items():
            result[source] = {
                "doc_count": stats.doc_count,
                "total_chars": stats.total_chars,
                "estimated_tokens": stats.estimated_tokens,
                "domain_breakdown": dict(stats.domain_counts),
                "char_length_percentiles": stats.length_percentiles(),
                "thai_ratio_percentiles": stats.thai_ratio_percentiles() if stats.thai_ratios else {},
            }
        output_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"\nStats saved to {output_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
