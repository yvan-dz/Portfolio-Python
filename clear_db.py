import sqlite3

# Verbindung zur Datenbank herstellen
def connect_to_db():
    try:
        connection = sqlite3.connect("database.db")
        return connection
    except sqlite3.Error as e:
        print(f"Fehler bei der Verbindung zur Datenbank: {e}")
        return None

# Datenbank löschen mit Bestätigung
def clear_table(table_name):
    connection = connect_to_db()
    if not connection:
        return

    cursor = connection.cursor()

    try:
        confirmation = input(f"Möchtest du wirklich alle Daten aus der Tabelle '{table_name}' löschen? (ja/nein): ").strip().lower()
        if confirmation != "ja":
            print("Löschvorgang abgebrochen.")
            return

        cursor.execute(f"DELETE FROM {table_name}")
        connection.commit()
        print(f"Alle Einträge in der Tabelle '{table_name}' wurden gelöscht.")
    except sqlite3.Error as e:
        print(f"Fehler beim Löschen der Tabelle '{table_name}': {e}")
    finally:
        connection.close()

if __name__ == "__main__":
    print("Verfügbare Tabellen: projects, blogs")
    table = input("Welche Tabelle möchtest du löschen? ").strip()
    if table in ["projects", "blogs"]:
        clear_table(table)
    else:
        print("Ungültige Tabellenwahl.")
