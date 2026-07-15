from models.database import get_connection


def create_user(username, password_hash):
    # password_hash is a bytes object produced by bcrypt — stored as BLOB
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users (username, password_hash) VALUES (?, ?)",
        (username, password_hash),
    )
    conn.commit()
    conn.close()


def get_user_by_username(username):
    # Returns (id, username, password_hash) or None if not found
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, username, password_hash FROM users WHERE username = ?",
        (username,),
    )
    user = cursor.fetchone()
    conn.close()
    return user
