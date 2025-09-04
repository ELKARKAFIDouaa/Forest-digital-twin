import React, { useState, useEffect } from 'react';
import Forest2D from '../Digital twin/Forest2D';
import Forest3D from '../Digital twin/Forest3D';
import ErrorBoundary from '../components/Common/ErrorBoundary';


interface Forest {
  id: number;
  name: string;
  country: string;
}

const forests: Forest[] = [
  { id: 1, name: 'Forêt de la Mamora', country: 'Morocco' },
  { id: 2, name: 'Amazon Sector', country: 'Brazil' },
  { id: 3, name: 'Black Forest', country: 'Germany' },
];

const DigitalTwin: React.FC = () => {
  const [selectedForest, setSelectedForest] = useState<number>(1);
  const [view, setView] = useState<'2d' | '3d'>('2d');
  const [data, setData] = useState<any>(null);

  // Simulate forest data refresh
  useEffect(() => {
    const generateData = () => ({
      temperature: (20 + Math.random() * 10).toFixed(1),
      humidity: (60 + Math.random() * 20).toFixed(1),
      airQuality: (30 + Math.random() * 10).toFixed(0),
    });

    setData(generateData());
    const interval = setInterval(() => setData(generateData()), 5000);

    return () => clearInterval(interval);
  }, [selectedForest]);

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold text-gray-900">Digital Twin</h1>
      <p className="text-gray-600">
        Visualisation 2D et 3D des forêts avec données environnementales simulées
      </p>

      {/* Forest selector + view toggle */}
      <div className="flex items-center space-x-4">
        <select
          value={selectedForest}
          onChange={(e) => setSelectedForest(Number(e.target.value))}
          className="border rounded px-4 py-2"
        >
          {forests.map((f) => (
            <option key={f.id} value={f.id}>
              {f.name} ({f.country})
            </option>
          ))}
        </select>

        <button
          onClick={() => setView('2d')}
          className={`px-4 py-2 rounded ${view === '2d' ? 'bg-emerald-600 text-white' : 'bg-gray-200'}`}
        >
          2D
        </button>
        <button
          onClick={() => setView('3d')}
          className={`px-4 py-2 rounded ${view === '3d' ? 'bg-emerald-600 text-white' : 'bg-gray-200'}`}
        >
          3D
        </button>
      </div>

      {/* Forest data */}
      {data && (
        <div className="bg-white p-4 rounded-lg border grid grid-cols-3 gap-4 text-center">
          <div>
            🌡️ <span className="font-bold">{data.temperature} °C</span>
          </div>
          <div>
            💧 <span className="font-bold">{data.humidity} %</span>
          </div>
          <div>
            🌍 <span className="font-bold">AQI {data.airQuality}</span>
          </div>
        </div>
      )}

      {/* Visualization */}
      
      <div className="h-[600px] w-full border rounded-lg">
        <ErrorBoundary>
    {view === '2d' ? (
      <Forest2D forestId={selectedForest} />
    ) : (
      <Forest3D forestId={selectedForest} />
    )}
  </ErrorBoundary>
</div>
    </div>
  );
};

export default DigitalTwin;
