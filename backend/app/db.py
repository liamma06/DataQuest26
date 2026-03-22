from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from .schemas import HistoryItem, HistoryResponse, HistorySummary, PredictionInput, PredictionOutput


class PredictionStore:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS predictions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at TEXT NOT NULL DEFAULT (datetime('now')),
                    inputs_json TEXT NOT NULL,
                    prediction INTEGER NOT NULL,
                    risk_score REAL NOT NULL,
                    risk_category TEXT NOT NULL,
                    top_factors_json TEXT NOT NULL,
                    recommendations_json TEXT NOT NULL
                );
                """
            )
            conn.commit()

    def insert_prediction(self, payload: PredictionInput, result: PredictionOutput) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO predictions (
                    inputs_json, prediction, risk_score, risk_category,
                    top_factors_json, recommendations_json
                ) VALUES (?, ?, ?, ?, ?, ?);
                """,
                (
                    json.dumps(payload.model_dump(), separators=(",", ":")),
                    result.prediction,
                    result.risk_score,
                    result.risk_category,
                    json.dumps(result.top_factors, separators=(",", ":")),
                    json.dumps(result.recommendations, separators=(",", ":")),
                ),
            )
            conn.commit()

    def fetch_history(self, limit: int = 50) -> HistoryResponse:
        with self._connect() as conn:
            records_rows = conn.execute(
                """
                SELECT id, created_at, risk_score, risk_category, prediction
                FROM predictions
                ORDER BY id DESC
                LIMIT ?;
                """,
                (limit,),
            ).fetchall()
            summary_row = conn.execute(
                """
                SELECT
                    COUNT(*) AS total_predictions,
                    COALESCE(AVG(risk_score), 0.0) AS avg_risk_score,
                    SUM(CASE WHEN risk_category = 'low' THEN 1 ELSE 0 END) AS low_count,
                    SUM(CASE WHEN risk_category = 'medium' THEN 1 ELSE 0 END) AS medium_count,
                    SUM(CASE WHEN risk_category = 'high' THEN 1 ELSE 0 END) AS high_count
                FROM predictions;
                """
            ).fetchone()

        records = [
            HistoryItem(
                id=int(r["id"]),
                created_at=str(r["created_at"]),
                risk_score=float(r["risk_score"]),
                risk_category=str(r["risk_category"]),
                prediction=int(r["prediction"]),
            )
            for r in records_rows
        ]

        summary = HistorySummary(
            total_predictions=int(summary_row["total_predictions"]),
            avg_risk_score=float(summary_row["avg_risk_score"]),
            low_count=int(summary_row["low_count"] or 0),
            medium_count=int(summary_row["medium_count"] or 0),
            high_count=int(summary_row["high_count"] or 0),
        )
        return HistoryResponse(summary=summary, records=records)
