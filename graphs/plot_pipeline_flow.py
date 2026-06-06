"""
Generate pipeline flow diagram for the Thai LLM data processing pipeline.

Visualizes the data flow from raw datasets through validation, schema conversion,
deduplication, QA gating, and handoff to model training. Includes estimated
token counts at each stage.

Uses matplotlib patches to create a clean, publication-quality diagram.
"""

from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np


def create_output_dir():
    """Create output directory if it doesn't exist."""
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)
    return output_dir


def plot_pipeline_flow():
    """Generate pipeline flow diagram with token counts."""
    fig, ax = plt.subplots(figsize=(16, 8))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis('off')

    # Define pipeline stages with token counts
    stages = [
        {'label': 'SSD\n(4 Datasets)', 'x': 0.8, 'tokens': '22.0B', 'color': '#FF6B6B', 'width': 1.2},
        {'label': 'Validate', 'x': 2.4, 'tokens': '21.5B', 'color': '#4ECDC4', 'width': 1.0},
        {'label': 'Convert\nSchema', 'x': 3.8, 'tokens': '21.5B', 'color': '#45B7D1', 'width': 1.0},
        {'label': 'Cross\nDedup', 'x': 5.2, 'tokens': '20.7B', 'color': '#96CEB4', 'width': 1.0},
        {'label': 'QA Gate', 'x': 6.6, 'tokens': '20.2B', 'color': '#FFEAA7', 'width': 1.0},
        {'label': 'Handoff', 'x': 8.0, 'tokens': '20.0B', 'color': '#DDA0DD', 'width': 1.0},
        {'label': 'Model\nTeam', 'x': 9.2, 'tokens': '20.0B', 'color': '#B19CD9', 'width': 1.2},
    ]

    # Draw stage boxes and labels
    for stage in stages:
        x = stage['x']
        width = stage['width']
        height = 1.8

        # Draw fancy box
        box = FancyBboxPatch(
            (x - width / 2, 2.1),
            width,
            height,
            boxstyle="round,pad=0.1",
            linewidth=2.5,
            edgecolor='black',
            facecolor=stage['color'],
            alpha=0.85
        )
        ax.add_patch(box)

        # Stage label
        ax.text(x, 3.2, stage['label'], ha='center', va='center',
               fontsize=10, fontweight='bold', family='monospace')

        # Token count
        ax.text(x, 2.4, stage['tokens'], ha='center', va='center',
               fontsize=9, fontweight='bold', style='italic')

    # Draw arrows between stages
    for i in range(len(stages) - 1):
        x1 = stages[i]['x'] + stages[i]['width'] / 2
        x2 = stages[i + 1]['x'] - stages[i + 1]['width'] / 2
        y = 3.0

        arrow = FancyArrowPatch(
            (x1, y),
            (x2, y),
            arrowstyle='->,head_width=0.4,head_length=0.4',
            linewidth=2.5,
            color='#2C3E50',
            mutation_scale=25
        )
        ax.add_patch(arrow)

    # Add title and legend
    ax.text(5, 5.4, 'Thai LLM Data Processing Pipeline', ha='center', va='center',
           fontsize=16, fontweight='bold')

    # Add summary statistics box
    summary_text = (
        'Pipeline Summary:\n'
        '600 GB SSD input\n'
        '4 source datasets\n'
        '1.8% token loss through filtering\n'
        '~20B token pretraining corpus'
    )
    ax.text(0.5, 0.8, summary_text, fontsize=9, verticalalignment='top',
           bbox=dict(boxstyle='round', facecolor='#F0F0F0', alpha=0.8, pad=0.8),
           family='monospace')

    # Add processing notes
    notes_text = (
        'Processing Details:\n'
        'Validate: Format & integrity checks\n'
        'Convert: Unified schema application\n'
        'Dedup: Cross-source deduplication\n'
        'QA: Quality gating & filtering'
    )
    ax.text(9.5, 0.8, notes_text, fontsize=8, verticalalignment='top',
           horizontalalignment='right',
           bbox=dict(boxstyle='round', facecolor='#F0F0F0', alpha=0.8, pad=0.8),
           family='monospace')

    plt.tight_layout()

    output_dir = create_output_dir()
    output_path = output_dir / "pipeline_flow.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"Saved: {output_path}")
    plt.close()


if __name__ == "__main__":
    plot_pipeline_flow()
