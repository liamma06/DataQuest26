from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .db import PredictionStore
from .model_service import ModelService
from .recommendations import recommendations, risk_category_from_probability, top_factors
from .schemas import HistoryResponse, PredictionInput, PredictionOutput


PROJECT_ROOT = Path(__file__).resolve().parents[2]
MODEL_PATH = PROJECT_ROOT / "model.pkl"
DB_PATH = PROJECT_ROOT / "backend" / "predictions.db"

app = FastAPI(title="DataQuest26 API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

model_service = ModelService(model_path=MODEL_PATH)
prediction_store = PredictionStore(db_path=DB_PATH)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/predict", response_model=PredictionOutput)
def predict(payload: PredictionInput) -> PredictionOutput:
    probability = model_service.predict_probability(payload)
    category = risk_category_from_probability(probability)
    prediction = 1 if probability >= 0.5 else 0
    result = PredictionOutput(
        prediction=prediction,
        risk_score=round(probability * 100.0, 2),
        risk_category=category,
        top_factors=top_factors(payload, probability),
        recommendations=recommendations(payload, probability),
    )
    prediction_store.insert_prediction(payload, result)
    return result


@app.get("/history", response_model=HistoryResponse)
def history(limit: int = 50) -> HistoryResponse:
    safe_limit = max(1, min(limit, 200))
    return prediction_store.fetch_history(limit=safe_limit)
