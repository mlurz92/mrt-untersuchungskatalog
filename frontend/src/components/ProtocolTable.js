import React from 'react';

function ProtocolTable({ protocol, openOverlay }) {
  return (
    <div className="protocol-table">
      <div className="protocol-header">
        {/* Anzeige des vollständigen Navigationspfads */}
        <h3>
          {protocol.tree} &gt; {protocol.region} &gt; {protocol.examEngine} &gt; {protocol.program} &gt; {protocol.protocol}
        </h3>
        <button onClick={openOverlay} className="edit-button">
          Bearbeiten
        </button>
      </div>
      <table>
        <thead>
          <tr>
            <th>Reihenfolge</th>
            <th>Sequenzname</th>
          </tr>
        </thead>
        <tbody>
          {protocol.sequenceArray.map(seq => (
            <tr key={seq.id}>
              <td>{seq.sequence_order}</td>
              <td>{seq.sequence}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default ProtocolTable;
