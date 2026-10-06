import os
import re
import sqlite3
import secrets
from functools import wraps

import bcrypt
from dotenv import load_dotenv
from email_validator import validate_email, EmailNotValidError
from flask import (
    Flask, render_template, request, redirect,
    url_for, session, flash, g
)

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY") or secrets.token_hex(32)
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = False  # Set True when using HTTPS.
app.config["DATABASE"] = os.path.join(app.instance_path, "users.db")

os.makedirs(app.instance_path, exist_ok=True)


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(exception=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = get_db()
    db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    db.commit()


def valid_username(username):
    return bool(re.fullmatch(r"[A-Za-z0-9_]{3,30}", username))


def valid_password(password):
    return (
        len(password) >= 8
        and len(password) <= 128
        and re.search(r"[A-Za-z]", password)
        and re.search(r"\d", password)
    )


def valid_email(email):
    try:
        validate_email(email, check_deliverability=False)
        return True
    except EmailNotValidError:
        return False


def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to continue.", "error")
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped_view


@app.after_request
def add_security_headers(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "style-src 'self'; "
        "script-src 'self'; "
        "img-src 'self' data:;"
    )
    return response


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        errors = []

        if not valid_username(username):
            errors.append(
                "Username must be 3-30 characters and contain only letters, numbers, or underscore."
            )

        if not valid_email(email):
            errors.append("Enter a valid email address.")

        if not valid_password(password):
            errors.append(
                "Password must be 8-128 characters and contain at least one letter and one number."
            )

        if password != confirm_password:
            errors.append("Passwords do not match.")

        db = get_db()

        existing = db.execute(
            "SELECT id FROM users WHERE username = ? OR email = ?",
            (username, email)
        ).fetchone()

        if existing:
            errors.append("Username or email is already registered.")

        if errors:
            for error in errors:
                flash(error, "error")
            return render_template("register.html")

        password_hash = bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt()
        ).decode("utf-8")

        db.execute(
            "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
            (username, email, password_hash)
        )
        db.commit()

        flash("Registration successful. Please log in.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        db = get_db()

        user = db.execute(
            "SELECT id, username, password_hash FROM users WHERE username = ?",
            (username,)
        ).fetchone()

        if user and bcrypt.checkpw(
            password.encode("utf-8"),
            user["password_hash"].encode("utf-8")
        ):
            session.clear()
            session["user_id"] = user["id"]
            session["username"] = user["username"]

            flash("Login successful.", "success")
            return redirect(url_for("dashboard"))

        flash("Invalid username or password.", "error")

    return render_template("login.html")


@app.route("/dashboard")
@login_required
def dashboard():
    return render_template(
        "dashboard.html",
        username=session.get("username")
    )


@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("index"))


with app.app_context():
    init_db()


if __name__ == "__main__":
    app.run()
