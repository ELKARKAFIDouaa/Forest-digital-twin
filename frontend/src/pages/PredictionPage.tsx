import React, { useState } from "react";

function PredictionPage() {
  const [inputData, setInputData] = useState({});
  const [prediction, setPrediction] = useState(null);
  const [error, setError] = useState(null);

  const handleChange = (e) => {
    setInputData({
      ...inputData,
      [e.target.name]: parseFloat(e.target.value) || 0,
    });
  };

  const handleSubmit = async () => {
    try {
      const res = await fetch("http://localhost:5001/predict/single", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(inputData),
      });
      const data = await res.json();
      if (data.success) {
        setPrediction(data.prediction);
        setError(null);
      } else {
        setError(data.message);
      }
    } catch (err) {
      setError("Erreur de connexion à l’API");
    }
  };

  return (
    <div className="p-4">
      <h1 className="text-xl font-bold mb-4">Prédiction Santé Forêt 🌲</h1>

      {/* Exemple simple : saisie de deux features */}
      <input
        type="number"
        name="feature1"
        placeholder="Feature 1"
        onChange={handleChange}
        className="border p-2 mr-2"
      />
      <input
        type="number"
        name="feature2"
        placeholder="Feature 2"
        onChange={handleChange}
        className="border p-2 mr-2"
      />

      <button
        onClick={handleSubmit}
        className="bg-blue-500 text-white px-4 py-2 rounded"
      >
        Prédire
      </button>

      {prediction && (
        <p className="mt-4 text-green-600">
          ✅ Résultat : <strong>{prediction}</strong>
        </p>
      )}
      {error && <p className="mt-4 text-red-600">⚠️ {error}</p>}
    </div>
  );
}

export default PredictionPage;
