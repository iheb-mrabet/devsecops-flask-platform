import sqlite3

from flask import current_app, g


SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'candidate',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    department TEXT NOT NULL,
    location TEXT NOT NULL,
    description TEXT NOT NULL,
    salary_range TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS candidates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    full_name TEXT NOT NULL,
    email TEXT NOT NULL,
    phone TEXT NOT NULL,
    summary TEXT NOT NULL,
    resume_url TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users (id)
);

CREATE TABLE IF NOT EXISTS feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    message TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(error=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = get_db()
    db.executescript(SCHEMA)
    seed_data(db)


def seed_data(db):
    user_count = db.execute("SELECT COUNT(*) AS total FROM users").fetchone()["total"]
    if user_count:
        return

    # Intentional vulnerability for DevSecOps demos:
    # Passwords are stored in plaintext and the default password is weak.
    # Secure version notes: store Argon2/bcrypt hashes, require strong password
    # policy, rotate defaults, and force first-login reset.
    db.executemany(
        "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
        [
            ("admin", "admin123", "admin"),
            ("jane.candidate", "welcome", "candidate"),
            ("alex.recruiter", "recruiter1", "recruiter"),
        ],
    )

    db.executemany(
        """
        INSERT INTO jobs (title, department, location, description, salary_range)
        VALUES (?, ?, ?, ?, ?)
        """,
        [
            (
                "Security Analyst",
                "Security Operations",
                "Remote",
                "Monitor alerts, triage findings, and partner with engineering on remediation.",
                "$78k - $105k",
            ),
            (
                "Platform Engineer",
                "Infrastructure",
                "Austin, TX",
                "Build CI/CD workflows, container images, and deployment automation.",
                "$110k - $145k",
            ),
            (
                "Application Security Intern",
                "Product Security",
                "New York, NY",
                "Assist with threat modeling, SAST triage, and secure coding education.",
                "$28/hr - $38/hr",
            ),
            (
                "Recruiting Coordinator",
                "People Operations",
                "Chicago, IL",
                "Coordinate interview loops and help candidates move smoothly through hiring.",
                "$55k - $72k",
            ),
        ],
    )

    db.executemany(
        """
        INSERT INTO candidates (user_id, full_name, email, phone, summary, resume_url)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        [
            (
                1,
                "Admin Demo",
                "admin@example.test",
                "555-0100",
                "Platform owner for demo administration and security review workflows.",
                "https://example.test/resumes/admin-demo.pdf",
            ),
            (
                2,
                "Jane Candidate",
                "jane@example.test",
                "555-0199",
                "Entry-level analyst with lab experience in Linux, SIEMs, and Python.",
                "https://example.test/resumes/jane-candidate.pdf",
            ),
            (
                3,
                "Alex Recruiter",
                "alex@example.test",
                "555-0144",
                "Recruiter focused on cloud, security, and platform engineering roles.",
                "https://example.test/resumes/alex-recruiter.pdf",
            ),
        ],
    )

    db.executemany(
        "INSERT INTO feedback (name, email, message) VALUES (?, ?, ?)",
        [
            (
                "Morgan Reviewer",
                "morgan@example.test",
                "Great candidate dashboard. Please add more filters later.",
            ),
            (
                "Sam Hiring Manager",
                "sam@example.test",
                "The search page makes it easy to demo application security testing.",
            ),
        ],
    )

    db.commit()
