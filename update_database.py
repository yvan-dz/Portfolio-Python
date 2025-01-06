import sqlite3

# Verbindung zur Datenbank herstellen
connection = sqlite3.connect("database.db")
cursor = connection.cursor()

# Versuche, die Spalte hinzuzufügen
try:
    cursor.execute("ALTER TABLE projects ADD COLUMN views INTEGER DEFAULT 0")
    print("Spalte 'views' wurde erfolgreich hinzugefügt.")
except sqlite3.OperationalError:
    print("Spalte 'views' existiert bereits.")

# Änderungen speichern und Verbindung schließen
connection.commit()
connection.close()
