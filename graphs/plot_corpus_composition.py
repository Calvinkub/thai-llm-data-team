"""
Plot corpus composition by source dataset.

This script visualizes the token distribution and document count across the four
source datasets (THAILLM, SEAPILE, The Stack V2, FineMath) used in the pretraining corpus.

Reads from manifest.json if available, otherwise uses mock data.
Generates two subplots: pie chart of token share and bar chart of document counts.
"""

import json
import os
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import numpy as np


def load_manifest_data():
    """
    Load corpus composition data from manifest.json.

    Returns a dict with 'sources' containing {name, tokens, docs}.
    Falls back to mock data if file not found.
    """
    manifest_path = Path(__file__).parent / "manifest.json"

    if manifest_path.exists():
        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if 'sources' in data:
                    return data
        except Exception as e:
            print(f"Warning: Could not read manifest.json: {e}. Using mock data.")

    # Mock data: 20B token corpus
    mock_data = {
        'sources': [
            {'name': 'THAILLM', 'tokens': 7_000_000_000, 'docs': 450_000},
            {'name': 'SEAPILE', 'tokens': 5_000_000_000, 'docs': 320_000},
            {'name': 'The Stack V2', 'tokens': 5_000_000_000, 'docs': 280_000},
            {'name': 'FineMath', 'tokens': 3_000_000_000, 'docs': 150_000},
        ]
    }
    return mock_data


def create_output_dir():
    """Create output directory if it doesn't exist."""
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)
    return output_dir


def plot_corpus_composition():
    """Generate pie and bar charts for corpus composition."""
    data = load_manifest_data()
    sources = data['sources']

    names = [s['name'] for s in sources]
    tokens = [s['tokens'] for s in sources]
    docs = [s['docs'] for s in sources]

    # Set style
    plt.style.use('seaborn-v0_8-whitegrid')
    sns.set_palette("husl")

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    # Pie chart: token share
    colors = sns.color_palette("husl", len(names))
    wedges, texts, autotexts = ax1.pie(
        tokens,
        labels=names,
        autopct='%1.1f%%',
        colors=colors,
        startangle=90,
        textprops={'fontsize': 10}
    )
    ax1.set_title('Token Share by Source', fontsize=12, fontweight='bold', pad=20)

    # Make percentage text bold and readable
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')
        autotext.set_fontsize(9)

    # Bar chart: document count
    bars = ax2.bar(names, docs, color=colors, edgecolor='black', linewidth=1.2)
    ax2.set_ylabel('Document Count', fontsize=11, fontweight='bold')
    ax2.set_title('Document Count by Source', fontsize=12, fontweight='bold', pad=20)
    ax2.grid(axis='y', alpha=0.3)

    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        ax2.text(
            bar.get_x() + bar.get_width() / 2,
            height,
            f'{int(height):,}',
            ha='center',
            va='bottom',
            fontsize=9,
            fontweight='bold'
        )

    # Rotate x labels
    ax2.set_xticklabels(names, rotation=15, ha='right')

    plt.tight_layout()

    output_dir = create_output_dir()
    output_path = output_dir / "corpus_composition.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Saved: {output_path}")
    plt.close()


if __name__ == "__main__":
    plot_corpus_composition()
