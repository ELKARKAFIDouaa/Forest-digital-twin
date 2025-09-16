import { Alert } from "../types";

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:5000/api";

export const getAlerts = async (): Promise<Alert[]> => {
  const res = await fetch(`${API_BASE_URL}/alerts/`, {
    headers: { "Authorization": `Bearer ${localStorage.getItem("token")}` }
  });
  if (!res.ok) throw new Error("Erreur récupération alertes");
  return res.json();
};

export const acknowledgeAlert = async (id: string): Promise<Alert> => {
  const res = await fetch(`${API_BASE_URL}/alerts/${id}/ack`, {
    method: "PATCH",
    headers: { "Authorization": `Bearer ${localStorage.getItem("token")}` }
  });
  if (!res.ok) throw new Error("Erreur acquittement alerte");
  return res.json();
};
