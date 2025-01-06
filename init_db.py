import sqlite3

# Verbindung zur Datenbank herstellen
connection = sqlite3.connect("database.db")
cursor = connection.cursor()

# Tabelle für Projekte erstellen (falls nicht vorhanden)
cursor.execute("""
    CREATE TABLE IF NOT EXISTS projects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT NOT NULL,
        image TEXT NOT NULL
    )
""")

# Prüfen, ob bereits Projekte existieren
cursor.execute("SELECT COUNT(*) FROM projects")
project_count = cursor.fetchone()[0]

if project_count == 0:
    # Beispiel-Daten für Projekte hinzufügen
    cursor.execute("""
        INSERT INTO projects (name, description, image) VALUES
        ('Projekt 1', 'Beschreibung des Projekts 1', 'static/images/projekt1.png'),
        ('Projekt 2', 'Beschreibung des Projekts 2', 'static/images/projekt2.png'),
        ('Projekt 3', 'Beschreibung des Projekts 3', 'static/images/projekt3.png')
    """)
    print("Beispieldaten für Projekte wurden hinzugefügt.")
else:
    print("Projekte existieren bereits. Keine neuen Einträge hinzugefügt.")

# Tabelle für Blogs erstellen (falls nicht vorhanden)
cursor.execute("""
    CREATE TABLE IF NOT EXISTS blogs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        author TEXT NOT NULL,
        image TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        views INTEGER DEFAULT 0
    )
""")

# Prüfen, ob bereits Blogs existieren
cursor.execute("SELECT COUNT(*) FROM blogs")
blog_count = cursor.fetchone()[0]

if blog_count == 0:
    # Beispiel-Daten für Blogs hinzufügen
    cursor.execute("""
        INSERT INTO blogs (title, content, author, image) VALUES
        ('Blog 1', 'Inhalt des Blogs 1', 'Max Mustermann', 'static/images/blog1.png'),
        ('Blog 2', 'Inhalt des Blogs 2', 'Erika Musterfrau', 'static/images/blog2.png'),
        ('Blog 3', 'Inhalt des Blogs 3', 'Max Mustermann', 'static/images/blog3.png')
    """)
    print("Beispieldaten für Blogs wurden hinzugefügt.")
else:
    print("Blogs existieren bereits. Keine neuen Einträge hinzugefügt.")

# Änderungen speichern und Verbindung schließen
connection.commit()
connection.close()
