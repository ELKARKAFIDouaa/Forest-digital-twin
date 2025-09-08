import { useEffect, useState } from "react";
import { io } from "socket.io-client";
import './App.css';

const socket = io("http://localhost:5000"); // l'adresse de ton backend Flask

function App() {
  const [sensorData, setSensorData] = useState({});

  useEffect(() => {
    // Écoute les mises à jour du serveur
    socket.on("sensor_update", (data) => {
      setSensorData(prev => ({
        ...prev,
        [data.sensor_id]: data
      }));
    });

    // Nettoyage à la destruction du composant
    return () => {
      socket.off("sensor_update");
    };
  }, []);

  return (
    <div className="App">
      <header className="App-header">
        <h1>Capteurs en temps réel</h1>
        <ul>
          {Object.values(sensorData).map((d) => (
            <li key={d.sensor_id}>
              {d.name}: {d.value} {d.unit} ({new Date(d.timestamp).toLocaleTimeString()})
            </li>
          ))}
        </ul>
      </header>
    </div>
  );
}

export default App;
