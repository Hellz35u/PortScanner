import sqlite3
from pathlib import Path

# Derive the DB path from this file's location so it works regardless of the
# current working directory when the app is launched.
PROJECT_ROOT  = Path(__file__).resolve().parent.parent
DATABASE_PATH = PROJECT_ROOT / "data" / "port_scanner.db"


def get_connection():
    # Create the data/ directory if it doesn't exist yet
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(DATABASE_PATH)
    # Enforce referential integrity (user_id in reports must exist in users)
    conn.execute("PRAGMA foreign_keys = ON")

    return conn


def initialize_database():
    # CREATE TABLE IF NOT EXISTS means this is safe to call on every startup
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            username      TEXT    NOT NULL UNIQUE,
            password_hash BLOB    NOT NULL
        )
        """
    )

    # open_ports is stored as a JSON string (list of {port, service} objects)
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS reports (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id    INTEGER NOT NULL,
            target_ip  TEXT    NOT NULL,
            open_ports TEXT    NOT NULL,
            created_at TEXT    NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        """
    )

    conn.commit()
    conn.close()
