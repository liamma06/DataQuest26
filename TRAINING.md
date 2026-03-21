# TRAINING.md

Beginner-friendly guide to train the **Cardiovascular Risk Prediction** model from scratch for your hackathon.

This guide is based on `README.md` and follows your constraints:
- no pretrained models
- no external APIs
- must train from scratch
- must report evaluation metrics

---

## 1) What your team is building

You will train a model that predicts:
- `cardio = 0` (no disease) or `1` (disease)
- risk score (probability from 0.0 to 1.0, displayed as 0–100%)
- risk category:
  - Low: `< 0.30`
  - Medium: `0.30–0.70`
  - High: `> 0.70`

You should start with a simple baseline (Logistic Regression), then train a stronger primary model (Random Forest).

---

## 2) Team workflow (recommended)

- **ML person (or pair):** data cleaning, feature engineering, training, evaluation
- **Backend person:** load saved model and expose prediction endpoint
- **Frontend person:** risk score + category + top factors + recommendations
- **Presenter:** demo narrative and slide story

Keep one shared Google Doc/Notion page with:
- latest model metrics
- chosen model version
- known limitations

---

## 3) Project setup (copy/paste)

From repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install pandas numpy scikit-learn matplotlib seaborn joblib
```

Expected data file (already downloaded earlier):

- `cardio_train.csv`

Quick sanity check:

```bash
python - << 'PY'
import pandas as pd
df = pd.read_csv("cardio_train.csv", sep=";")
print(df.shape)
print(df.head(2))
PY
```

You should see roughly `(70000, 13)`.

---

## 4) Training script (create `train.py`)

Create a file named `train.py` in repo root and paste this:

```python
import json
import joblib
import numpy as np
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


RANDOM_STATE = 42


def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, sep=";")
    return df


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    # Convert age days -> years for interpretability
    df = df.copy()
    df["age_years"] = df["age"] / 365.25

    # Remove clearly invalid physiological values (common in this dataset)
    df = df[(df["height"] >= 120) & (df["height"] <= 220)]
    df = df[(df["weight"] >= 30) & (df["weight"] <= 250)]
    df = df[(df["ap_hi"] >= 80) & (df["ap_hi"] <= 250)]
    df = df[(df["ap_lo"] >= 40) & (df["ap_lo"] <= 160)]

    # Ensure systolic >= diastolic
    df = df[df["ap_hi"] >= df["ap_lo"]]
    return df


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # BMI
    height_m = df["height"] / 100.0
    df["bmi"] = df["weight"] / (height_m ** 2)

    # Pulse pressure
    df["pulse_pressure"] = df["ap_hi"] - df["ap_lo"]

    # Lifestyle score (higher can indicate healthier behavior)
    df["lifestyle_score"] = df["active"] - df["smoke"] - df["alco"]

    # Optional interaction
    df["chol_gluc_interaction"] = df["cholesterol"] * df["gluc"]

    return df


def build_preprocessor(numeric_features, categorical_features):
    numeric_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )

    categorical_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore")),
        ]
    )

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_transformer, numeric_features),
            ("cat", categorical_transformer, categorical_features),
        ]
    )
    return preprocessor


def evaluate(name, model, X_test, y_test):
    preds = model.predict(X_test)
    probs = model.predict_proba(X_test)[:, 1]

    metrics = {
        "model": name,
        "accuracy": accuracy_score(y_test, preds),
        "f1": f1_score(y_test, preds),
        "roc_auc": roc_auc_score(y_test, probs),
        "confusion_matrix": confusion_matrix(y_test, preds).tolist(),
        "classification_report": classification_report(y_test, preds, output_dict=True),
    }
    return metrics


def main():
    df = load_data("cardio_train.csv")
    df = clean_data(df)
    df = engineer_features(df)

    # Target
    y = df["cardio"]

    # Feature set (drop id + original target + age in days to avoid duplication with age_years)
    X = df.drop(columns=["id", "cardio", "age"])

    # Treat encoded medical/lifestyle integers as categorical where appropriate
    categorical_features = ["gender", "cholesterol", "gluc", "smoke", "alco", "active"]
    numeric_features = [c for c in X.columns if c not in categorical_features]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=RANDOM_STATE, stratify=y
    )

    preprocessor = build_preprocessor(numeric_features, categorical_features)

    # Baseline
    lr_pipeline = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("model", LogisticRegression(max_iter=1000, random_state=RANDOM_STATE)),
        ]
    )

    # Primary model
    rf_pipeline = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("model", RandomForestClassifier(
                n_estimators=300,
                max_depth=None,
                min_samples_split=4,
                min_samples_leaf=2,
                random_state=RANDOM_STATE,
                n_jobs=-1,
            )),
        ]
    )

    lr_pipeline.fit(X_train, y_train)
    rf_pipeline.fit(X_train, y_train)

    lr_metrics = evaluate("logistic_regression", lr_pipeline, X_test, y_test)
    rf_metrics = evaluate("random_forest", rf_pipeline, X_test, y_test)

    all_metrics = {"baseline": lr_metrics, "primary": rf_metrics}
    print(json.dumps(all_metrics, indent=2))

    # Save the better model by F1
    best_model = rf_pipeline if rf_metrics["f1"] >= lr_metrics["f1"] else lr_pipeline
    best_name = "random_forest" if best_model is rf_pipeline else "logistic_regression"

    joblib.dump(best_model, "model.pkl")
    with open("metrics.json", "w", encoding="utf-8") as f:
        json.dump(all_metrics, f, indent=2)

    print(f"\nSaved best model: {best_name} -> model.pkl")
    print("Saved metrics -> metrics.json")


if __name__ == "__main__":
    main()
```

---

## 5) Run training

```bash
source .venv/bin/activate
python train.py
```

This generates:
- `model.pkl` (trained model)
- `metrics.json` (evaluation summary)

---

## 6) Read results (what to care about)

Open metrics:

```bash
python - << 'PY'
import json
with open("metrics.json") as f:
    m = json.load(f)
for k in ["baseline", "primary"]:
    print(k, "accuracy=", round(m[k]["accuracy"], 4), "f1=", round(m[k]["f1"], 4), "roc_auc=", round(m[k]["roc_auc"], 4))
PY
```

For hackathon judging, report:
- Accuracy
- F1 score (important if class balance changes after cleaning)
- Confusion matrix
- ROC-AUC (optional but strong)

Pick the model with better **F1** unless judges specifically prioritize another metric.

---

## 7) Inference demo snippet (for backend integration)

Use this in API/backend code:

```python
import joblib
import pandas as pd

model = joblib.load("model.pkl")

sample = pd.DataFrame([{
    "gender": 1,
    "height": 165,
    "weight": 72.0,
    "ap_hi": 135,
    "ap_lo": 85,
    "cholesterol": 2,
    "gluc": 1,
    "smoke": 0,
    "alco": 0,
    "active": 1,
    "age_years": 54.0,
    "bmi": 72.0 / (1.65 ** 2),
    "pulse_pressure": 135 - 85,
    "lifestyle_score": 1 - 0 - 0,
    "chol_gluc_interaction": 2 * 1,
}])

prob = float(model.predict_proba(sample)[:, 1][0])
pred = int(prob >= 0.5)

if prob < 0.30:
    risk_category = "low"
elif prob <= 0.70:
    risk_category = "medium"
else:
    risk_category = "high"

print({"prediction": pred, "risk_score": round(prob * 100, 2), "risk_category": risk_category})
```

Important: backend input preprocessing must match training preprocessing exactly.

---

## 8) Explainability (simple and hackathon-friendly)

For Random Forest, use feature importance:

```python
import joblib
import numpy as np

pipe = joblib.load("model.pkl")
rf = pipe.named_steps["model"]
pre = pipe.named_steps["preprocessor"]

feature_names = pre.get_feature_names_out()
importances = rf.feature_importances_
idx = np.argsort(importances)[::-1][:10]

for i in idx:
    print(feature_names[i], round(float(importances[i]), 4))
```

Use top factors to generate recommendations:
- high BP -> monitor blood pressure, reduce salt, medical follow-up
- high cholesterol/glucose -> diet changes, checkups
- low activity -> exercise plan

---

## 9) Quality gates before submission

You are ready only if all are true:
- Training runs end-to-end with one command.
- `model.pkl` and `metrics.json` are generated.
- Metrics are documented in your slides.
- Risk score + category are visible in your UI/API response.
- You can explain at least 3 top risk factors.
- No pretrained models or external APIs used.

---

## 10) Troubleshooting

- **Very low performance:** check cleaning rules are not too aggressive; inspect class balance after cleaning.
- **Feature mismatch error in backend:** ensure exact same engineered columns and names.
- **`predict_proba` missing:** use classifiers that support it (Logistic Regression, Random Forest do).
- **Overfitting suspicion:** compare train vs test metrics; reduce RF complexity if needed.

---

## 11) Suggested next iteration (if time permits)

- Add cross-validation (`cross_val_score`) for more robust metrics.
- Tune RF with `GridSearchCV` on a small parameter grid.
- Add calibration (`CalibratedClassifierCV`) if probability quality matters.
- Add simple input validation in backend (range checks for BP, height, weight).

---

## 12) Final hackathon checklist

- [ ] `train.py` committed
- [ ] `model.pkl` produced locally (do not commit large binaries unless required)
- [ ] `metrics.json` numbers copied to slides
- [ ] API returns prediction + risk score + risk category + recommendations
- [ ] Demo scenario prepared (1 low-risk, 1 high-risk patient)

If your team follows this document step-by-step, you will have a complete train-from-scratch pipeline aligned with the README goals.
