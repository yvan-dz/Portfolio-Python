from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, session
from flask_mail import Mail, Message
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from supabase import create_client, Client
import os
from config import SUPABASE_URL, SUPABASE_KEY
from supabase import create_client, Client
app = Flask(__name__, static_folder="static", template_folder="templates")

# Geheimen Schlüssel für Flash-Messages und Sitzungen setzen
app.secret_key = 'dein_geheimer_schlüssel'

# Konfiguration für Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'deine.email@gmail.com'
app.config['MAIL_PASSWORD'] = 'dein_passwort'

mail = Mail(app)

# Supabase konfigurieren

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Flask-Login konfigurieren
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.login_message = "Bitte melde dich an, um diese Aktion auszuführen."
login_manager.login_message_category = "warning"

class User(UserMixin):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

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

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Erfolgreich abgemeldet.", "success")
    return redirect(url_for("home"))

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

# Blogs anzeigen
@app.route("/blogs")
def blogs():
    response = supabase.table("blogs").select("*").execute()
    blogs_list = response.data if response.data else []
    return render_template("blogs.html", blogs=blogs_list)

# Blog hinzufügen
@app.route("/add_blog", methods=["GET", "POST"])
@login_required
def add_blog():
    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]
        author = current_user.username

        supabase.table("blogs").insert({
            "title": title,
            "content": content,
            "author": author
        }).execute()

        flash("Blog erfolgreich erstellt!", "success")
        return redirect(url_for("blogs"))

    return render_template("add_blog.html")

# Blog bearbeiten
@app.route("/edit_blog/<int:blog_id>", methods=["GET", "POST"])
@login_required
def edit_blog(blog_id):
    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]

        supabase.table("blogs").update({
            "title": title,
            "content": content
        }).eq("id", blog_id).execute()

        flash("Blog erfolgreich bearbeitet!", "success")
        return redirect(url_for("blogs"))

    response = supabase.table("blogs").select("*").eq("id", blog_id).single().execute()
    blog = response.data if response.data else None
    return render_template("edit_blog.html", blog=blog)

# Blog löschen
@app.route("/delete_blog/<int:blog_id>", methods=["POST"])
@login_required
def delete_blog(blog_id):
    supabase.table("blogs").delete().eq("id", blog_id).execute()
    flash("Blog erfolgreich gelöscht!", "success")
    return redirect(url_for("blogs"))

# Blog Details
@app.route("/blog/<int:blog_id>")
def blog_detail(blog_id):
    response = supabase.table("blogs").select("*").eq("id", blog_id).single().execute()
    blog = response.data if response.data else None
    return render_template("blog_detail.html", blog=blog)

# Projekte anzeigen
@app.route("/projects")
def projects():
    response = supabase.table("projects").select("*").execute()
    project_list = response.data if response.data else []
    return render_template("projects.html", projects=project_list)

# Projekt hinzufügen
@app.route("/add_project", methods=["GET", "POST"])
@login_required
def add_project():
    if request.method == "POST":
        name = request.form["name"]
        description = request.form["description"]
        image = request.form["image_url"]

        supabase.table("projects").insert({
            "name": name,
            "description": description,
            "image": image
        }).execute()

        flash("Projekt erfolgreich hinzugefügt!", "success")
        return redirect(url_for("projects"))

    return render_template("add_project.html")

# Projekt bearbeiten
@app.route("/edit_project/<int:project_id>", methods=["GET", "POST"])
@login_required
def edit_project(project_id):
    if request.method == "POST":
        name = request.form["name"]
        description = request.form["description"]
        image = request.form["image_url"]

        supabase.table("projects").update({
            "name": name,
            "description": description,
            "image": image
        }).eq("id", project_id).execute()

        flash("Projekt erfolgreich bearbeitet!", "success")
        return redirect(url_for("projects"))

    response = supabase.table("projects").select("*").eq("id", project_id).single().execute()
    project = response.data if response.data else None
    return render_template("edit_project.html", project=project)

# Projekt löschen
@app.route("/delete_project/<int:project_id>", methods=["POST"])
@login_required
def delete_project(project_id):
    # Versuch, das Projekt zu löschen
    response = supabase.table("projects").delete().eq("id", project_id).execute()

    if response.data:
        flash("Projekt erfolgreich gelöscht!", "success")
    else:
        flash("Fehler beim Löschen des Projekts. Bitte überprüfe die Logs.", "error")

    return redirect(url_for("projects"))

#dete confirm Seite
@app.route("/delete_confirm/<string:item_type>/<int:item_id>", methods=["GET"])
@login_required
def delete_confirm(item_type, item_id):
    # Abrufen der Eintragsdaten aus Supabase
    if item_type == "project":
        table_name = "projects"
    elif item_type == "blog":
        table_name = "blogs"
    else:
        flash("Ungültiger Eintragstyp.", "error")
        return redirect(url_for("home"))

    response = supabase.table(table_name).select("*").eq("id", item_id).single().execute()
    item = response.data if response.data else None

    if not item:
        flash(f"{item_type.capitalize()} nicht gefunden.", "error")
        return redirect(url_for(item_type + "s"))

    return render_template("delete_confirm.html", item=item, item_type=item_type)

# Projekt Details
@app.route("/project/<int:project_id>")
def project_detail(project_id):
    response = supabase.table("projects").select("*").eq("id", project_id).single().execute()
    project = response.data if response.data else None
    return render_template("project_detail.html", project=project)

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

@app.route("/delete_item/<string:item_type>/<int:item_id>", methods=["GET", "POST"])
@login_required
def delete_item(item_type, item_id):
    if request.method == "GET":
        # Zeige die Bestätigungsseite an
        if item_type == "project":
            table_name = "projects"
        elif item_type == "blog":
            table_name = "blogs"
        else:
            flash("Ungültiger Eintragstyp.", "error")
            return redirect(url_for("home"))

        # Abrufen des Eintrags aus Supabase
        response = supabase.table(table_name).select("*").eq("id", item_id).single().execute()
        item = response.data if response.data else None

        if not item:
            flash(f"{item_type.capitalize()} nicht gefunden.", "error")
            return redirect(url_for(item_type + "s"))

        return render_template("delete_confirm.html", item=item, item_type=item_type)

    elif request.method == "POST":
        # Führe die Löschung aus
        if item_type == "project":
            table_name = "projects"
            redirect_url = "projects"
        elif item_type == "blog":
            table_name = "blogs"
            redirect_url = "blogs"
        else:
            flash("Ungültiger Eintragstyp.", "error")
            return redirect(url_for("home"))

        # Versuch, den Eintrag zu löschen
        response = supabase.table(table_name).delete().eq("id", item_id).execute()

        if response.data:
            flash(f"{item_type.capitalize()} erfolgreich gelöscht!", "success")
        else:
            flash(f"Fehler beim Löschen des {item_type}. Bitte überprüfe die Logs.", "error")

        return redirect(url_for(redirect_url))



if __name__ == "__main__":
    app.run(debug=True)
