import React, { useEffect, useState, useRef } from 'react';
import axios from 'axios';
import { gsap } from 'gsap';
import Navigation from './components/Navigation';
import ProtocolTable from './components/ProtocolTable';
import EditOverlay from './components/EditOverlay';

function App() {
  const [protocols, setProtocols] = useState([]);
  const [selectedProtocol, setSelectedProtocol] = useState(null);
  const [showOverlay, setShowOverlay] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const mainContainerRef = useRef(null);

  // Protokolle laden und Ladezustand/Fehler aktualisieren
  useEffect(() => {
    axios.get('http://localhost:5000/api/protocols')
      .then(response => {
        setProtocols(response.data);
        setLoading(false);
        // Sanftes Einblenden des Hauptbereichs
        gsap.fromTo(mainContainerRef.current, { opacity: 0 }, { opacity: 1, duration: 1 });
      })
      .catch(err => {
        console.error("Fehler beim Laden der Protokolle:", err);
        setError("Fehler beim Laden der Protokolle.");
        setLoading(false);
      });
  }, []);

  return (
    <div className="app-container">
      {/* Linke Navigation */}
      <Navigation protocols={protocols} onSelectProtocol={setSelectedProtocol} />
      
      {/* Hauptbereich */}
      <div className="main-container" ref={mainContainerRef}>
        {loading ? (
          <div className="placeholder">Lade Protokolle...</div>
        ) : error ? (
          <div className="placeholder">{error}</div>
        ) : selectedProtocol ? (
          <ProtocolTable protocol={selectedProtocol} openOverlay={() => setShowOverlay(true)} />
        ) : (
          <div className="placeholder">Bitte wähle einen Eintrag aus der Navigation.</div>
        )}
      </div>
      
      {/* Bearbeitungsoverlay */}
      {showOverlay && (
        <EditOverlay 
          protocol={selectedProtocol} 
          closeOverlay={() => setShowOverlay(false)} 
          refreshProtocols={() => {
            axios.get('http://localhost:5000/api/protocols')
              .then(response => setProtocols(response.data))
              .catch(error => console.error("Fehler beim Aktualisieren:", error));
          }}
        />
      )}
    </div>
  );
}

export default App;
