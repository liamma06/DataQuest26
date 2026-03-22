import React from "react";

export default function ResultCard({ result }) {
  if (!result) return null;

  const riskClass = `risk-${result.risk_category}`;

  return (
    <div className="card result-card">
      <h2>Prediction Result</h2>

      <div className="result-header">
        <div className="risk-score">{result.risk_score}%</div>
        <span className={`risk-badge ${riskClass}`}>
          {result.risk_category} risk
        </span>
      </div>

      <div className="result-section">
        <h3>Key Risk Factors</h3>
        <ul className="factors-list">
          {result.top_factors.map((factor) => (
            <li key={factor}>{factor.replace(/_/g, " ")}</li>
          ))}
        </ul>
      </div>

      <div className="result-section">
        <h3>Recommendations</h3>
        <ul className="recommendations-list">
          {result.recommendations.map((tip) => (
            <li key={tip}>{tip}</li>
          ))}
        </ul>
      </div>
    </div>
  );
}
