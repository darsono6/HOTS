import hashlib
import hmac
import os

_PREFIX = "pbkdf2_sha256"
_ITERATIONS = 600_000
_MAX_ITERATIONS = 10_000_000


def hash_password(password: str) -> str:
    salt = os.urandom(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, _ITERATIONS)
    return f"{_PREFIX}${_ITERATIONS}${salt.hex()}${dk.hex()}"


def verify_password(password: str, stored_hash: str) -> bool:
    try:
        if not stored_hash:
            return False
        pw = password.encode("utf-8")
        if stored_hash.startswith(_PREFIX + "$"):
            _, iters, salt_hex, expected = stored_hash.split("$")
            iters = int(iters)
            if not 1 <= iters <= _MAX_ITERATIONS:
                return False
            dk = hashlib.pbkdf2_hmac("sha256", pw, bytes.fromhex(salt_hex), iters)
            return hmac.compare_digest(dk.hex(), expected)
        # old format (plain SHA-256): still accepted until the password is changed
        return hmac.compare_digest(hashlib.sha256(pw).hexdigest(), stored_hash)
    except Exception:
        return False
