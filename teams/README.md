# teams/ - Per-Team Workspace

Each subfolder belongs to one Data sub-team. Workers commit their notebooks and fill in the report as they go.

| Folder | Team | Primary task |
|--------|------|-------------|
| [01_data_retrieval/](01_data_retrieval/) | Data Retrieval | Verify SSD access, count shards, confirm schema fields |
| [02_data_preprocessing/](02_data_preprocessing/) | Data Preprocessing | Convert to unified schema, spam filter, dedup, validate |
| [03_data_understanding/](03_data_understanding/) | Data Understanding / Model Liaison | Corpus stats, confirm mix ratios with Model team, produce handoff data card |

## How to use

1. Open `notebook_template.ipynb` in your team folder and run the cells for your assigned shard/dataset.
2. Fill in `report.md` with results as you go.
3. `git add`, `git commit`, `git push` after each shard is done.

## Branch naming

Follow [CONTRIBUTING.md](../CONTRIBUTING.md):

```
data/<your-name>/<task>
# examples:
data/mingkwan/retrieval-thaillm
data/ploy/preprocess-seapile-shard000
data/tae/understanding-mix-ratio
```

## Commit prefix

| Prefix | When to use |
|--------|-------------|
| `feat:` | new notebook cell or script |
| `fix:` | bug fix in processing |
| `docs:` | update report.md |
| `analysis:` | new stats / graphs |
