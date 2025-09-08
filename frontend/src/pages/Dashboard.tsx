import React, { useState, useEffect } from "react";
import { socket } from "../services/socket";
import EnvironmentalChart from "../components/Dashboard/EnvironmentalChart";
import StatsCard from "../components/Dashboard/StatsCard";
import { Activity, TrendingUp, AlertCircle } from "lucide-react";

interface SensorData {
  sensor_id: number;
  name: string;
  value: number;
  unit: string;
  timestamp: string;
}

const Dashboard: React.FC = () => {
  const [sensorData, setSensorData] = useState<SensorData[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let isMounted = true;

    // 1. Fetch historical data first
    async function fetchHistory() {
      try {
        const res = await fetch("http://localhost:5000/api/history?limit=500");
        const history: SensorData[] = await res.json();
        if (isMounted) {
          setSensorData(history);
          setLoading(false);
        }
      } catch (err) {
        console.error("Failed to load history:", err);
        setLoading(false);
      }
    }

    fetchHistory();

    // 2. Listen for real-time updates
    socket.on("sensor_data", (data: SensorData) => {
      if (isMounted) {
        setSensorData((prev) => [...prev, data]);
      }
    });

    // Cleanup
    return () => {
      isMounted = false;
      socket.off("sensor_data");
    };
  }, []);

  // Show loading while history is being fetched
  if (loading) {
    return <div className="p-6 text-lg font-semibold">Loading historical data...</div>;
  }

  // Group data by sensor name
  const groupedData = sensorData.reduce((acc, curr) => {
    if (!acc[curr.name]) acc[curr.name] = [];
    acc[curr.name].push({ time: curr.timestamp, value: curr.value });
    return acc;
  }, {} as Record<string, { time: string; value: number }[]>);

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Dashboard</h1>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatsCard title="Capteurs totaux" value={Object.keys(groupedData).length} icon={Activity} color="blue" />
        <StatsCard title="Capteurs actifs" value={Object.keys(groupedData).length} icon={TrendingUp} color="green" />
        <StatsCard title="Alertes critiques" value={2} icon={AlertCircle} color="red" />
      </div>

      {/* Dynamic Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {Object.entries(groupedData).map(([name, data], idx) => (
          <EnvironmentalChart
            key={idx}
            title={name}
            data={data}
            unit={sensorData.find((d) => d.name === name)?.unit || ""}
            color={["red", "blue", "green", "orange", "purple", "teal", "pink"][idx % 7]}
          />
        ))}
      </div>
    </div>
  );
};

export default Dashboard;
