# Thai Foundation LLM - Data Team Repository

![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue)
![License MIT](https://img.shields.io/badge/License-MIT-green)
![Status Active](https://img.shields.io/badge/Status-Active-brightgreen)
![Camp Super AI SS6](https://img.shields.io/badge/Camp-Super%20AI%20SS6-purple)

---

## About This Project

This repository is the data engineering hub for the **Thai Foundation LLM Initiative**, part of the Super AI SS6 competitive bootcamp in Thailand. A 156-person camp across 7 teams is building a >1 billion parameter foundational language model for the Thai language. The Data Team (30-40 workers) is responsible for validating, preprocessing, and delivering a high-quality corpus of approximately 20 billion tokens to the Model Team. Our work ensures the training data meets quality standards, is properly formatted, and is optimized for effective pretraining.

---

## Team

| Name | Role |
|------|------|
| Poom | Data Team Lead |
| Pete | Data Team Lead |
| Calvin | Teaching Assistant & Data Lead |
| Arthur | Data Team Contributor |

---

## Dataset Overview

| Source | Domain | Language | Est. Size | License |
|--------|--------|----------|-----------|---------|
| THAILLM | General Thai Text | Thai | ~5B tokens | MIT |
| SEAPILE | Web Data (Southeast Asia) | Thai | ~8B tokens | CC-BY-4.0 |
| The Stack V2 | Source Code | Multi-language | ~4B tokens | Open |
| FineMath | Mathematical Content | Multi-language | ~3B tokens | MIT |

All datasets are pre-provisioned on a dedicated 600 GB SSD for efficient processing.

---

## Repository Structure

```
thai-llm-data-team/
├── README.md
│
├── docs/
│   ├── 01_data_retrieval_guidelines.md       # How to access and download data
│   ├── 02_data_preprocessing_guidelines.md   # Data cleaning and standardization
│   ├── 03_data_understanding_for_model_team.md # Dataset insights and statistics
│   ├── 04_worker_workflow_and_qa.md          # Task assignment, QA, validation
│   └── 05_master_10h_sprint_plan.md          # Camp schedule and sprint objectives
│
├── code/
│   ├── validate/                             # Data validation scripts
│   │   └── schema_validator.py
│   │
│   ├── preprocess/                           # Data preprocessing pipelines
│   │   └── tokenizer.py
│   │
│   └── analysis/                             # Data analysis and statistics
│       └── corpus_analyzer.py
│
├── graphs/
│   └── (data visualizations, distribution charts, quality metrics)
│
└── logs/
    └── (experiment results, processing outcomes, research findings)
```

---

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/your-org/thai-llm-data-team.git
cd thai-llm-data-team
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

Required packages include tokenizers, datasets, and data validation libraries.

### 3. Run Validator on a Sample Shard

```bash
python code/validate/schema_validator.py --input-path /path/to/sample/shard
```

This validates data format, encoding, and quality metrics on a test dataset.

---

## Documentation

Start with these guides in the recommended order:

1. **[Data Retrieval Guidelines](docs/01_data_retrieval_guidelines.md)** - Access and download instructions for all 4 data sources
2. **[Data Preprocessing Guidelines](docs/02_data_preprocessing_guidelines.md)** - Cleaning, normalization, and tokenization procedures
3. **[Data Understanding for Model Team](docs/03_data_understanding_for_model_team.md)** - Dataset statistics, language distributions, quality metrics
4. **[Worker Workflow and QA](docs/04_worker_workflow_and_qa.md)** - Task assignment, validation checklist, quality assurance process
5. **[Master 10-Hour Sprint Plan](docs/05_master_10h_sprint_plan.md)** - Camp schedule, sprint goals, and milestones

---

## Outcomes & Research Log

The `logs/` directory contains:

- **Experiment Results** - Outputs from data preprocessing runs, including token counts and quality scores
- **Processing Metrics** - Validation statistics, encoding errors, and recovery procedures
- **Research Findings** - Insights into data characteristics, language patterns, and corpus composition
- **Camp Progress** - Sprint completion reports and blockers encountered

All team members should document their experiments and findings in dated log files to maintain a continuous research record.

---

## Contributing

### Branch Naming Convention

- Feature branches: `feature/description`
- Bug fixes: `fix/description`
- Data processing: `data/description`
- Documentation: `docs/description`

### Pull Request Process

1. Create a feature branch from `main`
2. Make your changes with clear commit messages
3. Push to your branch and open a pull request
4. Ensure validation scripts pass
5. Request review from a Data Team Lead (Poom, Pete, or Calvin)
6. Merge after approval

---

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**Camp:** Super AI SS6 | **Duration:** Bootcamp Session | **Target:** >1B Parameter Thai LLM
