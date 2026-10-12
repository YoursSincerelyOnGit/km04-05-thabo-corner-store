"""security.py — Task 6: SHA-256 password gate (KM-04 KT08)."""

import hashlib
import getpass


# Set this to hash_password("yourchosenpassword") — see below.
STORED_PASSWORD_HASH = "1c8bfe8f801d79745c4631d09fff36c82aa37fc4cce4fc946683d7b336b63032"


def hash_password(plain_text_password: str) -> str:
    return hashlib.sha256(plain_text_password.encode()).hexdigest()


def check_password(attempt: str, stored_hash: str) -> bool:
    return hash_password(attempt) == stored_hash


def login_gate(stored_hash: str, max_attempts: int = 3) -> bool:
    for _ in range(max_attempts):
        attempt = getpass.getpass("Enter password to view reports: ")
        if check_password(attempt, stored_hash):
            print("Access granted.")
            return True
        print("Incorrect password. Try again.")
    print("Access denied — too many failed attempts.")
    return False