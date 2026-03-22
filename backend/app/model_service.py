from __future__ import annotations

from pathlib import Path

import joblib
import pandas as pd

from .schemas import PredictionInput


FEATURE_ORDER = [
    "gender",
    "height",
    "weight",
    "ap_hi",
    "ap_lo",
    "cholesterol",
    "gluc",
    "smoke",
    "alco",
    "active",
    "age_years",
    "bmi",
    "pulse_pressure",
    "lifestyle_score",
    "chol_gluc_interaction",
]


class ModelService:
    def __init__(self, model_path: Path) -> None:
        self._model = joblib.load(model_path)

    def _to_dataframe(self, payload: PredictionInput) -> pd.DataFrame:
        bmi = payload.weight / ((payload.height / 100.0) ** 2)
        pulse_pressure = payload.ap_hi - payload.ap_lo
        lifestyle_score = payload.active - payload.smoke - payload.alco
        chol_gluc_interaction = payload.cholesterol * payload.gluc

        row = {
            "gender": payload.gender,
            "height": payload.height,
            "weight": payload.weight,
            "ap_hi": payload.ap_hi,
            "ap_lo": payload.ap_lo,
            "cholesterol": payload.cholesterol,
            "gluc": payload.gluc,
            "smoke": payload.smoke,
            "alco": payload.alco,
            "active": payload.active,
            "age_years": payload.age_years,
            "bmi": bmi,
            "pulse_pressure": pulse_pressure,
            "lifestyle_score": lifestyle_score,
            "chol_gluc_interaction": chol_gluc_interaction,
        }
        return pd.DataFrame([[row[k] for k in FEATURE_ORDER]], columns=FEATURE_ORDER)

    def predict_probability(self, payload: PredictionInput) -> float:
        df = self._to_dataframe(payload)
        probability = float(self._model.predict_proba(df)[:, 1][0])
        return probability
