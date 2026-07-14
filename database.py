import sqlite3
import bcrypt

def initialize_database():
    conn = sqlite3.connect("port_scanner.db")
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()

    cursor.execute(
        """CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password_hash BLOB NOT NULL)"""
        )

    cursor.execute(
        """CREATE TABLE IF NOT EXISTS reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        target_ip TEXT NOT NULL,
        open_ports TEXT NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id)
        )"""
    )

    conn.commit()
    conn.close()

def create_user(username, password_hash):
    conn = sqlite3.connect("port_scanner.db")
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO users (username, password_hash) VALUES (?, ?)",
        (username, password_hash)
    )

    conn.commit()
    conn.close()

def get_user_by_username(username):
    conn = sqlite3.connect("port_scanner.db")
    cursor = conn.cursor()

    cursor.execute(
        """SELECT id, username, password_hash 
        FROM users 
        WHERE username = ?""", 
        (username,)
    )
    user = cursor.fetchone()
    conn.close()
    
    return user

def password_hashing(password):
    password_bytes = password.encode()
    random_salt = bcrypt.gensalt()

    hashed_password = bcrypt.hashpw(password_bytes, random_salt)

    return hashed_password

def register(username, password):
    if get_user_by_username(username) is not None:
        return False
    
    hashed_password = password_hashing(password)
    create_user(username, hashed_password)

    return True

def login(username, password):
    user = get_user_by_username(username)
    
    if user is not None:
        user_id = user[0]
        stored_username = user[1]
        stored_hashed_password = user[2]
        password_bytes = password.encode()
        if bcrypt.checkpw(password_bytes,stored_hashed_password):
            current_user = {
                "id": user_id,
                "username": stored_username
            }
            print(f"{stored_username} successfully logged in.")
            return current_user
    
    print("Username or password are incorrect.")
    return None



