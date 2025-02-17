import os
import json
import sqlite3

DB_FILE = "protocols.db"
JSON_FILE = "protocols.json"

def create_connection(db_file):
    """
    - Stellt eine Verbindung zur SQLite-Datenbank her.
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except sqlite3.Error as e:
        print("Fehler beim Verbinden mit der Datenbank:", e)
    return conn

def create_tables(conn):
    """
    - Erstellt die Tabellen 'protocols' und 'sequences', falls diese noch nicht existieren.
    """
    try:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS protocols (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tree TEXT,
                region TEXT,
                examEngine TEXT,
                program TEXT,
                protocol TEXT
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS sequences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                protocol_id INTEGER,
                sequence_order INTEGER,
                sequence TEXT,
                FOREIGN KEY(protocol_id) REFERENCES protocols(id)
            )
        """)
        conn.commit()
    except sqlite3.Error as e:
        print("Fehler beim Erstellen der Tabellen:", e)

def import_json_data(conn):
    """
    - Liest die JSON-Datei 'protocols.json' ein und importiert die Daten in die Datenbank.
    - Jeder JSON-Eintrag wird in die Tabelle 'protocols' eingefügt und seine Sequenzen in 'sequences'
      unter Beachtung der numerischen Reihenfolge übertragen.
    """
    try:
        with open(JSON_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print("Fehler beim Lesen der JSON-Datei:", e)
        return

    try:
        cur = conn.cursor()
        for entry in data:
            tree = entry.get("tree")
            region = entry.get("region")
            examEngine = entry.get("examEngine")
            program = entry.get("program")
            protocol_field = entry.get("protocol")
            # Einfügen in Tabelle 'protocols'
            cur.execute("""
                INSERT INTO protocols (tree, region, examEngine, program, protocol)
                VALUES (?, ?, ?, ?, ?)
            """, (tree, region, examEngine, program, protocol_field))
            protocol_id = cur.lastrowid

            # Einfügen der Sequenzen in der vorgegebenen Reihenfolge
            sequence_array = entry.get("sequenceArray", [])
            order = 1
            for sequence in sequence_array:
                cur.execute("""
                    INSERT INTO sequences (protocol_id, sequence_order, sequence)
                    VALUES (?, ?, ?)
                """, (protocol_id, order, sequence))
                order += 1
        conn.commit()
        print("Datenbank erstellt und JSON-Daten erfolgreich importiert.")
    except sqlite3.Error as e:
        print("Fehler beim Importieren der JSON-Daten:", e)

def initialize_database():
    """
    - Überprüft, ob die Datenbank existiert.
    - Falls nicht, wird die Datenbank erstellt, die Tabellen werden angelegt und die JSON-Daten werden importiert.
    - Andernfalls werden die bestehenden Daten verwendet.
    """
    if not os.path.exists(DB_FILE):
        print("Datenbank nicht gefunden. Starte Import aus 'protocols.json' ...")
        conn = create_connection(DB_FILE)
        if conn is not None:
            create_tables(conn)
            import_json_data(conn)
            conn.close()
        else:
            print("Fehler! Es konnte keine Verbindung zur Datenbank hergestellt werden.")
    else:
        print("Datenbank existiert bereits. Es werden die bestehenden Daten verwendet.")

if __name__ == "__main__":
    initialize_database()
