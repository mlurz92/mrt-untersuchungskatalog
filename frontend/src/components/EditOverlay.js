import React, { useState } from 'react';
import { gsap } from 'gsap'; // für flüssige Animationen
import { DragDropContext, Droppable, Draggable } from 'react-beautiful-dnd';

function EditOverlay({ protocol, closeOverlay, refreshProtocols }) {
  // Initialisierung des lokalen State anhand der aktuellen Sequenzliste
  const [editedSequences, setEditedSequences] = useState(
    protocol.sequenceArray.map(seq => ({ ...seq }))
  );

  // Hilfsfunktion: Reihenfolge der Liste bei Drag & Drop aktualisieren
  const reorder = (list, startIndex, endIndex) => {
    const result = Array.from(list);
    const [removed] = result.splice(startIndex, 1);
    result.splice(endIndex, 0, removed);
    // Aktualisiere die Reihenfolge basierend auf dem neuen Index
    return result.map((item, index) => ({ ...item, sequence_order: index + 1 }));
  };

  // Handler für Drag & Drop Abschluss
  const onDragEnd = (result) => {
    if (!result.destination) return;
    const reordered = reorder(editedSequences, result.source.index, result.destination.index);
    setEditedSequences(reordered);
  };

  // Neue Sequenzzeile hinzufügen
  const addSequence = () => {
    const newSequence = { id: Date.now(), sequence_order: editedSequences.length + 1, sequence: "Neue_Sequenz" };
    setEditedSequences([...editedSequences, newSequence]);
  };

  // Eine Sequenzzeile löschen und Reihenfolge neu berechnen
  const deleteSequence = (id) => {
    const updated = editedSequences.filter(seq => seq.id !== id)
      .map((seq, index) => ({ ...seq, sequence_order: index + 1 }));
    setEditedSequences(updated);
  };

  // Speichern: Animation auslösen und anschließend Overlay schließen sowie Protokolle aktualisieren
  const saveChanges = () => {
    gsap.to(".edit-overlay", { opacity: 0, duration: 0.5, onComplete: () => {
      closeOverlay();
      refreshProtocols();
    }});
  };

  return (
    <div className="edit-overlay">
      <div className="overlay-content">
        <h3>Bearbeiten: {protocol.tree} - {protocol.region}</h3>
        <DragDropContext onDragEnd={onDragEnd}>
          <Droppable droppableId="sequenceList">
            {(provided) => (
              <table ref={provided.innerRef} {...provided.droppableProps}>
                <thead>
                  <tr>
                    <th>Reihenfolge</th>
                    <th>Sequenzname</th>
                    <th>Aktion</th>
                  </tr>
                </thead>
                <tbody>
                  {editedSequences.map((seq, index) => (
                    <Draggable key={seq.id} draggableId={seq.id.toString()} index={index}>
                      {(provided) => (
                        <tr
                          ref={provided.innerRef}
                          {...provided.draggableProps}
                          {...provided.dragHandleProps}
                        >
                          <td>{seq.sequence_order}</td>
                          <td>
                            <input 
                              type="text" 
                              value={seq.sequence} 
                              onChange={(e) => {
                                const newSequences = editedSequences.map(s => 
                                  s.id === seq.id ? { ...s, sequence: e.target.value } : s
                                );
                                setEditedSequences(newSequences);
                              }}
                            />
                          </td>
                          <td>
                            <button onClick={() => deleteSequence(seq.id)}>Löschen</button>
                          </td>
                        </tr>
                      )}
                    </Draggable>
                  ))}
                  {provided.placeholder}
                </tbody>
              </table>
            )}
          </Droppable>
        </DragDropContext>
        <div className="overlay-actions">
          <button onClick={addSequence}>Zeile hinzufügen</button>
          <button onClick={saveChanges}>Speichern</button>
          <button onClick={closeOverlay}>Abbrechen</button>
        </div>
      </div>
    </div>
  );
}

export default EditOverlay;
