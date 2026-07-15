import bcrypt


def hash_password(password):
    # gensalt() generates a unique random salt per password, so two users with
    # the same password will have completely different hashes in the database.
    password_bytes = password.encode()
    random_salt    = bcrypt.gensalt()
    return bcrypt.hashpw(password_bytes, random_salt)


def verify_password(password, stored_password_hash):
    # checkpw is timing-safe — it won't leak information through response time
    return bcrypt.checkpw(password.encode(), stored_password_hash)
