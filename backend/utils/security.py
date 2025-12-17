import hashlib

def hash_password(password: str) -> str:
    if password is None:
        return ""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def verify_password(password: str, hashed: str) -> bool:
    return hash_password(password) == hashed