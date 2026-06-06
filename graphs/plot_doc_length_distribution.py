"""
Plot document length distribution across source datasets.

This script visualizes the distribution of document lengths (in characters)
from the pretraining corpus. Shows both a histogram with log-scale x-axis
and box plots per source to reveal distribution differences.

Reads from shard files if available, otherwise uses mock data.
"""

import json
import os
from pathlib import Path

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np


def generate_mock_doc_lengths():
    """
    Generate mock document length data with realistic distributions per source.

    Returns a dict mapping source names to lists of document lengths (in chars).
    """
    np.random.seed(42)

    mock_data = {
        'THAILLM': np.random.gamma(shape=3, scale=1500, size=10000).astype(int),
        'SEAPILE': np.random.gamma(shape=2.5, scale=2000, size=8000).astype(int),
        'The Stack V2': np.random.gamma(shape=2, scale=2500, size=8000).astype(int),
        'FineMath': np.random.gamma(shape=3.5, scale=1200, size=5000).astype(int),
    }

    # Clip to realistic bounds (10 chars to 1M chars)
    for source in mock_data:
        mock_data[source] = np.clip(mock_data[source], 10, 1_000_000)

    return mock_data


def load_shard_data():
    """
    Load document length data from shard files or generate mock data.

    Looks for shard files in a standard location. Falls back to mock data
    if shards are not found.
    """
    shard_dir = Path(__file__).parent / "shards"

    if shard_dir.exists():
        try:
            doc_lengths = {}
            for shard_file in shard_dir.glob("*.jsonl"):
                source_name = shard_file.stem
                lengths = []
                with open(shard_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        obj = json.loads(line)
                        if 'text' in obj:
                            lengths.append(len(obj['text']))
                if lengths:
                    doc_lengths[source_name] = np.array(lengths)
            if doc_lengths:
                return doc_lengths
        except Exception as e:
            print(f"Warning: Could not read shard files: {e}. Using mock data.")

    return generate_mock_doc_lengths()


def create_output_dir():
    """Create output directory if it doesn't exist."""
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)
    return output_dir


def plot_doc_length_distribution():
    """Generate histogram and box plot for document length distributions."""
    doc_lengths = load_shard_data()

    # Set style
    plt.style.use('seaborn-v0_8-whitegrid')
    sns.set_palette("husl")

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))

    # Combine all lengths for overall histogram
    all_lengths = np.concatenate(list(doc_lengths.values()))

    # Histogram with log scale x-axis
    counts, bins, patches = ax1.hist(
        all_lengths,
        bins=50,
        color='steelblue',
        edgecolor='black',
        alpha=0.7
    )
    ax1.set_xscale('log')
    ax1.set_xlabel('Document Length (characters, log scale)', fontsize=11, fontweight='bold')
    ax1.set_ylabel('Frequency', fontsize=11, fontweight='bold')
    ax1.set_title('Overall Document Length Distribution (All Sources)', fontsize=12, fontweight='bold', pad=15)
    ax1.grid(True, alpha=0.3)

    # Add statistics text
    stats_text = f"Total docs: {len(all_lengths):,}\nMean: {np.mean(all_lengths):,.0f}\nMedian: {np.median(all_lengths):,.0f}"
    ax1.text(0.98, 0.97, stats_text, transform=ax1.transAxes, fontsize=9,
             verticalalignment='top', horizontalalignment='right',
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    # Box plot per source
    sources = list(doc_lengths.keys())
    data_for_box = [doc_lengths[s] for s in sources]
    colors = sns.color_palette("husl", len(sources))

    bp = ax2.boxplot(
        data_for_box,
        labels=sources,
        patch_artist=True,
        widths=0.6
    )

    # Color the boxes
    for patch, color in zip(bp['boxes'], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)

    ax2.set_ylabel('Document Length (characters)', fontsize=11, fontweight='bold')
    ax2.set_title('Document Length Distribution by Source', fontsize=12, fontweight='bold', pad=15)
    ax2.set_yscale('log')
    ax2.grid(axis='y', alpha=0.3)
    ax2.set_xticklabels(sources, rotation=15, ha='right')

    plt.tight_layout()

    output_dir = create_output_dir()
    output_path = output_dir / "doc_length_dist.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Saved: {output_path}")
    plt.close()


if __name__ == "__main__":
    plot_doc_length_distribution()
