import React from 'react';
import { useNavigate } from 'react-router-dom';

const Home: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div style={{ textAlign: "center", marginTop: "50px" }}>
      <h1>Bienvenue</h1>
      <button 
        onClick={() => navigate('/login')}
        style={{ margin: "10px", padding: "10px 20px" }}
      >
        Connexion
      </button>
      <button 
        onClick={() => navigate('/register')} // ✅ cohérent avec App.tsx
        style={{ margin: "10px", padding: "10px 20px" }}
      >
        Inscription
      </button>
    </div>
  );
};

export default Home;
