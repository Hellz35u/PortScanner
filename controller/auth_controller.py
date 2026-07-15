from models.user_model import create_user, get_user_by_username
from services.auth_service import hash_password, verify_password


def register_user(username, password):
    # Reject duplicates before attempting an INSERT to avoid a DB-level exception
    if get_user_by_username(username) is not None:
        return {
            "success": False,
            "message": "Username already exists."
        }

    hashed_password = hash_password(password)
    create_user(username, hashed_password)

    return {
        "success": True,
        "message": "Registration completed successfully."
    }


def login_user(username, password):
    user = get_user_by_username(username)

    # Return the same generic message for both "not found" and "wrong password"
    # so attackers cannot enumerate valid usernames
    if user is None:
        return {
            "success": False,
            "message": "Username or password are incorrect."
        }

    user_id            = user[0]
    stored_username    = user[1]
    stored_password_hash = user[2]

    if not verify_password(password, stored_password_hash):
        return {
            "success": False,
            "message": "Username or password are incorrect."
        }

    return {
        "success": True,
        "user": {
            "id": user_id,
            "username": stored_username
        }
    }
