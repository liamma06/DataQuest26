# Copilot Instructions for DataQuest26

## Build, test, and lint commands

This repository is currently script-and-data driven (no project-level `Makefile`, `pytest`, or linter config committed yet).

Use the virtual environment in repo root:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install pandas numpy scikit-learn matplotlib seaborn joblib
```

Current runnable commands from committed files/docs:

- Clean raw dataset:
  ```bash
  source .venv/bin/activate
  python data/clean_data.py
  ```
- Run the training flow (once `train.py` exists, per `TRAINING.md`):
  ```bash
  source .venv/bin/activate
  python train.py
  ```
- Quick metrics readout (single check):
  ```bash
  source .venv/bin/activate
  python - << 'PY'
  import json
  with open("metrics.json") as f:
      m = json.load(f)
  for k in ["baseline", "primary"]:
      print(k, "accuracy=", round(m[k]["accuracy"], 4), "f1=", round(m[k]["f1"], 4), "roc_auc=", round(m[k]["roc_auc"], 4))
  PY
  ```

There is no formal single-test runner configured. For targeted validation, run focused one-off checks with `python - << 'PY' ... PY` against the specific function/output you changed.

## High-level architecture

The repository is organized around a hackathon ML pipeline for cardiovascular risk prediction:

1. **Data layer** (`data/`)
   - `cardio_train.csv` is the raw Kaggle export using semicolon delimiters.
   - `clean_data.py` applies a minimal cleaning pass (`ap_hi > 0`, `ap_lo > 0`, `ap_hi > ap_lo`) and writes `cardio_clean.csv` (comma-delimited).

2. **Model training flow** (documented in `TRAINING.md`)
   - Train from scratch using scikit-learn pipelines.
   - Expected sequence: load -> clean -> feature engineering (BMI, pulse pressure, lifestyle score, optional interaction) -> split -> baseline + primary model training -> evaluation -> save artifacts.
   - Canonical output artifacts are `model.pkl` and `metrics.json`.

3. **Product architecture** (from `README.md`)
   - User Input -> Backend API -> ML Model -> Predictions -> Dashboard UI.
   - Prediction contract includes class label, risk score, risk category, top factors, and recommendations.

## Key conventions in this codebase

- **Hackathon constraints are hard requirements** (from `README.md`): no pretrained models, no pretrained weights/embeddings, no external APIs.
- **Dataset delimiter convention matters**:
  - Raw `data/cardio_train.csv` is semicolon-separated (`sep=";"`).
  - Cleaned `data/cardio_clean.csv` is comma-separated.
- **Domain validity rule already encoded in scripts**: blood pressure must satisfy `ap_hi > ap_lo`; preserve this when extending cleaning/training.
- **Label and risk semantics are fixed by docs**:
  - target column is `cardio` (`0` no disease, `1` disease)
  - risk categories use `<30%`, `30–70%`, `>70%` thresholds.
- **Artifact convention**: trained model should be saved as `.pkl` and consumed by backend/UI flow.

