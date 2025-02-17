import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './styles/style.css'; // Basisstyles inkl. dunkles Farbschema und Animationen

// Rendern der App innerhalb von React.StrictMode für zusätzliche Validierung
const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
