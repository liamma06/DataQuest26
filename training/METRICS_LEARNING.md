# Metrics Learning Guide (Beginner-Friendly)

This guide explains what each metric means in our cardiovascular risk project and how to interpret it.

## Why accuracy is not enough

In health-risk screening, missing a true-risk patient is often worse than flagging an extra low-risk patient.

That means we should track **recall** and **false negative rate (FNR)** very closely, not just accuracy.

## Core classification metrics

### Accuracy
- **What it is:** Percent of all predictions that are correct.
- **Formula:** `(TP + TN) / (TP + TN + FP + FN)`
- **Use:** Quick overall snapshot.
- **Limit:** Can look good while still missing too many true-risk patients.

### Precision
- **What it is:** Of patients predicted as high risk, how many are truly high risk.
- **Formula:** `TP / (TP + FP)`
- **Use:** Helps control false alarms.
- **Tradeoff:** Higher precision often lowers recall.

### Recall (Sensitivity)
- **What it is:** Of truly high-risk patients, how many we correctly detect.
- **Formula:** `TP / (TP + FN)`
- **Use:** Critical for screening because it measures missed-risk control.
- **Project priority:** We optimize this more heavily.

### F1 Score
- **What it is:** Balance between precision and recall.
- **Formula:** `2 * (Precision * Recall) / (Precision + Recall)`
- **Use:** Good single score when you want balance.

### ROC-AUC
- **What it is:** Ranking quality across all thresholds.
- **Range:** `0.5` (random) to `1.0` (perfect).
- **Use:** Measures how well the model separates risk vs non-risk overall.

## Confusion-matrix-derived metrics

### Specificity (True Negative Rate)
- **What it is:** Of truly low-risk patients, how many we correctly mark as low risk.
- **Formula:** `TN / (TN + FP)`
- **Use:** Helps understand false positives.

### FNR (False Negative Rate)
- **What it is:** Of truly high-risk patients, how many we miss.
- **Formula:** `FN / (FN + TP)`
- **Use:** Very important in this project. Lower is better.

### NPV (Negative Predictive Value)
- **What it is:** Of patients predicted low risk, how many are truly low risk.
- **Formula:** `TN / (TN + FN)`
- **Use:** Confidence in “you are low risk” outputs.

## Probability-quality metrics

### Brier Score
- **What it is:** Mean squared error of predicted probabilities.
- **Range:** Lower is better (0 is perfect).
- **Use:** Evaluates whether predicted risk percentages are numerically reliable.

### Calibration (ECE)
- **What it is:** How close predicted probabilities are to observed outcomes.
- **Interpretation:** Lower ECE means better-calibrated probabilities.
- **Example:** If model says 70% risk, roughly 70% should truly be positive.

## Thresholds and tradeoffs

Our model outputs a probability (0 to 1). We pick a threshold to convert probability into class 0/1.

- Lower threshold -> higher recall, lower precision
- Higher threshold -> higher precision, lower recall

For our current recall-priority setup, a threshold around `0.37` gave better missed-risk control than `0.50`.

## Risk categories in this project

We map probabilities to categories for product output:
- Low: `< 0.313`
- Medium: `0.313 - 0.625`
- High: `> 0.625`

These were chosen from calibrated model behavior, not arbitrary defaults.

## Practical recommendation for presentations

When showing results, always present at least:
- Recall
- FNR
- F1
- ROC-AUC
- Confusion matrix

And explain the threshold used, since metrics change with threshold.
