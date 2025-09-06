
const API_URL = "http://127.0.0.1:5000";

export async function apiRequest(endpoint, method = "GET", body = null) {
  const options = {
    method,
    headers: { "Content-Type": "application/json" },
    credentials: "include"
  };
  if (body) options.body = JSON.stringify(body);

  const res = await fetch(`${API_URL}${endpoint}`, options);
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || "Erreur API");
  return data;
}
