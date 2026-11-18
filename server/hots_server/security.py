"""Passwords, tokens and a small in-memory rate limiter."""

import hashlib
import hmac
import os
import secrets
import time
from collections import defaultdict, deque

from . import settings

_PREFIX = "pbkdf2_sha256"
CODE_ALPHABET = "ABCDEFGHJKMNPQRSTUVWXYZ23456789"  # no 0/O, 1/I/L


def hash_password(password: str, iterations: int = None) -> str:
    iterations = iterations or settings.PBKDF2_ITERATIONS
    salt = os.urandom(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    return f"{_PREFIX}${iterations}${salt.hex()}${dk.hex()}"


def verify_password(password: str, stored: str) -> bool:
    try:
        prefix, iters, salt_hex, expected = stored.split("$")
        if prefix != _PREFIX:
            return False
        iters = int(iters)
        if not 1 <= iters <= 10_000_000:
            return False
        dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), bytes.fromhex(salt_hex), iters)
        return hmac.compare_digest(dk.hex(), expected)
    except Exception:
        return False


# Constant-time dummy check when the account does not exist (no user enumeration by timing).
_DUMMY_HASH = None


def dummy_verify(password: str) -> None:
    global _DUMMY_HASH
    if _DUMMY_HASH is None:
        _DUMMY_HASH = hash_password("dummy-password")
    verify_password(password, _DUMMY_HASH)


def new_token(nbytes: int = 32) -> str:
    return secrets.token_urlsafe(nbytes)


def token_hash(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def new_device_id() -> str:
    return "pc_" + secrets.token_hex(8)


def new_enroll_code() -> str:
    return "".join(secrets.choice(CODE_ALPHABET) for _ in range(8))


def normalize_code(code: str) -> str:
    return "".join(ch for ch in (code or "").upper() if ch.isalnum())


def format_code(code: str) -> str:
    return f"{code[:4]}-{code[4:]}" if len(code) == 8 else code


def password_problem(password) -> str:
    if not isinstance(password, str) or len(password) < 10:
        return "Le mot de passe doit contenir au moins 10 caractères."
    if len(password) > 200:
        return "Le mot de passe est trop long."
    return ""


class RateLimiter:
    """Sliding-window counter: allow at most `limit` hits per `window` seconds for each key."""

    def __init__(self):
        self._hits = defaultdict(deque)

    def hit(self, key: str, limit: int, window: float) -> bool:
        now = time.monotonic()
        q = self._hits[key]
        while q and now - q[0] > window:
            q.popleft()
        if len(q) >= limit:
            return False
        q.append(now)
        if len(self._hits) > 50_000:  # keep memory bounded
            for k in list(self._hits)[:10_000]:
                self._hits.pop(k, None)
        return True

    def reset(self, key: str) -> None:
        self._hits.pop(key, None)


limiter = RateLimiter()
