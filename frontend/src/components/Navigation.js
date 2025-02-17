import React, { useState } from 'react';

function Navigation({ protocols, onSelectProtocol }) {
  const [searchTerm, setSearchTerm] = useState('');

  // Filtert Protokolle anhand des Suchbegriffs (case-insensitive)
  const filteredProtocols = protocols.filter(protocol => {
    const combinedText = `${protocol.tree} ${protocol.region} ${protocol.examEngine} ${protocol.program} ${protocol.protocol}`.toLowerCase();
    return combinedText.includes(searchTerm.toLowerCase());
  });

  // Gruppierung der Protokolle nach der obersten Hierarchieebene (tree)
  const groupedByTree = filteredProtocols.reduce((groups, protocol) => {
    if (!groups[protocol.tree]) {
      groups[protocol.tree] = [];
    }
    groups[protocol.tree].push(protocol);
    return groups;
  }, {});

  return (
    <div className="navigation-container">
      <h2>Navigation</h2>
      <input
        type="text"
        placeholder="Suche..."
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)}
        style={{
          width: '100%',
          padding: '0.5rem',
          marginBottom: '1rem',
          borderRadius: '4px',
          border: '1px solid #333',
          backgroundColor: '#2e2e2e',
          color: '#e0e0e0'
        }}
      />
      <div className="nav-groups">
        {Object.keys(groupedByTree).map(tree => (
          <div key={tree} className="nav-group">
            <h3>{tree}</h3>
            <ul className="nav-list">
              {groupedByTree[tree].map(protocol => (
                <li key={protocol.id} onClick={() => onSelectProtocol(protocol)}>
                  {protocol.region} &gt; {protocol.examEngine}
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>
    </div>
  );
}

export default Navigation;
