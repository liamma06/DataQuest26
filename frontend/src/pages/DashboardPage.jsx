import React, { useEffect, useMemo, useState } from "react";
import {
  CartesianGrid,
  Cell,
  Legend,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { fetchHistory, predict } from "../api";
import ResultCard from "../components/ResultCard";

const initialForm = {
  age_years: 54,
  gender: 1,
  height: 165,
  weight: 72,
  ap_hi: 135,
  ap_lo: 85,
  cholesterol: 2,
  gluc: 1,
  smoke: 0,
  alco: 0,
  active: 1,
};

const fieldLabels = {
  age_years: "Age (years)",
  gender: "Gender",
  height: "Height (cm)",
  weight: "Weight (kg)",
  ap_hi: "Systolic BP",
  ap_lo: "Diastolic BP",
  cholesterol: "Cholesterol",
  gluc: "Glucose",
  smoke: "Smoking",
  alco: "Alcohol",
  active: "Active",
};

const COLORS = {
  low: "#38d39f",
  medium: "#8bcf7a",
  high: "#f2c94c",
};

export default function DashboardPage() {
  const [form, setForm] = useState(initialForm);
  const [result, setResult] = useState(null);
  const [predictError, setPredictError] = useState("");
  const [historyError, setHistoryError] = useState("");
  const [loadingPredict, setLoadingPredict] = useState(false);
  const [loadingHistory, setLoadingHistory] = useState(true);
  const [history, setHistory] = useState(null);

  const loadHistory = async () => {
    setLoadingHistory(true);
    setHistoryError("");
    try {
      const data = await fetchHistory(50);
      setHistory(data);
    } catch (err) {
      setHistoryError(err.message);
    } finally {
      setLoadingHistory(false);
    }
  };

  useEffect(() => {
    loadHistory();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const update = (key, value) => {
    setForm((prev) => ({ ...prev, [key]: Number(value) }));
  };

  const onSubmit = async (e) => {
    e.preventDefault();
    setPredictError("");
    setLoadingPredict(true);
    try {
      const data = await predict(form);
      setResult(data);
      await loadHistory();
    } catch (err) {
      setPredictError(err.message);
    } finally {
      setLoadingPredict(false);
    }
  };

  const pieData = useMemo(() => {
    if (!history) return [];
    return [
      { name: "Low Risk", value: history.summary.low_count, color: COLORS.low },
      { name: "Medium Risk", value: history.summary.medium_count, color: COLORS.medium },
      { name: "High Risk", value: history.summary.high_count, color: COLORS.high },
    ].filter((d) => d.value > 0);
  }, [history]);

  const lineData = useMemo(() => {
    if (!history) return [];
    return history.records
      .slice()
      .reverse()
      .map((r, idx) => ({
        index: idx + 1,
        score: Number(r.risk_score),
      }));
  }, [history]);

  return (
    <div className="dashboard-grid">
      <section className="card animate-in form-panel">
        <h2>Patient Input</h2>
        <form onSubmit={onSubmit}>
          <div className="form-list">
            {Object.entries(form).map(([key, value]) => (
              <label key={key}>
                <span>{fieldLabels[key] || key}</span>
                {["gender", "cholesterol", "gluc", "smoke", "alco", "active"].includes(key) ? (
                  <select value={value} onChange={(e) => update(key, e.target.value)} required>
                    {key === "gender" ? (
                      <>
                        <option value="1">Male</option>
                        <option value="2">Female</option>
                      </>
                    ) : key === "cholesterol" || key === "gluc" ? (
                      <>
                        <option value="1">Normal</option>
                        <option value="2">Above Normal</option>
                        <option value="3">Well Above Normal</option>
                      </>
                    ) : (
                      <>
                        <option value="0">No</option>
                        <option value="1">Yes</option>
                      </>
                    )}
                  </select>
                ) : (
                  <input
                    type="number"
                    step={key === "age_years" || key === "weight" ? "0.1" : "1"}
                    value={value}
                    onChange={(e) => update(key, e.target.value)}
                    required
                  />
                )}
              </label>
            ))}
          </div>
          <button type="submit" disabled={loadingPredict}>
            {loadingPredict ? "Running prediction..." : "Run prediction"}
          </button>
        </form>
        {predictError && <p className="error">{predictError}</p>}
      </section>

      <section className="animate-in">
        <ResultCard result={result} />
      </section>

      <section className="card animate-in wide-panel">
        <h2>History Overview</h2>
        {historyError && <p className="error">{historyError}</p>}
        {loadingHistory && <p className="loading">Loading history...</p>}
        {!loadingHistory && history && (
          <>
            <div className="stat-grid">
              <div className="stat-card">
                <div className="stat-label">Total</div>
                <div className="stat-value">{history.summary.total_predictions}</div>
              </div>
              <div className="stat-card">
                <div className="stat-label">Average Score</div>
                <div className="stat-value">{history.summary.avg_risk_score.toFixed(1)}%</div>
              </div>
              <div className="stat-card">
                <div className="stat-label">Low</div>
                <div className="stat-value">{history.summary.low_count}</div>
              </div>
              <div className="stat-card">
                <div className="stat-label">Medium</div>
                <div className="stat-value">{history.summary.medium_count}</div>
              </div>
              <div className="stat-card">
                <div className="stat-label">High</div>
                <div className="stat-value">{history.summary.high_count}</div>
              </div>
            </div>

            <div className="charts-grid">
              <div className="chart-container">
                <h3>Risk Score Trend</h3>
                <ResponsiveContainer width="100%" height={260}>
                  <LineChart data={lineData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#2f3d4b" />
                    <XAxis dataKey="index" stroke="#90a1b5" />
                    <YAxis stroke="#90a1b5" domain={[0, 100]} />
                    <Tooltip
                      contentStyle={{
                        background: "#101a26",
                        border: "1px solid #2f3d4b",
                        borderRadius: "8px",
                      }}
                      labelStyle={{ color: "#d8e1ea" }}
                    />
                    <Legend />
                    <Line
                      type="monotone"
                      dataKey="score"
                      stroke="#38d39f"
                      strokeWidth={2}
                      dot={{ fill: "#38d39f", r: 3 }}
                      activeDot={{ r: 5 }}
                      name="Risk score"
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>

              <div className="chart-container">
                <h3>Risk Distribution</h3>
                <ResponsiveContainer width="100%" height={260}>
                  <PieChart>
                    <Pie
                      data={pieData}
                      cx="50%"
                      cy="50%"
                      outerRadius={88}
                      label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                      labelLine={false}
                      dataKey="value"
                    >
                      {pieData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip
                      contentStyle={{
                        background: "#101a26",
                        border: "1px solid #2f3d4b",
                        borderRadius: "8px",
                      }}
                      labelStyle={{ color: "#d8e1ea" }}
                    />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </div>

            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Timestamp</th>
                    <th>Score</th>
                    <th>Category</th>
                  </tr>
                </thead>
                <tbody>
                  {history.records.map((r) => (
                    <tr key={r.id}>
                      <td>#{r.id}</td>
                      <td>{new Date(r.created_at).toLocaleString()}</td>
                      <td>{Number(r.risk_score).toFixed(1)}%</td>
                      <td>
                        <span className={`risk-badge risk-${r.risk_category}`}>{r.risk_category}</span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </>
        )}
      </section>
    </div>
  );
}
