from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
from flask_mail import Mail, Message
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import sqlite3
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Geheimen Schlüssel für Flash-Messages und Sitzungen setzen
app.secret_key = 'dein_geheimer_schlüssel'

# Konfiguration für Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'deine.email@gmail.com'
app.config['MAIL_PASSWORD'] = 'dein_passwort'

mail = Mail(app)

# Ordner für Bild-Uploads konfigurieren
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Route für den Zugriff auf hochgeladene Bilder
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Flask-Login konfigurieren
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.login_message = "Bitte melde dich an, um diese Aktion auszuführen."
login_manager.login_message_category = "warning"

# Benutzerklasse und Benutzerliste
class User(UserMixin):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

# Beispielbenutzer
users = {
    "admin": User(id=1, username="admin", password="pass123")
}

@login_manager.user_loader
def load_user(user_id):
    return next((u for u in users.values() if u.id == int(user_id)), None)

# Login-Route
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = next((u for u in users.values() if u.username == username and u.password == password), None)

        if user:
            login_user(user)
            flash("Erfolgreich angemeldet!", "success")
            return redirect(url_for("blogs"))
        else:
            flash("Ungültige Anmeldedaten.", "error")
    return render_template("login.html")

# Logout-Route
@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Erfolgreich abgemeldet.", "success")
    return redirect(url_for("home"))

# Startseite
@app.route("/")
def home():
    return render_template("index.html")

# Über mich
@app.route("/about")
def about():
    return render_template("about.html")

# Blog-Übersicht
@app.route("/blogs")
def blogs():
    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()

    cursor.execute("SELECT id, title, author, created_at, views FROM blogs")
    blogs_list = [
        {"id": row[0], "title": row[1], "author": row[2], "created_at": row[3], "views": row[4]}
        for row in cursor.fetchall()
    ]

    connection.close()
    return render_template("blogs.html", blogs=blogs_list)

# Blog erstellen
@app.route("/add_blog", methods=["GET", "POST"])
@login_required
def add_blog():
    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]
        author = current_user.username

        connection = sqlite3.connect("database.db")
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO blogs (title, content, author) VALUES (?, ?, ?)
        """, (title, content, author))

        connection.commit()
        connection.close()

        flash("Blog erfolgreich erstellt!", "success")
        return redirect(url_for("blogs"))

    return render_template("add_blog.html")

# Blog bearbeiten
@app.route("/edit_blog/<int:blog_id>", methods=["GET", "POST"])
@login_required
def edit_blog(blog_id):
    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()

    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]

        cursor.execute("""
            UPDATE blogs SET title = ?, content = ? WHERE id = ?
        """, (title, content, blog_id))

        connection.commit()
        connection.close()

        flash("Blog erfolgreich bearbeitet!", "success")
        return redirect(url_for("blogs"))

    # Blog-Daten abrufen
    cursor.execute("SELECT id, title, content FROM blogs WHERE id = ?", (blog_id,))
    blog = cursor.fetchone()
    connection.close()

    if not blog:
        flash("Blog nicht gefunden.", "error")
        return redirect(url_for("blogs"))

    blog_data = {
        "id": blog[0],
        "title": blog[1],
        "content": blog[2]
    }

    return render_template("edit_blog.html", blog=blog_data)

# Blog löschen
@app.route("/delete_blog/<int:blog_id>", methods=["POST"])
@login_required
def delete_blog(blog_id):
    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()

    cursor.execute("DELETE FROM blogs WHERE id = ?", (blog_id,))
    connection.commit()
    connection.close()

    flash("Blog erfolgreich gelöscht!", "success")
    return redirect(url_for("blogs"))

# Blog-Details anzeigen (inkl. Views erhöhen)
@app.route("/blog/<int:blog_id>")
def blog_detail(blog_id):
    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM blogs WHERE id = ?", (blog_id,))
    blog = cursor.fetchone()

    if not blog:
        flash("Blog nicht gefunden.", "error")
        return redirect(url_for("blogs"))

    cursor.execute("UPDATE blogs SET views = views + 1 WHERE id = ?", (blog_id,))
    connection.commit()
    connection.close()

    blog_data = {
        "id": blog[0],
        "title": blog[1],
        "content": blog[2],
        "author": blog[3],
        "created_at": blog[4],
        "views": blog[5] + 1
    }

    return render_template("blog_detail.html", blog=blog_data)

# Projekte anzeigen
@app.route("/projects")
def projects():
    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()

    cursor.execute("SELECT id, name, description, image FROM projects")
    project_list = [
        {"id": row[0], "name": row[1], "description": row[2], "image": row[3]}
        for row in cursor.fetchall()
    ]

    connection.close()
    return render_template("projects.html", projects=project_list)

# Kontaktformular
@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        message = request.form["message"]

        msg = Message(
            "Kontaktformular Nachricht",
            sender=email,
            recipients=["deine.email@gmail.com"]
        )
        msg.body = f"Name: {name}\nE-Mail: {email}\nNachricht:\n{message}"
        mail.send(msg)

        flash("Deine Nachricht wurde erfolgreich gesendet!", "success")
        return redirect(url_for("contact"))
    return render_template("contact.html")

# Neues Projekt hinzufügen
@app.route("/add_project", methods=["GET", "POST"])
@login_required
def add_project():
    if request.method == "POST":
        name = request.form["name"]
        description = request.form["description"]
        image_url = request.form["image_url"]

        # Bild-Upload verarbeiten, falls vorhanden
        image_path = None
        if "image_file" in request.files:
            file = request.files["image_file"]
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(image_path)

        # Bevorzuge hochgeladenes Bild, falls vorhanden
        image = image_path if image_path else image_url

        # Projekt in die Datenbank einfügen
        connection = sqlite3.connect("database.db")
        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO projects (name, description, image) VALUES (?, ?, ?)
        """, (name, description, image))
        connection.commit()
        connection.close()

        flash("Projekt erfolgreich hinzugefügt!", "success")
        return redirect(url_for("projects"))
    return render_template("add_project.html")

# Projekt bearbeiten
@app.route("/edit_project/<int:project_id>", methods=["GET", "POST"])
@login_required
def edit_project(project_id):
    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()

    if request.method == "POST":
        name = request.form["name"]
        description = request.form["description"]
        image_url = request.form["image_url"]

        # Bild-Upload verarbeiten, falls vorhanden
        image_path = None
        if "image_file" in request.files:
            file = request.files["image_file"]
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(image_path)

        # Bevorzuge hochgeladenes Bild, falls vorhanden
        image = image_path if image_path else image_url

        cursor.execute("""
            UPDATE projects SET name = ?, description = ?, image = ? WHERE id = ?
        """, (name, description, image, project_id))

        connection.commit()
        connection.close()

        flash("Projekt erfolgreich bearbeitet!", "success")
        return redirect(url_for("projects"))

    cursor.execute("SELECT * FROM projects WHERE id = ?", (project_id,))
    project = cursor.fetchone()

    connection.close()
    return render_template("edit_project.html", project=project)

# Projekt löschen
@app.route("/delete_project/<int:project_id>", methods=["GET", "POST"])
@login_required
def delete_project(project_id):
    if request.method == "POST":
        connection = sqlite3.connect("database.db")
        cursor = connection.cursor()

        cursor.execute("DELETE FROM projects WHERE id = ?", (project_id,))
        connection.commit()
        connection.close()

        flash("Projekt erfolgreich gelöscht!", "success")
        return redirect(url_for("projects"))

    flash("Möchtest du dieses Projekt wirklich löschen? Bestätige unten.", "warning")
    return render_template("delete_confirm.html", project_id=project_id)

@app.route("/project/<int:project_id>")
def project_detail(project_id):
    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()

    # Hole die Projektdaten aus der Datenbank
    cursor.execute("SELECT id, name, description, image FROM projects WHERE id = ?", (project_id,))
    project = cursor.fetchone()

    # Falls kein Projekt gefunden wurde, leite zur Projekte-Seite weiter
    if not project:
        flash("Projekt nicht gefunden.", "error")
        return redirect(url_for("projects"))

    project_data = {
        "id": project[0],
        "name": project[1],
        "description": project[2],
        "image": project[3]
    }

    connection.close()
    return render_template("project_detail.html", project=project_data)

if __name__ == "__main__":
    app.run(debug=True)
