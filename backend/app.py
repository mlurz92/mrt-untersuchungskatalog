from flask import Flask, request, jsonify
import sqlite3
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Erlaubt Cross-Origin Anfragen

DB_FILE = "protocols.db"

def get_db_connection():
    """
    - Stellt Verbindung zur Datenbank her und konfiguriert Row Factory.
    """
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/api/protocols', methods=['GET'])
def get_protocols():
    """
    - Gibt alle Protokolle mit zugehörigen Sequenzen zurück.
    """
    conn = get_db_connection()
    protocols = conn.execute('SELECT * FROM protocols').fetchall()
    result = []
    for protocol in protocols:
        pid = protocol['id']
        sequences = conn.execute(
            'SELECT * FROM sequences WHERE protocol_id = ? ORDER BY sequence_order',
            (pid,)
        ).fetchall()
        sequences_list = [
            {
                "id": seq["id"],
                "sequence_order": seq["sequence_order"],
                "sequence": seq["sequence"]
            } for seq in sequences
        ]
        result.append({
            "id": protocol["id"],
            "tree": protocol["tree"],
            "region": protocol["region"],
            "examEngine": protocol["examEngine"],
            "program": protocol["program"],
            "protocol": protocol["protocol"],
            "sequenceArray": sequences_list
        })
    conn.close()
    return jsonify(result), 200

@app.route('/api/protocols/<int:protocol_id>', methods=['GET'])
def get_protocol_by_id(protocol_id):
    """
    - Liefert einen einzelnen Protokolleintrag inkl. Sequenzen basierend auf der ID.
    """
    conn = get_db_connection()
    protocol = conn.execute(
        'SELECT * FROM protocols WHERE id = ?',
        (protocol_id,)
    ).fetchone()
    if protocol is None:
        conn.close()
        return jsonify({"error": "Protocol not found"}), 404

    sequences = conn.execute(
        'SELECT * FROM sequences WHERE protocol_id = ? ORDER BY sequence_order',
        (protocol_id,)
    ).fetchall()
    sequence_list = [
        {
            "id": seq["id"],
            "sequence_order": seq["sequence_order"],
            "sequence": seq["sequence"]
        } for seq in sequences
    ]
    result = {
        "id": protocol["id"],
        "tree": protocol["tree"],
        "region": protocol["region"],
        "examEngine": protocol["examEngine"],
        "program": protocol["program"],
        "protocol": protocol["protocol"],
        "sequenceArray": sequence_list
    }
    conn.close()
    return jsonify(result), 200

@app.route('/api/protocols', methods=['POST'])
def create_protocol():
    """
    - Erstellt einen neuen Protokolleintrag inkl. Sequenzliste.
    - Erwartet JSON mit: tree, region, examEngine, program, protocol, sequenceArray.
    """
    if not request.json:
        return jsonify({"error": "Missing JSON in request"}), 400

    required_fields = ["tree", "region", "examEngine", "program", "protocol", "sequenceArray"]
    data = request.json
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing field: {field}"}), 400

    tree = data["tree"]
    region = data["region"]
    examEngine = data["examEngine"]
    program = data["program"]
    protocol_field = data["protocol"]
    sequenceArray = data["sequenceArray"]

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO protocols (tree, region, examEngine, program, protocol)
        VALUES (?, ?, ?, ?, ?)
    """, (tree, region, examEngine, program, protocol_field))
    protocol_id = cursor.lastrowid

    # Sequenzen mit fortlaufender Reihenfolge einfügen
    order = 1
    for sequence in sequenceArray:
        cursor.execute("""
            INSERT INTO sequences (protocol_id, sequence_order, sequence)
            VALUES (?, ?, ?)
        """, (protocol_id, order, sequence))
        order += 1

    conn.commit()
    conn.close()
    return jsonify({"success": True, "id": protocol_id}), 201

@app.route('/api/protocols/<int:protocol_id>', methods=['PUT'])
def update_protocol(protocol_id):
    """
    - Aktualisiert existierende Felder eines Protokolleintrags:
      tree, region, examEngine, program, protocol.
    """
    if not request.json:
        return jsonify({"error": "Missing JSON in request"}), 400

    data = request.json
    allowed_fields = ["tree", "region", "examEngine", "program", "protocol"]
    update_fields = { key: data[key] for key in allowed_fields if key in data }
    if not update_fields:
        return jsonify({"error": "No valid fields to update."}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    protocol = cursor.execute(
        'SELECT * FROM protocols WHERE id = ?',
        (protocol_id,)
    ).fetchone()
    if protocol is None:
        conn.close()
        return jsonify({"error": "Protocol not found"}), 404

    for key, value in update_fields.items():
        cursor.execute(f"UPDATE protocols SET {key} = ? WHERE id = ?", (value, protocol_id))
    conn.commit()
    conn.close()
    return jsonify({"success": True}), 200

@app.route('/api/protocols/<int:protocol_id>', methods=['DELETE'])
def delete_protocol(protocol_id):
    """
    - Löscht den Protokolleintrag und alle zugehörigen Sequenzen anhand der ID.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    protocol = cursor.execute(
        'SELECT * FROM protocols WHERE id = ?',
        (protocol_id,)
    ).fetchone()
    if protocol is None:
        conn.close()
        return jsonify({"error": "Protocol not found"}), 404

    cursor.execute('DELETE FROM sequences WHERE protocol_id = ?', (protocol_id,))
    cursor.execute('DELETE FROM protocols WHERE id = ?', (protocol_id,))
    conn.commit()
    conn.close()
    return jsonify({"success": True}), 200

@app.route('/api/protocols/<int:protocol_id>/sequences', methods=['PUT'])
def update_sequences(protocol_id):
    """
    - Aktualisiert die Sequenzliste eines Protokolleintrags.
    - Erwartet JSON mit dem Schlüssel 'sequenceArray', einem Array von Sequenzobjekten.
    - Bestehende Sequenzen werden gelöscht und die neuen werden in der angegebenen Reihenfolge eingefügt.
    """
    if not request.json or 'sequenceArray' not in request.json:
        return jsonify({"error": "Missing sequenceArray in request"}), 400
    sequenceArray = request.json['sequenceArray']

    conn = get_db_connection()
    cursor = conn.cursor()

    # Überprüfen, ob der Protokolleintrag existiert
    protocol = cursor.execute("SELECT * FROM protocols WHERE id = ?", (protocol_id,)).fetchone()
    if protocol is None:
        conn.close()
        return jsonify({"error": "Protocol not found"}), 404

    # Lösche alle bestehenden Sequenzen für den Protokolleintrag
    cursor.execute("DELETE FROM sequences WHERE protocol_id = ?", (protocol_id,))

    # Füge die neuen Sequenzen in der Reihenfolge ein
    order = 1
    for seq in sequenceArray:
        sequence_value = seq['sequence']
        cursor.execute("""
            INSERT INTO sequences (protocol_id, sequence_order, sequence)
            VALUES (?, ?, ?)
        """, (protocol_id, order, sequence_value))
        order += 1

    conn.commit()
    conn.close()
    return jsonify({"success": True}), 200

if __name__ == "__main__":
    if not os.path.exists(DB_FILE):
        print("Datenbank 'protocols.db' nicht gefunden. Bitte zuerst den Import durchführen.")
    else:
        app.run(host="0.0.0.0", port=5000, debug=True)
