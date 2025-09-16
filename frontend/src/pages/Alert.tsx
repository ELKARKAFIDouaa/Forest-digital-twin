import { useEffect, useState } from "react";
import { getAlerts, acknowledgeAlert } from "../services/alertAPI";
import { getSensorHistory } from "../services/sensorAPI";
import { Alert, SensorData } from "../types";
import { AlertTriangle } from "lucide-react";
import { Line } from "react-chartjs-2"; // utiliser chart.js
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js';

// Enregistrement global
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

const AlertsPage: React.FC = () => {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [history, setHistory] = useState<SensorData[]>([]);
  const [loadingAlerts, setLoadingAlerts] = useState(true);
  const [loadingHistory, setLoadingHistory] = useState(true);

  // --- Fetch alertes ---
  useEffect(() => {
    const fetchAlerts = async () => {
      try {
        const data = await getAlerts();
        setAlerts(data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoadingAlerts(false);
      }
    };
    fetchAlerts();
    const interval = setInterval(fetchAlerts, 15000);
    return () => clearInterval(interval);
  }, []);

  const handleAcknowledge = async (id: string) => {
    try {
      const updated = await acknowledgeAlert(id);
      setAlerts(prev => prev.map(a => (a.id === updated.id ? updated : a)));
    } catch (err) {
      console.error(err);
    }
  };

  // --- Fetch historique ---
  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const data = await getSensorHistory(50);
        setHistory(data);
      } catch (err) {
        console.error("Failed to load history:", err);
      } finally {
        setLoadingHistory(false);
      }
    };
    fetchHistory();
  }, []);

  // --- Préparer les données du graphique ---
  const chartData = {
    labels: history.map(h => new Date(h.timestamp).toLocaleTimeString()),
    datasets: [
      {
        label: "Valeurs capteurs",
        data: history.map(h => h.value),
        borderColor: "rgb(34,197,94)",
        backgroundColor: "rgba(34,197,94,0.3)",
        tension: 0.3,
      },
    ],
  };
  
  return (
    <div className="p-6 space-y-8">
      <h1 className="text-2xl font-bold flex items-center gap-2">
        <AlertTriangle className="text-red-500" /> Alertes
      </h1>

      {/* --- Alertes --- */}
      {loadingAlerts ? <p>Chargement des alertes...</p> :
        alerts.length === 0 ? <p className="text-gray-500">Aucune alerte active</p> :
        <div className="space-y-4">
          {alerts.map(alert => (
            <div key={alert.id} className={`p-4 rounded-xl shadow flex justify-between items-center ${
              alert.severity === "high" ? "bg-red-100 border border-red-400" :
              alert.severity === "medium" ? "bg-yellow-100 border border-yellow-400" :
              "bg-blue-100 border border-blue-400"
            }`}>
              <div>
                <p className="font-semibold">{alert.message}</p>
                <p className="text-xs text-gray-600">{new Date(alert.createdAt).toLocaleString()}</p>
              </div>
              {!alert.acknowledged && (
                <button onClick={() => handleAcknowledge(alert.id)} className="bg-emerald-500 text-white px-3 py-1 rounded-lg hover:bg-emerald-600">
                  Acquitter
                </button>
              )}
            </div>
          ))}
        </div>
      }

      {/* --- Historique graphique --- */}
      <h2 className="text-xl font-bold mt-8 mb-4">Historique des mesures</h2>
      {loadingHistory ? <p>Chargement de l'historique...</p> :
        <Line data={chartData} />
      }
    </div>
  );
};

export default AlertsPage;
