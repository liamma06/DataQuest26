from __future__ import annotations

from .schemas import PredictionInput


def risk_category_from_probability(probability: float) -> str:
    if probability < 0.30:
        return "low"
    if probability <= 0.70:
        return "medium"
    return "high"


def top_factors(payload: PredictionInput, probability: float) -> list[str]:
    factors: list[str] = []
    if payload.ap_hi >= 140 or payload.ap_lo >= 90:
        factors.append("elevated_blood_pressure")
    if payload.cholesterol >= 2:
        factors.append("cholesterol_level")
    if payload.gluc >= 2:
        factors.append("glucose_level")
    if payload.age_years >= 55:
        factors.append("age")
    bmi = payload.weight / ((payload.height / 100.0) ** 2)
    if bmi >= 30:
        factors.append("bmi")
    if payload.smoke == 1:
        factors.append("smoking")
    if payload.active == 0:
        factors.append("low_activity")
    if not factors:
        factors.append("overall_profile")
    return factors[:3] if probability < 0.7 else factors[:5]


def recommendations(payload: PredictionInput, probability: float) -> list[str]:
    tips: list[str] = []
    if payload.ap_hi >= 140 or payload.ap_lo >= 90:
        tips.append("Monitor blood pressure regularly and reduce sodium intake.")
    if payload.cholesterol >= 2:
        tips.append("Adopt a heart-healthy diet and schedule lipid follow-up checks.")
    if payload.gluc >= 2:
        tips.append("Track glucose and discuss metabolic screening with a clinician.")
    if payload.active == 0:
        tips.append("Increase weekly physical activity with a realistic routine.")
    if payload.smoke == 1:
        tips.append("Start a smoking cessation plan to reduce cardiovascular risk.")
    if probability > 0.70:
        tips.append("Consider prompt clinical follow-up for personalized assessment.")
    if not tips:
        tips.append("Maintain current healthy habits and periodic preventive checkups.")
    return tips[:4]
