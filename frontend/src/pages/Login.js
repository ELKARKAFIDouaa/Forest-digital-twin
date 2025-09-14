import React, { useState } from "react";
import { apiRequest } from "../utils/api";
import "../style/login.css"; 

export default function Login({ navigateTo }) {
  const [form, setForm] = useState({ email: "", password: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const handleLogin = async () => {
    try {
      setLoading(true);
      setError("");
      const response = await apiRequest("/auth/login", "POST", form);
      alert("Connexion réussie !");
      navigateTo("home"); 
    } catch (err) {
      setError(err.message || "Une erreur s'est produite");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-page">
      <div className="login-left">
        <img src="/logo2.png" alt="Forest Digital Twin Logo" className="logo" />
        <h1>Forest Digital Twin</h1>
        <p>Votre partenaire pour la surveillance environnementale.</p>
        <a href="#" className="help-link">Having troubles? Get Help</a>
      </div>
      <div className="login-right">
        <div className="login-container">
          <h2>Connectez-vous à Digital Twin</h2>
          <input
            name="email"
            type="email"
            placeholder="Email address"
            value={form.email}
            onChange={handleChange}
          />
          <input
            name="password"
            type="password"
            placeholder="Mot de passe"
            value={form.password}
            onChange={handleChange}
          />
          <button onClick={handleLogin} disabled={loading}>
            {loading ? "Connexion..." : "Se connecter"}
          </button>
          {error && <p className="error">{error}</p>}
          <p className="terms">
            En cliquant sur "Se connecter", j'accepte d'avoir lu et accepté les Conditions d'utilisation et de confidentialité.
          </p>
          <button onClick={() => navigateTo("home")} className="back-btn">
            Retour
          </button>
          <p className="signup-link">Vous n'avez pas de compte ? <a href="#" onClick={() => navigateTo("signup")}>Inscrivez-vous</a></p>
        </div>
      </div>
    </div>
  );
}