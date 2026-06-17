import sqlite3
from functools import wraps

from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from .db import get_db


main = Blueprint("main", __name__)


def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if not session.get("user_id"):
            flash("Please sign in to view that page.", "warning")
            return redirect(url_for("main.login"))
        return view(*args, **kwargs)

    return wrapped_view


def admin_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if not session.get("user_id"):
            flash("Please sign in to view the admin panel.", "warning")
            return redirect(url_for("main.login"))
        if session.get("role") != "admin":
            flash("Admin access is required for that page.", "danger")
            return redirect(url_for("main.dashboard"))
        return view(*args, **kwargs)

    return wrapped_view


@main.route("/")
def home():
    db = get_db()
    stats = {
        "jobs": db.execute("SELECT COUNT(*) AS total FROM jobs").fetchone()["total"],
        "candidates": db.execute("SELECT COUNT(*) AS total FROM candidates").fetchone()[
            "total"
        ],
        "feedback": db.execute("SELECT COUNT(*) AS total FROM feedback").fetchone()[
            "total"
        ],
    }
    recent_jobs = db.execute(
        "SELECT id, title, department, location FROM jobs ORDER BY id DESC LIMIT 3"
    ).fetchall()
    return render_template("home.html", stats=stats, recent_jobs=recent_jobs)


@main.route("/login", methods=("GET", "POST"))
def login():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")

        # Intentional vulnerability for DevSecOps demos:
        # Raw string formatting makes this login form vulnerable to SQL injection.
        # Example demo payload: username "admin' --" with any password.
        # Secure version notes: use parameterized queries or an ORM, hash stored
        # passwords, rate-limit attempts, and add MFA for admin users.
        query = (
            "SELECT * FROM users "
            f"WHERE username = '{username}' AND password = '{password}'"
        )
        try:
            user = get_db().execute(query).fetchone()
        except sqlite3.Error as exc:
            user = None
            flash(f"Database error: {exc}", "danger")

        if user:
            session.clear()
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["role"] = user["role"]
            flash("Signed in successfully.", "success")
            return redirect(url_for("main.dashboard"))

        flash("Invalid username or password.", "danger")

    return render_template("login.html")


@main.route("/logout")
def logout():
    session.clear()
    flash("Signed out.", "info")
    return redirect(url_for("main.home"))


@main.route("/dashboard")
@login_required
def dashboard():
    db = get_db()
    metrics = {
        "open_jobs": db.execute("SELECT COUNT(*) AS total FROM jobs").fetchone()["total"],
        "candidates": db.execute("SELECT COUNT(*) AS total FROM candidates").fetchone()[
            "total"
        ],
        "feedback_items": db.execute(
            "SELECT COUNT(*) AS total FROM feedback"
        ).fetchone()["total"],
    }
    jobs = db.execute(
        "SELECT id, title, department, location, salary_range FROM jobs ORDER BY id"
    ).fetchall()
    return render_template("dashboard.html", metrics=metrics, jobs=jobs)


@main.route("/jobs", methods=("GET", "POST"))
def jobs():
    if request.method == "POST":
        # Intentional vulnerability for DevSecOps demos:
        # This form has no CSRF token.
        # Secure version notes: use Flask-WTF or another CSRF middleware and
        # reject state-changing requests without a valid token.
        job_id = request.form.get("job_id", "")
        applicant = request.form.get("applicant", "")
        flash(f"Application for job #{job_id} received from {applicant}.", "success")
        return redirect(url_for("main.jobs"))

    job_rows = get_db().execute(
        "SELECT id, title, department, location, description, salary_range FROM jobs ORDER BY id"
    ).fetchall()
    return render_template("jobs.html", jobs=job_rows)


@main.route("/profile", methods=("GET", "POST"))
@login_required
def profile():
    db = get_db()
    candidate = db.execute(
        "SELECT * FROM candidates WHERE user_id = ?", (session["user_id"],)
    ).fetchone()

    if candidate is None:
        candidate = db.execute("SELECT * FROM candidates ORDER BY id LIMIT 1").fetchone()

    if request.method == "POST" and candidate:
        full_name = request.form.get("full_name", "")
        email = request.form.get("email", "")
        phone = request.form.get("phone", "")
        summary = request.form.get("summary", "")
        new_password = request.form.get("new_password", "")

        db.execute(
            """
            UPDATE candidates
            SET full_name = ?, email = ?, phone = ?, summary = ?
            WHERE id = ?
            """,
            (full_name, email, phone, summary, candidate["id"]),
        )

        # Intentional vulnerability for DevSecOps demos:
        # Weak password validation accepts tiny passwords and stores them as
        # plaintext because this training app is intentionally unsafe.
        # Secure version notes: enforce length and complexity, block breached
        # passwords, hash with Argon2/bcrypt, and require current password checks.
        if new_password:
            if len(new_password) >= 3:
                db.execute(
                    "UPDATE users SET password = ? WHERE id = ?",
                    (new_password, candidate["user_id"]),
                )
                flash("Profile and password updated.", "warning")
            else:
                flash("Password must be at least 3 characters.", "danger")
        else:
            flash("Profile updated.", "success")

        db.commit()
        return redirect(url_for("main.profile"))

    return render_template("profile.html", candidate=candidate)


@main.route("/admin", methods=("GET", "POST"))
@admin_required
def admin():
    db = get_db()
    if request.method == "POST":
        # Intentional vulnerability for DevSecOps demos:
        # Admin state-changing form has no CSRF protection.
        # Secure version notes: enforce CSRF tokens and role-based authorization
        # checks on every state-changing endpoint.
        title = request.form.get("title", "")
        department = request.form.get("department", "")
        location = request.form.get("location", "")
        description = request.form.get("description", "")
        salary_range = request.form.get("salary_range", "")
        db.execute(
            """
            INSERT INTO jobs (title, department, location, description, salary_range)
            VALUES (?, ?, ?, ?, ?)
            """,
            (title, department, location, description, salary_range),
        )
        db.commit()
        flash("Job post created.", "success")
        return redirect(url_for("main.admin"))

    users = db.execute(
        "SELECT id, username, role, created_at FROM users ORDER BY id"
    ).fetchall()
    candidates = db.execute(
        "SELECT id, full_name, email, phone, summary FROM candidates ORDER BY id"
    ).fetchall()
    jobs = db.execute(
        "SELECT id, title, department, location, salary_range FROM jobs ORDER BY id"
    ).fetchall()
    feedback_items = db.execute(
        "SELECT id, name, email, message, created_at FROM feedback ORDER BY id DESC"
    ).fetchall()
    return render_template(
        "admin.html",
        users=users,
        candidates=candidates,
        jobs=jobs,
        feedback_items=feedback_items,
    )


@main.route("/feedback", methods=("GET", "POST"))
def feedback():
    db = get_db()
    if request.method == "POST":
        name = request.form.get("name", "")
        email = request.form.get("email", "")
        message = request.form.get("message", "")

        # Intentional vulnerability for DevSecOps demos:
        # Feedback is stored without sanitization, and the template renders it
        # with the safe filter, causing stored XSS.
        # Secure version notes: validate and encode output, sanitize rich text if
        # needed, and use a strict content security policy.
        db.execute(
            "INSERT INTO feedback (name, email, message) VALUES (?, ?, ?)",
            (name, email, message),
        )
        db.commit()
        flash("Feedback submitted.", "success")
        return redirect(url_for("main.feedback"))

    feedback_items = db.execute(
        "SELECT id, name, email, message, created_at FROM feedback ORDER BY id DESC"
    ).fetchall()
    return render_template("feedback.html", feedback_items=feedback_items)


@main.route("/search")
def search():
    query = request.args.get("q", "")
    results = []
    error = None

    if query:
        # Intentional vulnerability for DevSecOps demos:
        # Raw SQL string formatting makes search vulnerable to SQL injection.
        # The template also reflects query with the safe filter, causing
        # reflected XSS.
        # Secure version notes: use parameterized queries, escape output by
        # default, remove the safe filter, and add input validation.
        sql = (
            "SELECT id, title, department, location, description, salary_range "
            "FROM jobs "
            f"WHERE title LIKE '%{query}%' "
            f"OR department LIKE '%{query}%' "
            f"OR location LIKE '%{query}%' "
            f"OR description LIKE '%{query}%'"
        )
        try:
            results = get_db().execute(sql).fetchall()
        except sqlite3.Error as exc:
            error = str(exc)

    return render_template(
        "search.html",
        query=query,
        results=results,
        error=error,
    )
