from __future__ import annotations

from pydantic import BaseModel, Field, model_validator


class PredictionInput(BaseModel):
    age_years: float = Field(..., ge=18, le=120)
    gender: int = Field(..., ge=1, le=2)
    height: float = Field(..., ge=120, le=220)
    weight: float = Field(..., ge=30, le=250)
    ap_hi: float = Field(..., ge=80, le=250)
    ap_lo: float = Field(..., ge=40, le=160)
    cholesterol: int = Field(..., ge=1, le=3)
    gluc: int = Field(..., ge=1, le=3)
    smoke: int = Field(..., ge=0, le=1)
    alco: int = Field(..., ge=0, le=1)
    active: int = Field(..., ge=0, le=1)

    @model_validator(mode="after")
    def validate_bp_order(self) -> "PredictionInput":
        if self.ap_hi <= self.ap_lo:
            raise ValueError("ap_hi must be greater than ap_lo")
        return self


class PredictionOutput(BaseModel):
    prediction: int
    risk_score: float
    risk_category: str
    top_factors: list[str]
    recommendations: list[str]


class HistoryItem(BaseModel):
    id: int
    created_at: str
    risk_score: float
    risk_category: str
    prediction: int


class HistorySummary(BaseModel):
    total_predictions: int
    avg_risk_score: float
    low_count: int
    medium_count: int
    high_count: int


class HistoryResponse(BaseModel):
    summary: HistorySummary
    records: list[HistoryItem]
