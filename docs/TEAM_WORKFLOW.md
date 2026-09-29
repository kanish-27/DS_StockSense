# Team Workflow

## Dependency sequence

```
 Student 1 (Data)            Student 2 (Forecasting)        Student 3 (Decision Intelligence)
 ────────────────            ───────────────────────        ─────────────────────────────────
 Inspect raw data            Scaffold features /            Scaffold classifier, risk
 Clean + integrate           validation code (no data)      categories, dashboard layout
 EDA + stats                          │                              │
 ▼                                    │                              │
 Cleaned master dataset ──────────────┴──────────────►               │
 + data contract                      ▼                              │
                             Train + evaluate 7-day                  │
                             forecasts ─────────────────────────────►▼
                                                            Stock-out model, explainability,
                                                            recommendations, dashboard
                                        │
                                        ▼
                     Integration via pull requests + tests on `main`
```

### Phase 1 — Parallel setup (no shared data needed)
- **Student 1** inspects the raw data and drafts the **data contract**: file name,
  columns, types, granularity, date range, and known data-quality issues.
- **Student 2** prepares independent scaffolding: feature-engineering functions,
  time-aware validation helpers, metric functions, and a baseline structure.
- **Student 3** prepares independent scaffolding: classifier/evaluation structure,
  explainability helpers, and a dashboard layout skeleton.
- Nobody hard-codes column names until the data contract is agreed.

### Phase 2 — Master dataset handoff
- Student 1 delivers the **agreed cleaned master dataset** to `data/processed/`
  and records its path and key columns in `src/common/config.py` via a PR.
- Because data files are git-ignored, share the file itself through the team's
  agreed channel. **TODO(team): decide the sharing method (e.g. shared drive).**

### Phase 3 — Data-dependent work
- Student 2 trains and evaluates the 7-day forecasting models and shares the
  forecast output format.
- Student 3 builds stock-out classification (optionally using forecasts),
  explainability, risk categorization, and replenishment recommendations.

### Phase 4 — Integration
- All modules merge into `main` through pull requests using the PR template.
- Every PR must keep `pytest` passing.
- Student 3 wires final outputs into the Streamlit dashboard.

## Decisions the team still needs to make
- [ ] Master dataset file name, format, and key columns
- [ ] Definition of a "stock-out" for this dataset
- [ ] Forecast evaluation metrics and validation window
- [ ] Classification metrics and risk-category thresholds
- [ ] Replenishment rules and any business constraints
- [ ] How data files are shared (they are not committed to Git)

## Ground rules
- Shared settings live in `src/common/config.py` — change them through a PR.
- One feature branch per task; small, focused PRs.
- Do not commit raw data, `.env`, or large model files.
- Report only real results; never fabricate metrics.
