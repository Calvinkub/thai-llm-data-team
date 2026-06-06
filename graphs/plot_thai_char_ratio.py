"""
Plot Thai character ratio distribution for web sources.

This script visualizes the distribution of Thai character ratios across documents
from web sources in the pretraining corpus. Includes a quality filter threshold
at 0.50 (50% Thai characters) to show which documents pass quality gating.

Uses mock data: normal distribution centered at 0.72 (mean Thai character ratio)
with standard deviation of 0.15.
"""

from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import numpy as np


def generate_mock_thai_ratio_data():
    """
    Generate mock Thai character ratio data.

    Returns array of ratios (0.0 to 1.0) representing the proportion of Thai
    characters in each web document. Uses normal distribution.
    """
    np.random.seed(42)

    # Normal distribution: mean=0.72, std=0.15
    # Representative of typical web sources with mixed Thai and English content
    thai_ratios = np.random.normal(loc=0.72, scale=0.15, size=5000)

    # Clip to [0, 1] bounds
    thai_ratios = np.clip(thai_ratios, 0, 1.0)

    return thai_ratios


def load_thai_ratio_data():
    """
    Load Thai character ratio data from file or generate mock data.

    Looks for a JSON or CSV file with thai_ratios. Falls back to mock data
    if file not found.
    """
    data_file = Path(__file__).parent / "thai_ratios.json"

    if data_file.exists():
        try:
            import json
            with open(data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, dict) and 'ratios' in data:
                    return np.array(data['ratios'])
                elif isinstance(data, list):
                    return np.array(data)
        except Exception as e:
            print(f"Warning: Could not read thai_ratios.json: {e}. Using mock data.")

    return generate_mock_thai_ratio_data()


def create_output_dir():
    """Create output directory if it doesn't exist."""
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)
    return output_dir


def plot_thai_char_ratio():
    """Generate histogram showing Thai character ratio distribution."""
    thai_ratios = load_thai_ratio_data()

    # Set style
    plt.style.use('seaborn-v0_8-whitegrid')

    fig, ax = plt.subplots(figsize=(12, 6))

    # Histogram
    counts, bins, patches = ax.hist(
        thai_ratios,
        bins=40,
        color='#4ECDC4',
        edgecolor='black',
        alpha=0.75,
        linewidth=1.2
    )

    # Quality threshold line (0.50)
    threshold = 0.50
    ax.axvline(threshold, color='#FF6B6B', linestyle='--', linewidth=2.5,
              label=f'Quality Filter Threshold ({threshold})')

    # Mean line
    mean_ratio = np.mean(thai_ratios)
    ax.axvline(mean_ratio, color='#2C3E50', linestyle='-', linewidth=2.0,
              label=f'Mean Ratio ({mean_ratio:.2f})')

    ax.set_xlabel('Thai Character Ratio', fontsize=12, fontweight='bold')
    ax.set_ylabel('Document Count', fontsize=12, fontweight='bold')
    ax.set_title('Thai Character Ratio Distribution (Web Sources)', fontsize=13, fontweight='bold', pad=15)
    ax.legend(fontsize=10, loc='upper right')
    ax.grid(True, alpha=0.3)

    # Calculate statistics
    below_threshold = np.sum(thai_ratios < threshold)
    above_threshold = np.sum(thai_ratios >= threshold)
    pct_pass = 100 * above_threshold / len(thai_ratios)

    # Add statistics box
    stats_text = (
        f'Total documents: {len(thai_ratios):,}\n'
        f'Mean ratio: {mean_ratio:.3f}\n'
        f'Std deviation: {np.std(thai_ratios):.3f}\n'
        f'Median: {np.median(thai_ratios):.3f}\n\n'
        f'Pass QA filter (>=0.50): {above_threshold:,} ({pct_pass:.1f}%)\n'
        f'Fail QA filter (<0.50): {below_threshold:,} ({100-pct_pass:.1f}%)'
    )
    ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, fontsize=9,
           verticalalignment='top', horizontalalignment='left',
           bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.7, pad=0.8),
           family='monospace')

    plt.tight_layout()

    output_dir = create_output_dir()
    output_path = output_dir / "thai_char_ratio.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Saved: {output_path}")
    plt.close()


if __name__ == "__main__":
    plot_thai_char_ratio()
