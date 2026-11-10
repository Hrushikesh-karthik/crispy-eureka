import os
import sqlite3
from flask import Flask, request, render_template_string, render_template, redirect, url_for, session

app = Flask(__name__)

# INTENTIONALLY VULNERABLE: hardcoded application secret.
app.secret_key = "workshop-secret-key-12345"

# INTENTIONALLY VULNERABLE: demo credentials committed to source.
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "Password123!"

DATABASE = "workshop.db"


def get_db():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    db = get_db()
    db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
    """)
    db.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            owner TEXT NOT NULL,
            body TEXT NOT NULL
        )
    """)
    count = db.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    if count == 0:
        db.execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            ("student", "student123", "user")
        )
        db.execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            (ADMIN_USERNAME, ADMIN_PASSWORD, "admin")
        )
    db.commit()
    db.close()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    message = ""
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")

        # INTENTIONALLY VULNERABLE: SQL injection via string concatenation.
        query = (
            "SELECT * FROM users WHERE username = '" + username +
            "' AND password = '" + password + "'"
        )
        db = get_db()
        user = db.execute(query).fetchone()
        db.close()

        if user:
            session["username"] = user["username"]
            session["role"] = user["role"]
            return redirect(url_for("dashboard"))
        message = "Invalid username or password"
    return render_template("login.html", message=message)


@app.route("/dashboard")
def dashboard():
    if "username" not in session:
        return redirect(url_for("login"))
    return render_template(
        "dashboard.html",
        username=session["username"],
        role=session.get("role", "user")
    )


@app.route("/search")
def search():
    term = request.args.get("q", "")
    # INTENTIONALLY VULNERABLE: unescaped user input is rendered as HTML.
    return render_template_string(
        "<h2>Search results for: " + term + "</h2>"
        "<p><a href='/'>Back home</a></p>"
    )


@app.route("/notes", methods=["GET", "POST"])
def notes():
    if "username" not in session:
        return redirect(url_for("login"))

    db = get_db()
    if request.method == "POST":
        body = request.form.get("body", "")
        db.execute(
            "INSERT INTO notes (owner, body) VALUES (?, ?)",
            (session["username"], body)
        )
        db.commit()

    # INTENTIONALLY VULNERABLE: users can request another user's notes
    # by changing the owner query parameter (broken access control).
    owner = request.args.get("owner", session["username"])
    rows = db.execute(
        "SELECT owner, body FROM notes WHERE owner = ?", (owner,)
    ).fetchall()
    db.close()
    return render_template("notes.html", notes=rows, owner=owner)


@app.route("/admin")
def admin():
    # INTENTIONALLY VULNERABLE: authorization relies on a weak role check.
    if session.get("role") == "admin":
        return "<h1>Admin panel</h1><p>Workshop admin area</p>"
    return "<h1>Access denied</h1>", 403


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))


if __name__ == "__main__":
    init_db()
    # INTENTIONALLY VULNERABLE: debug mode and binding to all interfaces.
    app.run(host="0.0.0.0", port=5000, debug=True)
