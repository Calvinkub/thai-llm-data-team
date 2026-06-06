# Thai LLM Data Visualization Scripts

This directory contains Python visualization scripts for analyzing the Thai language model's pretraining corpus composition, document characteristics, and data processing pipeline.

## Overview

The Thai LLM project processed approximately 22 billion raw tokens from four source datasets (THAILLM, SEAPILE, The Stack V2, FineMath) sourced from a 600 GB SSD. These scripts visualize key aspects of the data processing workflow and corpus characteristics.

## Scripts

### 1. plot_corpus_composition.py

Visualizes the distribution of tokens and documents across the four source datasets.

**Output file:** `output/corpus_composition.png`

**What it shows:**
- Pie chart: Token share percentage by source (THAILLM 35%, SEAPILE 25%, Stack V2 25%, FineMath 15%)
- Bar chart: Total document count per source

**Data source:**
- Primary: `manifest.json` (if exists)
- Fallback: Mock data with realistic corpus statistics

**How to run:**
```bash
python plot_corpus_composition.py
```

**Expected output:**
- Figure with two subplots showing relative corpus composition
- PNG saved to output/ directory at 300 DPI

---

### 2. plot_doc_length_distribution.py

Analyzes document length distributions across the corpus sources.

**Output file:** `output/doc_length_dist.png`

**What it shows:**
- Histogram: Overall document length distribution (x-axis log scale)
- Box plot: Per-source length distribution comparison
- Summary statistics: Mean, median, and count of documents

**Data source:**
- Primary: Shard files in `shards/` directory (JSONL format with 'text' field)
- Fallback: Mock data using gamma distributions with realistic parameters

**How to run:**
```bash
python plot_doc_length_distribution.py
```

**Expected output:**
- Two-panel figure with histogram and box plots
- PNG saved to output/ directory at 300 DPI

---

### 3. plot_pipeline_flow.py

Visualizes the complete data processing pipeline from raw input to model handoff.

**Output file:** `output/pipeline_flow.png`

**What it shows:**
- Pipeline stages: SSD -> Validate -> Convert Schema -> Cross Dedup -> QA Gate -> Handoff -> Model Team
- Token counts at each stage (shows 1.8% loss through processing)
- Stage descriptions and summary statistics

**Data source:**
- No external data required (uses predefined pipeline configuration)

**How to run:**
```bash
python plot_pipeline_flow.py
```

**Expected output:**
- Clean, publication-quality diagram suitable for GitHub README
- PNG saved to output/ directory at 300 DPI

---

### 4. plot_thai_char_ratio.py

Analyzes the distribution of Thai character ratios in web documents and quality filtering impact.

**Output file:** `output/thai_char_ratio.png`

**What it shows:**
- Histogram: Distribution of Thai character ratio (0.0 to 1.0)
- Quality threshold line: 0.50 (50% Thai characters) - documents below this are filtered
- Mean line: Average Thai character ratio across documents
- Statistics: Pass/fail counts for QA filter

**Data source:**
- Primary: `thai_ratios.json` (JSON array or dict with 'ratios' key)
- Fallback: Mock data (normal distribution centered at 0.72, std 0.15)

**How to run:**
```bash
python plot_thai_char_ratio.py
```

**Expected output:**
- Histogram with quality threshold visualization
- PNG saved to output/ directory at 300 DPI

---

## Output Files

All scripts save visualizations to the `output/` subdirectory:

```
graphs/
├── output/
│   ├── corpus_composition.png
│   ├── doc_length_dist.png
│   ├── pipeline_flow.png
│   └── thai_char_ratio.png
```

The output directory is created automatically if it doesn't exist.

## Data Requirements

### For production use (optional):

**manifest.json** (for plot_corpus_composition.py):
```json
{
  "sources": [
    {"name": "THAILLM", "tokens": 7000000000, "docs": 450000},
    {"name": "SEAPILE", "tokens": 5000000000, "docs": 320000},
    {"name": "The Stack V2", "tokens": 5000000000, "docs": 280000},
    {"name": "FineMath", "tokens": 3000000000, "docs": 150000}
  ]
}
```

**shards/ directory** (for plot_doc_length_distribution.py):
- JSONL files with 'text' field for each document
- Each line is a JSON object: `{"text": "...", ...}`

**thai_ratios.json** (for plot_thai_char_ratio.py):
```json
{"ratios": [0.72, 0.68, 0.75, ...]}
```
or
```json
[0.72, 0.68, 0.75, ...]
```

All scripts have built-in mock data fallbacks, so they can run immediately without data files.

## Dependencies

Required packages:
- `matplotlib` (>= 3.5.0)
- `seaborn` (>= 0.12.0)
- `numpy` (>= 1.20.0)

Install with:
```bash
pip install matplotlib seaborn numpy
```

## Design Notes

- All scripts use `matplotlib` only (no plotly, bokeh, or other libraries)
- Style: `seaborn-v0_8-whitegrid` for clean, publication-ready plots
- Resolution: 300 DPI for high-quality publication/presentation use
- Font fallback: Automatic handling for Thai text and Unicode characters
- Output format: PNG with transparency support

## Running All Scripts

To generate all visualizations:
```bash
python plot_corpus_composition.py
python plot_doc_length_distribution.py
python plot_pipeline_flow.py
python plot_thai_char_ratio.py
```

Or in one command:
```bash
for script in plot_*.py; do python "$script"; done
```

## Updating the Visualizations

To update visualizations with new data:
1. Place `manifest.json` in the graphs directory (for corpus composition)
2. Place shard files in `graphs/shards/` (for document length distribution)
3. Place `thai_ratios.json` in the graphs directory (for Thai char ratio)
4. Run the corresponding script

The scripts will automatically detect and use real data files in preference to mock data.

## Notes

- All scripts include `if __name__ == "__main__"` guards for safe imports
- No em dashes (long dashes) used in comments or docstrings per style guidelines
- Each script is self-contained and can run independently
- Mock data uses realistic statistical distributions matching expected corpus characteristics
