# STOCKSENSE — Demand Intelligence

**Predict Demand. Prevent Stock-outs. Power Better Decisions.**

A data science hackathon project by a 3-member team that forecasts short-term
product demand, flags stock-out risk, explains the drivers, and recommends
replenishment actions through a dashboard.

> **Status:** initial project foundation only. No data cleaning, models, or
> dashboard have been implemented yet. Items marked **TODO(team)** still need
> to be decided or supplied by the team.

---

## Problem Statement

Stock-outs lose sales and customer trust, while over-stocking ties up capital.
The goal is to use historical data to **predict demand for the next 7 days**,
**identify items at risk of stock-out**, and turn those predictions into
**clear, explainable replenishment decisions**.

> **TODO(team):** paste the official hackathon problem statement text and a
> description of the supplied dataset (source, files, time period) here.

## Objectives

1. Produce a cleaned, integrated master dataset with documented cleaning decisions.
2. Explore and statistically analyze demand and inventory patterns.
3. Build and compare 7-day demand forecasting models using time-aware validation.
4. Build a stock-out risk classifier and explain its predictions.
5. Categorize risk and generate replenishment recommendations.
6. Present results in an interactive Streamlit dashboard.

## Team Roles

| Role | Responsibilities | Main locations |
|------|------------------|----------------|
| **Student 1 — Data Analyst** | Data inspection, cleaning, integration, EDA, statistical analysis, cleaned master dataset | `src/data/`, `notebooks/01_*` |
| **Student 2 — ML Engineer** | Feature engineering, 7-day demand forecasting, model comparison, time-aware validation, evaluation | `src/forecasting/`, `notebooks/02_*` |
| **Student 3 — Decision Intelligence Engineer** | Stock-out classification, explainability, risk categorization, replenishment recommendations, dashboard integration | `src/classification/`, `src/explainability/`, `src/recommendations/`, `dashboard/`, `notebooks/03_*` |

> **TODO(team):** add team member names next to each role.

## Proposed Workflow

1. **Student 1** inspects raw data and agrees a **data contract** (file, columns, granularity) with the team.
2. **Students 2 and 3** build data-independent scaffolding in parallel.
3. **Student 1** delivers the cleaned master dataset to `data/processed/`.
4. **Student 2** trains forecasts; **Student 3** builds stock-out risk, explanations, and recommendations.
5. Everything is integrated through pull requests and surfaced in the dashboard.

See [docs/TEAM_WORKFLOW.md](docs/TEAM_WORKFLOW.md) for the full dependency sequence
and the list of open team decisions.

## Project Structure

```
stocksense-demand-intelligence/
├── data/
│   ├── raw/                # original hackathon data (git-ignored)
│   ├── processed/          # cleaned master dataset (git-ignored)
│   └── synthetic/          # SYNTHETIC training data (committed)
├── notebooks/
│   ├── 01_data_understanding_eda.ipynb   # Student 1
│   ├── 02_demand_forecasting.ipynb       # Student 2
│   └── 03_stockout_intelligence.ipynb    # Student 3
├── src/
│   ├── common/config.py                  # shared paths & settings
│   ├── data/prepare_data.py              # cleaning + master dataset
│   ├── data/generate_synthetic_data.py   # synthetic dataset generator
│   ├── forecasting/train_forecast.py     # 7-day demand forecasting
│   ├── classification/train_stockout.py  # stock-out risk model
│   ├── explainability/explain.py         # model explanations
│   └── recommendations/replenishment.py  # risk categories + actions
├── dashboard/              # Streamlit app (later phase)
├── models/                 # saved model files (git-ignored)
├── reports/                # figures and written findings
├── tests/                  # pytest tests
├── docs/TEAM_WORKFLOW.md
├── .github/PULL_REQUEST_TEMPLATE.md
├── requirements.txt
├── pytest.ini
├── .env.example
└── .gitignore
```

## Environment Setup

Requires **Python 3.11 or newer** (3.11 / 3.12 recommended).

```bash
# 1. Create a virtual environment (from the project root)
python -m venv .venv

# 2. Activate it
#    Windows (PowerShell):
.venv\Scripts\Activate.ps1
#    macOS / Linux:
source .venv/bin/activate

# 3. Install dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt

# 4. (Optional) create local settings
cp .env.example .env        # Windows PowerShell: Copy-Item .env.example .env

# 5. Register the kernel for Jupyter (optional)
python -m ipykernel install --user --name stocksense
```

**Data:** a **synthetic training dataset** (stores, products, external factors,
inventory, transactions) is committed in `data/synthetic/`. See
[data/synthetic/README.md](data/synthetic/README.md) for the column dictionary,
table relationships and the data-quality issues injected for cleaning practice.
Regenerate it with `python -m src.data.generate_synthetic_data`.

Any real/supplied raw files go in `data/raw/`; they are not committed to Git.
> **TODO(team):** if official hackathon data is provided, document where it is
> downloaded from and how the cleaned master dataset is shared between members.

## Running the Code

Run modules from the **project root** so `src` imports work:

```bash
python -m src.data.generate_synthetic_data   # (re)create data/synthetic/*.csv
python -m src.data.prepare_data
python -m src.forecasting.train_forecast
python -m src.classification.train_stockout
```

The generator is fully working; the other modules currently only print placeholder messages.

## Running Tests

```bash
pytest          # from the project root
pytest -v       # verbose output
```

`tests/test_smoke.py` checks that every module in `src` can be imported. Add
real unit tests next to it as features are implemented.

## Git Collaboration

`main` should always be working. Each member works on a feature branch and
merges through a pull request.

```bash
# Get the latest main
git checkout main
git pull origin main

# Create your feature branch (one per task)
git checkout -b feature/data-cleaning-eda      # Student 1
git checkout -b feature/demand-forecasting     # Student 2
git checkout -b feature/decision-dashboard     # Student 3

# Commit your work
git status
git add src/data/prepare_data.py notebooks/01_data_understanding_eda.ipynb
git commit -m "Add initial data quality checks"

# Push the branch
git push -u origin feature/data-cleaning-eda

# Open a pull request (GitHub web UI, or with the GitHub CLI):
gh pr create --base main --fill
```

Before opening a PR: pull the latest `main`, run `pytest`, and fill in the PR
template. Keep PRs small; ask a teammate to review before merging.

> **TODO(team):** create the shared GitHub repository and add all members as collaborators.

## Rules of Thumb

- Don't hard-code column names or paths — put agreed values in `src/common/config.py`.
- Don't commit data, `.env`, or model files.
- Report only real results; label assumptions clearly.
