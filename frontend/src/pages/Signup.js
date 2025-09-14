import React, { useState } from "react";
import { apiRequest } from "../utils/api";
import "../style/signup.css";

export default function Signup({ navigateTo }) {
  const [form, setForm] = useState({ email: "", firstName: "", lastName: "", telephone: "", password: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const handleSignup = async () => {
    try {
      setLoading(true);
      setError("");
      await apiRequest("/auth/signup", "POST", form);
      alert("Inscription réussie !");
      navigateTo("home");
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="signup-page">
      <div className="signup-left">
        <img src="/logo.png" alt="Forest Digital Twin Logo" className="logo" />
        <h1>Forest Digital Twin</h1>
        <p>Votre partenaire pour la surveillance environnementale.</p>
        <a href="#" className="help-link">Having troubles? Get Help</a>
      </div>
      <div className="signup-right">
        <div className="signup-container">
          <h2>Créez votre compte sur Digital Twin</h2>
          <input
            name="email"
            type="email"
            placeholder="Email address"
            value={form.email}
            onChange={handleChange}
          />
          <div className="name-fields">
            <input
              name="firstname"
              placeholder="Prénom"
              value={form.firstname}
              onChange={handleChange}
            />
            <input
              name="lastname"
              placeholder="Nom"
              value={form.lastname}
              onChange={handleChange}
            />
          </div>
          <input
            name="telephone"
            placeholder="Téléphone"
            value={form.telephone}
            onChange={handleChange}
          />
          <input
            name="password"
            type="password"
            placeholder="Mot de passe"
            value={form.password}
            onChange={handleChange}
          />
          <button onClick={handleSignup} disabled={loading}>
            {loading ? "Inscription..." : "S'inscrire"}
          </button>
          {error && <p className="error">{error}</p>}
          <p className="terms">
            En cliquant sur "S'inscrire", j'accepte d'avoir lu et accepté les Conditions d'utilisation et de confidentialité.
          </p>
          <button onClick={() => navigateTo("home")} className="back-btn">
            Retour
          </button>
          <a href="#" className="signup-link">Vous avez déjà un compte ?</a>
        </div>
      </div>
    </div>
  );
}