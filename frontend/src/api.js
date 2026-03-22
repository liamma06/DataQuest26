const API_BASE = import.meta.env.VITE_API_BASE || "http://127.0.0.1:8000";

export async function predict(payload) {
  const response = await fetch(`${API_BASE}/predict`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    const text = await response.text();
    throw new Error(`Prediction failed: ${text}`);
  }
  return response.json();
}

export async function fetchHistory(limit = 20) {
  const response = await fetch(`${API_BASE}/history?limit=${limit}`);
  if (!response.ok) {
    const text = await response.text();
    throw new Error(`History failed: ${text}`);
  }
  return response.json();
}
