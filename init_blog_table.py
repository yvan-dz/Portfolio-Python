import sqlite3

# Verbindung zur Datenbank herstellen
connection = sqlite3.connect("database.db")
cursor = connection.cursor()

# Tabelle 'blogs' erstellen
try:
    cursor.execute("""
        CREATE TABLE blogs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            author TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            views INTEGER DEFAULT 0
        )
    """)
    print("Tabelle 'blogs' wurde erfolgreich erstellt.")
except sqlite3.OperationalError as e:
    print(f"Fehler: {e}. Wahrscheinlich existiert die Tabelle bereits.")

# Verbindung schließen
connection.commit()
connection.close()
