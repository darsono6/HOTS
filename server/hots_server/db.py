"""SQLite storage. All access happens on the event loop thread (short queries), WAL mode."""

import contextlib
import json
import os
import sqlite3
import time

from . import settings

SCHEMA = """
CREATE TABLE IF NOT EXISTS meta (
    key TEXT PRIMARY KEY,
    value TEXT
);
CREATE TABLE IF NOT EXISTS accounts (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    created_at REAL NOT NULL,
    suspended INTEGER NOT NULL DEFAULT 0,
    max_devices INTEGER,
    notes TEXT NOT NULL DEFAULT ''
);
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    account_id INTEGER NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
    email TEXT NOT NULL UNIQUE COLLATE NOCASE,
    name TEXT NOT NULL DEFAULT '',
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'owner',
    is_superadmin INTEGER NOT NULL DEFAULT 0,
    disabled INTEGER NOT NULL DEFAULT 0,
    created_at REAL NOT NULL,
    last_login REAL
);
CREATE TABLE IF NOT EXISTS sessions (
    token_hash TEXT PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at REAL NOT NULL,
    expires_at REAL NOT NULL,
    ip TEXT,
    user_agent TEXT
);
CREATE TABLE IF NOT EXISTS enroll_codes (
    id INTEGER PRIMARY KEY,
    account_id INTEGER NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
    code TEXT NOT NULL UNIQUE,
    label TEXT NOT NULL DEFAULT '',
    created_by INTEGER,
    created_at REAL NOT NULL,
    expires_at REAL NOT NULL,
    max_uses INTEGER,
    uses INTEGER NOT NULL DEFAULT 0,
    revoked INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS devices (
    id TEXT PRIMARY KEY,
    account_id INTEGER NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
    token_hash TEXT NOT NULL,
    name TEXT NOT NULL,
    hostname TEXT NOT NULL DEFAULT '',
    os TEXT NOT NULL DEFAULT '',
    machine_id TEXT NOT NULL DEFAULT '',
    agent_version TEXT NOT NULL DEFAULT '',
    app_version TEXT NOT NULL DEFAULT '',
    enrolled_at REAL NOT NULL,
    last_seen REAL,
    last_ip TEXT,
    state_json TEXT,
    state_at REAL,
    uninstalled_at REAL,
    notes TEXT NOT NULL DEFAULT ''
);
CREATE INDEX IF NOT EXISTS idx_devices_account ON devices(account_id);
CREATE TABLE IF NOT EXISTS commands (
    id INTEGER PRIMARY KEY,
    device_id TEXT NOT NULL REFERENCES devices(id) ON DELETE CASCADE,
    account_id INTEGER NOT NULL,
    user_id INTEGER,
    action TEXT NOT NULL,
    params_json TEXT NOT NULL DEFAULT '{}',
    summary TEXT NOT NULL DEFAULT '',
    status TEXT NOT NULL,
    result_json TEXT,
    error TEXT,
    created_at REAL NOT NULL,
    sent_at REAL,
    done_at REAL,
    duration_ms INTEGER
);
CREATE INDEX IF NOT EXISTS idx_commands_device ON commands(device_id, status);
CREATE INDEX IF NOT EXISTS idx_commands_created ON commands(created_at);
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY,
    account_id INTEGER,
    user_id INTEGER,
    device_id TEXT,
    kind TEXT NOT NULL,
    message TEXT NOT NULL DEFAULT '',
    ip TEXT,
    created_at REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_events_account ON events(account_id, created_at);
"""


def connect() -> sqlite3.Connection:
    os.makedirs(os.path.dirname(settings.DB_PATH), exist_ok=True)
    conn = sqlite3.connect(settings.DB_PATH, timeout=10, isolation_level=None, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA busy_timeout = 10000")
    return conn


_conn = None


def get() -> sqlite3.Connection:
    """Shared connection (used from the event loop thread only)."""
    global _conn
    if _conn is None:
        _conn = connect()
    return _conn


def close() -> None:
    global _conn
    if _conn is not None:
        _conn.close()
        _conn = None


def init() -> None:
    conn = get()
    conn.execute("PRAGMA journal_mode = WAL")
    conn.executescript(SCHEMA)
    if get_meta("schema_version") is None:
        set_meta("schema_version", "1")
    if get_meta("server_name") is None:
        set_meta("server_name", "Console HOTS Hosts")
    if get_meta("registration_open") is None:
        set_meta("registration_open", "0")


@contextlib.contextmanager
def transaction():
    conn = get()
    conn.execute("BEGIN IMMEDIATE")
    try:
        yield conn
        conn.execute("COMMIT")
    except BaseException:
        conn.execute("ROLLBACK")
        raise


def q(sql: str, args=()) -> list:
    return get().execute(sql, args).fetchall()


def q1(sql: str, args=()):
    return get().execute(sql, args).fetchone()


def ex(sql: str, args=()) -> sqlite3.Cursor:
    return get().execute(sql, args)


def get_meta(key: str, default=None):
    row = q1("SELECT value FROM meta WHERE key = ?", (key,))
    return row["value"] if row else default


def set_meta(key: str, value) -> None:
    ex("INSERT INTO meta(key, value) VALUES(?, ?) ON CONFLICT(key) DO UPDATE SET value = excluded.value",
       (key, None if value is None else str(value)))


def del_meta(key: str) -> None:
    ex("DELETE FROM meta WHERE key = ?", (key,))


def log_event(kind: str, message: str = "", account_id=None, user_id=None, device_id=None, ip=None) -> None:
    ex("INSERT INTO events(account_id, user_id, device_id, kind, message, ip, created_at) VALUES(?,?,?,?,?,?,?)",
       (account_id, user_id, device_id, kind, message[:500], ip, time.time()))


def loads(text, default=None):
    if not text:
        return default
    try:
        return json.loads(text)
    except ValueError:
        return default


def dumps(value) -> str:
    return json.dumps(value, separators=(",", ":"), ensure_ascii=False)
