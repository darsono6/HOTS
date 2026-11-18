"""HTTP application: agent API (long-polling), console API (cookie session) and static console."""

import asyncio
import contextlib
import hmac
import logging
import os
import re
import time

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import FileResponse, JSONResponse, Response
from starlette.routing import Mount, Route
from starlette.staticfiles import StaticFiles

from . import __version__, db, security, settings

log = logging.getLogger("hots_server")

STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
SESSION_COOKIE = "hots_session"
CSRF_HEADER = "x-hots-csrf"

# Mirror of hosts_editor/remote/actions.py (name -> changes something on the PC).
# A test checks both lists stay identical.
ACTIONS = {
    "agent.ping": False,
    "get_state": False,
    "hosts.read": False,
    "hosts.backups": False,
    "apps.list_installed": False,
    "privacy.check_drift": False,
    "parental.set": True,
    "custom_domains.set": True,
    "cf_family.set": True,
    "hosts_lock.set": True,
    "netblock.set": True,
    "doh.set": True,
    "vpn.set": True,
    "rstrui_lock.set": True,
    "apps.add": True,
    "apps.set_enabled": True,
    "apps.remove": True,
    "privacy.set_item": True,
    "privacy.set_level": True,
    "system.restore_point": True,
    "hosts.add_entry": True,
    "hosts.update_entry": True,
    "hosts.delete_entry": True,
    "hosts.save_text": True,
    "hosts.restore_backup": True,
    "dns.flush": True,
}
# Large read-only results are dropped from the history after a day.
BULKY_RESULTS = ("get_state", "hosts.read", "apps.list_installed", "hosts.backups")
TERMINAL = ("done", "error", "expired", "cancelled")

SENT_TIMEOUT = 15 * 60
PENDING_TIMEOUT = 7 * 24 * 3600
HISTORY_DAYS = 90

MAX_AGENT_BODY = 12 * 1024 * 1024
MAX_COMMAND_BODY = 7 * 1024 * 1024
MAX_DEFAULT_BODY = 256 * 1024

EMAIL_RE = re.compile(r"^[^@\s]{1,64}@[^@\s]{1,190}\.[^@\s]{2,}$")


class ApiError(Exception):
    def __init__(self, status: int, detail: str):
        super().__init__(detail)
        self.status = status
        self.detail = detail


# --- wake-up hub for long polling --------------------------------------------------------------

class Hub:
    def __init__(self):
        self.devices: dict = {}
        self.commands: dict = {}

    def _event(self, table: dict, key) -> asyncio.Event:
        ev = table.get(key)
        if ev is None:
            ev = table[key] = asyncio.Event()
        return ev

    def device(self, device_id: str) -> asyncio.Event:
        return self._event(self.devices, device_id)

    def command(self, command_id: int) -> asyncio.Event:
        return self._event(self.commands, command_id)

    def wake_device(self, device_id: str) -> None:
        ev = self.devices.get(device_id)
        if ev:
            ev.set()

    def wake_command(self, command_id: int) -> None:
        ev = self.commands.pop(command_id, None)
        if ev:
            ev.set()


hub = Hub()


async def wait_event(ev: asyncio.Event, timeout: float) -> bool:
    try:
        await asyncio.wait_for(ev.wait(), timeout=max(0.0, timeout))
        return True
    except asyncio.TimeoutError:
        return False


# --- helpers ----------------------------------------------------------------------------------------

def err(status: int, detail: str) -> JSONResponse:
    return JSONResponse({"detail": detail}, status_code=status)


def client_ip(request: Request) -> str:
    return request.client.host if request.client else ""


async def read_json(request: Request) -> dict:
    try:
        data = await request.json()
    except Exception:
        raise ApiError(400, "Requête JSON invalide.")
    if not isinstance(data, dict):
        raise ApiError(400, "Requête JSON invalide.")
    return data


def s(data: dict, key: str, maxlen: int = 200, required: bool = True, default: str = "") -> str:
    value = data.get(key)
    if value is None or (isinstance(value, str) and not value.strip()):
        if required:
            raise ApiError(400, f"Champ « {key} » obligatoire.")
        return default
    if not isinstance(value, str) or len(value) > maxlen:
        raise ApiError(400, f"Champ « {key} » invalide.")
    return value.strip()


def is_online(row) -> bool:
    return bool(row["last_seen"] and not row["uninstalled_at"]
                and time.time() - row["last_seen"] < settings.ONLINE_GRACE_SECONDS)


def summarize_state(state) -> dict:
    if not isinstance(state, dict):
        return None
    parental = state.get("parental") or {}
    cats = parental.get("categories") or []
    prot = state.get("protections") or {}
    privacy_items = [it for lvl in (state.get("privacy") or {}).get("levels") or []
                     for it in lvl.get("items") or [] if not it.get("user_scope")]
    return {
        "categories_active": sum(1 for c in cats if c.get("active")),
        "categories_total": len(cats),
        "custom": bool((parental.get("custom") or {}).get("active")),
        "cf_family": bool((state.get("cf_family") or {}).get("active")),
        "hosts_lock": bool(prot.get("hosts_lock")),
        "netblock": bool(prot.get("netblock")),
        "vpn": bool(prot.get("vpn")),
        "rstrui": bool(prot.get("rstrui")),
        "doh_blocked": sum(1 for b in prot.get("doh") or [] if b.get("blocked")),
        "apps_blocked": sum(1 for a in state.get("apps") or [] if a.get("enabled")),
        "privacy_active": sum(1 for it in privacy_items if it.get("active")),
        "privacy_total": len(privacy_items),
        "errors": len(state.get("errors") or {}),
    }


def device_public(row, with_state: bool = False) -> dict:
    state = db.loads(row["state_json"])
    pending = db.q1("SELECT COUNT(*) AS n FROM commands WHERE device_id = ? AND status IN ('pending','sent')",
                    (row["id"],))["n"]
    out = {
        "id": row["id"], "name": row["name"], "hostname": row["hostname"], "os": row["os"],
        "agent_version": row["agent_version"], "app_version": row["app_version"],
        "enrolled_at": row["enrolled_at"], "last_seen": row["last_seen"], "last_ip": row["last_ip"],
        "online": is_online(row), "uninstalled_at": row["uninstalled_at"], "notes": row["notes"],
        "state_at": row["state_at"], "summary": summarize_state(state), "pending_commands": pending,
    }
    if with_state:
        out["state"] = state
    return out


def command_public(row, with_result: bool = True) -> dict:
    out = {
        "id": row["id"], "device_id": row["device_id"], "action": row["action"], "summary": row["summary"],
        "status": row["status"], "error": row["error"], "created_at": row["created_at"],
        "sent_at": row["sent_at"], "done_at": row["done_at"], "duration_ms": row["duration_ms"],
        "user_id": row["user_id"],
    }
    if with_result:
        out["result"] = db.loads(row["result_json"])
    return out


def user_public(row) -> dict:
    return {"id": row["id"], "email": row["email"], "name": row["name"], "role": row["role"],
            "is_superadmin": bool(row["is_superadmin"]), "disabled": bool(row["disabled"]),
            "created_at": row["created_at"], "last_login": row["last_login"]}


DEFAULT_DOWNLOAD_URL = "https://github.com/jrsmrtn/HOTS-Web-Administrated/releases/latest"


def settings_public() -> dict:
    return {"server_name": db.get_meta("server_name", "Console HOTS Hosts"),
            "registration_open": db.get_meta("registration_open", "0") == "1",
            "download_url": db.get_meta("download_url") or DEFAULT_DOWNLOAD_URL,
            "version": __version__}


# --- sessions ----------------------------------------------------------------------------------------

def _cookie_secure(request: Request) -> bool:
    if settings.COOKIE_SECURE in ("1", "true", "yes"):
        return True
    if settings.COOKIE_SECURE in ("0", "false", "no"):
        return False
    return request.url.scheme == "https"


def start_session(request: Request, response: Response, user_id: int) -> None:
    token = security.new_token()
    now = time.time()
    db.ex("INSERT INTO sessions(token_hash, user_id, created_at, expires_at, ip, user_agent) VALUES(?,?,?,?,?,?)",
          (security.token_hash(token), user_id, now, now + settings.SESSION_DAYS * 86400,
           client_ip(request), (request.headers.get("user-agent") or "")[:200]))
    db.ex("UPDATE users SET last_login = ? WHERE id = ?", (now, user_id))
    response.set_cookie(SESSION_COOKIE, token, max_age=settings.SESSION_DAYS * 86400, httponly=True,
                        secure=_cookie_secure(request), samesite="strict", path="/")


def current_user(request: Request, required: bool = True):
    token = request.cookies.get(SESSION_COOKIE)
    row = None
    if token:
        row = db.q1(
            "SELECT u.*, a.name AS account_name, a.suspended AS account_suspended, a.max_devices, s.expires_at "
            "FROM sessions s JOIN users u ON u.id = s.user_id JOIN accounts a ON a.id = u.account_id "
            "WHERE s.token_hash = ?", (security.token_hash(token),))
        if row and row["expires_at"] < time.time():
            db.ex("DELETE FROM sessions WHERE token_hash = ?", (security.token_hash(token),))
            row = None
        if row and (row["disabled"] or (row["account_suspended"] and not row["is_superadmin"])):
            row = None
    if row is None and required:
        raise ApiError(401, "Session expirée : reconnectez-vous.")
    return row


def require_superadmin(request: Request):
    user = current_user(request)
    if not user["is_superadmin"]:
        raise ApiError(403, "Réservé à l'administrateur du serveur.")
    return user


def require_owner(user) -> None:
    if user["role"] != "owner" and not user["is_superadmin"]:
        raise ApiError(403, "Réservé au responsable du compte.")


def own_device(user, device_id: str):
    row = db.q1("SELECT * FROM devices WHERE id = ? AND account_id = ?", (device_id, user["account_id"]))
    if row is None:
        raise ApiError(404, "PC introuvable.")
    return row


# --- public / setup / auth -------------------------------------------------------------------------

async def bootstrap(request: Request):
    user = current_user(request, required=False)
    has_users = db.q1("SELECT 1 FROM users LIMIT 1") is not None
    out = dict(settings_public())
    out["setup_required"] = not has_users
    out["user"] = None
    if user:
        out["user"] = dict(user_public(user), account_id=user["account_id"], account_name=user["account_name"])
    return JSONResponse(out)


def ensure_setup_token() -> str:
    """Token required to create the first admin (printed by deploy.sh). None once set up."""
    if db.q1("SELECT 1 FROM users LIMIT 1"):
        return None
    token = db.get_meta("setup_token")
    if not token:
        token = security.new_token(18)
        db.set_meta("setup_token", token)
    try:
        path = os.path.join(settings.DATA_DIR, "setup-token.txt")
        with open(path, "w", encoding="utf-8") as f:
            f.write(token + "\n")
        os.chmod(path, 0o600)
    except OSError:
        pass
    return token


def _clear_setup_token() -> None:
    db.del_meta("setup_token")
    with contextlib.suppress(OSError):
        os.remove(os.path.join(settings.DATA_DIR, "setup-token.txt"))


def _create_account_with_owner(account_name: str, name: str, email: str, password_hash: str,
                               is_superadmin: bool = False, max_devices=None) -> tuple:
    if db.q1("SELECT 1 FROM users WHERE email = ?", (email,)):
        raise ApiError(409, "Cette adresse e-mail est déjà utilisée.")
    now = time.time()
    cur = db.ex("INSERT INTO accounts(name, created_at, max_devices) VALUES(?,?,?)", (account_name, now, max_devices))
    account_id = cur.lastrowid
    cur = db.ex("INSERT INTO users(account_id, email, name, password_hash, role, is_superadmin, created_at) "
                "VALUES(?,?,?,?,?,?,?)", (account_id, email, name, password_hash, "owner", int(is_superadmin), now))
    return account_id, cur.lastrowid


def _validate_identity(data: dict) -> tuple:
    email = s(data, "email", 254).lower()
    if not EMAIL_RE.match(email):
        raise ApiError(400, "Adresse e-mail invalide.")
    password = data.get("password")
    problem = security.password_problem(password)
    if problem:
        raise ApiError(400, problem)
    name = s(data, "name", 100, required=False)
    return email, password, name


async def setup(request: Request):
    data = await read_json(request)
    if db.q1("SELECT 1 FROM users LIMIT 1"):
        raise ApiError(409, "Le serveur est déjà configuré.")
    if not security.limiter.hit(f"setup:{client_ip(request)}", 10, 600):
        raise ApiError(429, "Trop de tentatives, réessayez plus tard.")
    expected = db.get_meta("setup_token")
    token = data.get("token")
    if not expected or not isinstance(token, str) or not hmac.compare_digest(token, expected):
        raise ApiError(403, "Lien d'installation invalide. Utilisez le lien affiché à la fin de deploy.sh.")
    email, password, name = _validate_identity(data)
    server_name = s(data, "server_name", 80, required=False, default="Console HOTS Hosts")
    account_name = s(data, "account_name", 80, required=False, default=name or "Administration")
    pw_hash = await asyncio.to_thread(security.hash_password, password)
    with db.transaction():
        account_id, user_id = _create_account_with_owner(account_name, name, email, pw_hash, is_superadmin=True)
        db.set_meta("server_name", server_name)
        db.set_meta("registration_open", "1" if data.get("registration_open") is True else "0")
        _clear_setup_token()
        db.log_event("setup", "Serveur configuré", account_id, user_id, ip=client_ip(request))
    response = JSONResponse({"ok": True})
    start_session(request, response, user_id)
    return response


async def login(request: Request):
    data = await read_json(request)
    email = s(data, "email", 254).lower()
    password = data.get("password") if isinstance(data.get("password"), str) else ""
    ip = client_ip(request)
    if not (security.limiter.hit(f"login-ip:{ip}", 20, 900) and security.limiter.hit(f"login:{email}", 8, 900)):
        raise ApiError(429, "Trop de tentatives de connexion. Patientez 15 minutes.")
    row = db.q1("SELECT u.*, a.suspended AS account_suspended FROM users u JOIN accounts a ON a.id = u.account_id "
                "WHERE u.email = ?", (email,))
    if row is None:
        await asyncio.to_thread(security.dummy_verify, password)
        db.log_event("login_failed", f"Compte inconnu : {email}", ip=ip)
        raise ApiError(401, "E-mail ou mot de passe incorrect.")
    ok = await asyncio.to_thread(security.verify_password, password, row["password_hash"])
    if not ok:
        db.log_event("login_failed", f"Mot de passe incorrect : {email}", row["account_id"], row["id"], ip=ip)
        raise ApiError(401, "E-mail ou mot de passe incorrect.")
    if row["disabled"]:
        raise ApiError(403, "Ce compte utilisateur est désactivé.")
    if row["account_suspended"] and not row["is_superadmin"]:
        raise ApiError(403, "Ce compte client est suspendu. Contactez l'administrateur du serveur.")
    security.limiter.reset(f"login:{email}")
    db.log_event("login", "Connexion", row["account_id"], row["id"], ip=ip)
    response = JSONResponse({"ok": True})
    start_session(request, response, row["id"])
    return response


async def logout(request: Request):
    token = request.cookies.get(SESSION_COOKIE)
    if token:
        db.ex("DELETE FROM sessions WHERE token_hash = ?", (security.token_hash(token),))
    response = JSONResponse({"ok": True})
    response.delete_cookie(SESSION_COOKIE, path="/")
    return response


async def register(request: Request):
    if db.get_meta("registration_open", "0") != "1":
        raise ApiError(403, "Les inscriptions sont fermées sur ce serveur.")
    if not security.limiter.hit(f"register:{client_ip(request)}", 5, 3600):
        raise ApiError(429, "Trop d'inscriptions depuis cette adresse, réessayez plus tard.")
    data = await read_json(request)
    email, password, name = _validate_identity(data)
    account_name = s(data, "account_name", 80, required=False, default=name or email.split("@")[0])
    pw_hash = await asyncio.to_thread(security.hash_password, password)
    with db.transaction():
        account_id, user_id = _create_account_with_owner(account_name, name, email, pw_hash)
        db.log_event("register", "Inscription", account_id, user_id, ip=client_ip(request))
    response = JSONResponse({"ok": True})
    start_session(request, response, user_id)
    return response


async def change_password(request: Request):
    user = current_user(request)
    data = await read_json(request)
    current = data.get("current") if isinstance(data.get("current"), str) else ""
    new = data.get("new")
    problem = security.password_problem(new)
    if problem:
        raise ApiError(400, problem)
    if not await asyncio.to_thread(security.verify_password, current, user["password_hash"]):
        raise ApiError(400, "Mot de passe actuel incorrect.")
    pw_hash = await asyncio.to_thread(security.hash_password, new)
    token_h = security.token_hash(request.cookies.get(SESSION_COOKIE, ""))
    db.ex("UPDATE users SET password_hash = ? WHERE id = ?", (pw_hash, user["id"]))
    db.ex("DELETE FROM sessions WHERE user_id = ? AND token_hash != ?", (user["id"], token_h))
    db.log_event("password", "Mot de passe modifié", user["account_id"], user["id"], ip=client_ip(request))
    return JSONResponse({"ok": True})


async def update_profile(request: Request):
    user = current_user(request)
    data = await read_json(request)
    name = s(data, "name", 100, required=False)
    db.ex("UPDATE users SET name = ? WHERE id = ?", (name, user["id"]))
    if "account_name" in data:
        require_owner(user)
        db.ex("UPDATE accounts SET name = ? WHERE id = ?", (s(data, "account_name", 80), user["account_id"]))
    return JSONResponse({"ok": True})


# --- devices -----------------------------------------------------------------------------------------

async def list_devices(request: Request):
    user = current_user(request)
    rows = db.q("SELECT * FROM devices WHERE account_id = ? ORDER BY name COLLATE NOCASE", (user["account_id"],))
    return JSONResponse({"devices": [device_public(r) for r in rows]})


async def get_device(request: Request):
    user = current_user(request)
    row = own_device(user, request.path_params["device_id"])
    return JSONResponse(device_public(row, with_state=True))


async def patch_device(request: Request):
    user = current_user(request)
    row = own_device(user, request.path_params["device_id"])
    data = await read_json(request)
    name = s(data, "name", 80, required=False, default=row["name"])
    notes = s(data, "notes", 2000, required=False, default=row["notes"]) if "notes" in data else row["notes"]
    db.ex("UPDATE devices SET name = ?, notes = ? WHERE id = ?", (name, notes, row["id"]))
    return JSONResponse({"ok": True})


async def delete_device(request: Request):
    user = current_user(request)
    row = own_device(user, request.path_params["device_id"])
    with db.transaction():
        db.ex("DELETE FROM devices WHERE id = ?", (row["id"],))
        db.log_event("device_removed", f"PC retiré : {row['name']}", user["account_id"], user["id"],
                     ip=client_ip(request))
    hub.wake_device(row["id"])
    return JSONResponse({"ok": True})


async def create_command(request: Request):
    user = current_user(request)
    row = own_device(user, request.path_params["device_id"])
    if row["uninstalled_at"]:
        raise ApiError(409, "HOTS Hosts a été désinstallé de ce PC.")
    data = await read_json(request)
    action = s(data, "action", 64)
    if action not in ACTIONS:
        raise ApiError(400, f"Action inconnue : {action}")
    params = data.get("params") or {}
    if not isinstance(params, dict):
        raise ApiError(400, "Paramètres invalides.")
    summary = s(data, "summary", 200, required=False)
    if not security.limiter.hit(f"cmd:{user['account_id']}", 120, 60):
        raise ApiError(429, "Trop de commandes, ralentissez un peu.")
    cur = db.ex("INSERT INTO commands(device_id, account_id, user_id, action, params_json, summary, status, created_at) "
                "VALUES(?,?,?,?,?,?, 'pending', ?)",
                (row["id"], user["account_id"], user["id"], action, db.dumps(params), summary, time.time()))
    hub.wake_device(row["id"])
    cmd = db.q1("SELECT * FROM commands WHERE id = ?", (cur.lastrowid,))
    return JSONResponse(command_public(cmd), status_code=201)


async def list_commands(request: Request):
    user = current_user(request)
    row = own_device(user, request.path_params["device_id"])
    try:
        limit = max(1, min(200, int(request.query_params.get("limit", "50"))))
    except ValueError:
        limit = 50
    rows = db.q("SELECT c.*, u.name AS user_name, u.email AS user_email FROM commands c "
                "LEFT JOIN users u ON u.id = c.user_id WHERE c.device_id = ? ORDER BY c.id DESC LIMIT ?",
                (row["id"], limit))
    out = []
    for r in rows:
        item = command_public(r, with_result=False)
        item["user"] = r["user_name"] or r["user_email"] or ""
        out.append(item)
    return JSONResponse({"commands": out})


def _own_command(user, command_id: int):
    row = db.q1("SELECT * FROM commands WHERE id = ? AND account_id = ?", (command_id, user["account_id"]))
    if row is None:
        raise ApiError(404, "Commande introuvable.")
    return row


async def get_command(request: Request):
    user = current_user(request)
    command_id = request.path_params["command_id"]
    row = _own_command(user, command_id)
    try:
        wait = max(0.0, min(30.0, float(request.query_params.get("wait", "0"))))
    except ValueError:
        wait = 0.0
    deadline = time.monotonic() + wait
    while row["status"] not in TERMINAL and time.monotonic() < deadline:
        ev = hub.command(command_id)
        await wait_event(ev, min(5.0, deadline - time.monotonic()))
        if await request.is_disconnected():
            break
        row = _own_command(user, command_id)
    return JSONResponse(command_public(row))


async def cancel_command(request: Request):
    user = current_user(request)
    row = _own_command(user, request.path_params["command_id"])
    if row["status"] != "pending":
        raise ApiError(409, "Seules les commandes en attente peuvent être annulées.")
    db.ex("UPDATE commands SET status = 'cancelled', done_at = ? WHERE id = ? AND status = 'pending'",
          (time.time(), row["id"]))
    hub.wake_command(row["id"])
    return JSONResponse({"ok": True})


# --- enrollment codes --------------------------------------------------------------------------------

def code_public(row) -> dict:
    now = time.time()
    exhausted = row["max_uses"] is not None and row["uses"] >= row["max_uses"]
    return {"id": row["id"], "code": security.format_code(row["code"]), "label": row["label"],
            "created_at": row["created_at"], "expires_at": row["expires_at"], "max_uses": row["max_uses"],
            "uses": row["uses"], "revoked": bool(row["revoked"]),
            "valid": not row["revoked"] and not exhausted and row["expires_at"] > now}


async def list_codes(request: Request):
    user = current_user(request)
    rows = db.q("SELECT * FROM enroll_codes WHERE account_id = ? AND (expires_at > ? OR created_at > ?) "
                "ORDER BY id DESC", (user["account_id"], time.time() - 7 * 86400, time.time() - 30 * 86400))
    return JSONResponse({"codes": [code_public(r) for r in rows]})


async def create_code(request: Request):
    user = current_user(request)
    data = await read_json(request)
    label = s(data, "label", 80, required=False)
    days = data.get("days", 7)
    if isinstance(days, bool) or not isinstance(days, (int, float)) or not 0 < days <= 90:
        raise ApiError(400, "Durée de validité invalide (1 à 90 jours).")
    max_uses = data.get("max_uses")
    if max_uses is not None and (isinstance(max_uses, bool) or not isinstance(max_uses, int) or not 1 <= max_uses <= 1000):
        raise ApiError(400, "Nombre d'utilisations invalide.")
    if not security.limiter.hit(f"code:{user['account_id']}", 30, 3600):
        raise ApiError(429, "Trop de codes créés, réessayez plus tard.")
    now = time.time()
    for _ in range(10):
        code = security.new_enroll_code()
        if not db.q1("SELECT 1 FROM enroll_codes WHERE code = ?", (code,)):
            break
    cur = db.ex("INSERT INTO enroll_codes(account_id, code, label, created_by, created_at, expires_at, max_uses) "
                "VALUES(?,?,?,?,?,?,?)", (user["account_id"], code, label, user["id"], now, now + days * 86400, max_uses))
    db.log_event("code_created", f"Code d'ajout créé ({label or security.format_code(code)})",
                 user["account_id"], user["id"], ip=client_ip(request))
    return JSONResponse(code_public(db.q1("SELECT * FROM enroll_codes WHERE id = ?", (cur.lastrowid,))), status_code=201)


async def revoke_code(request: Request):
    user = current_user(request)
    db.ex("UPDATE enroll_codes SET revoked = 1 WHERE id = ? AND account_id = ?",
          (request.path_params["code_id"], user["account_id"]))
    return JSONResponse({"ok": True})


# --- account users & events --------------------------------------------------------------------------

async def list_account_users(request: Request):
    user = current_user(request)
    rows = db.q("SELECT * FROM users WHERE account_id = ? ORDER BY id", (user["account_id"],))
    account = db.q1("SELECT * FROM accounts WHERE id = ?", (user["account_id"],))
    return JSONResponse({"account": {"id": account["id"], "name": account["name"], "max_devices": account["max_devices"]},
                         "users": [user_public(r) for r in rows]})


async def add_account_user(request: Request):
    user = current_user(request)
    require_owner(user)
    data = await read_json(request)
    email, password, name = _validate_identity(data)
    role = data.get("role") if data.get("role") in ("owner", "member") else "member"
    if db.q1("SELECT 1 FROM users WHERE email = ?", (email,)):
        raise ApiError(409, "Cette adresse e-mail est déjà utilisée.")
    pw_hash = await asyncio.to_thread(security.hash_password, password)
    db.ex("INSERT INTO users(account_id, email, name, password_hash, role, created_at) VALUES(?,?,?,?,?,?)",
          (user["account_id"], email, name, pw_hash, role, time.time()))
    db.log_event("user_added", f"Utilisateur ajouté : {email}", user["account_id"], user["id"], ip=client_ip(request))
    return JSONResponse({"ok": True}, status_code=201)


async def delete_account_user(request: Request):
    user = current_user(request)
    require_owner(user)
    uid = request.path_params["user_id"]
    if uid == user["id"]:
        raise ApiError(400, "Vous ne pouvez pas supprimer votre propre accès.")
    target = db.q1("SELECT * FROM users WHERE id = ? AND account_id = ?", (uid, user["account_id"]))
    if target is None:
        raise ApiError(404, "Utilisateur introuvable.")
    if target["is_superadmin"]:
        raise ApiError(400, "L'administrateur du serveur ne peut pas être supprimé ici.")
    db.ex("DELETE FROM users WHERE id = ?", (uid,))
    db.log_event("user_removed", f"Utilisateur retiré : {target['email']}", user["account_id"], user["id"],
                 ip=client_ip(request))
    return JSONResponse({"ok": True})


async def list_events(request: Request):
    user = current_user(request)
    rows = db.q("SELECT e.*, u.email AS user_email, d.name AS device_name FROM events e "
                "LEFT JOIN users u ON u.id = e.user_id LEFT JOIN devices d ON d.id = e.device_id "
                "WHERE e.account_id = ? ORDER BY e.id DESC LIMIT 200", (user["account_id"],))
    return JSONResponse({"events": [
        {"id": r["id"], "kind": r["kind"], "message": r["message"], "ip": r["ip"], "created_at": r["created_at"],
         "user": r["user_email"] or "", "device": r["device_name"] or ""} for r in rows]})


# --- server administration (superadmin) ----------------------------------------------------------------

async def admin_accounts(request: Request):
    require_superadmin(request)
    rows = db.q("SELECT a.*, (SELECT COUNT(*) FROM devices d WHERE d.account_id = a.id) AS devices, "
                "(SELECT COUNT(*) FROM devices d WHERE d.account_id = a.id AND d.last_seen > ? AND d.uninstalled_at IS NULL) AS online, "
                "(SELECT COUNT(*) FROM users u WHERE u.account_id = a.id) AS users "
                "FROM accounts a ORDER BY a.id", (time.time() - settings.ONLINE_GRACE_SECONDS,))
    accounts = []
    for r in rows:
        users = db.q("SELECT * FROM users WHERE account_id = ? ORDER BY id", (r["id"],))
        accounts.append({"id": r["id"], "name": r["name"], "created_at": r["created_at"],
                         "suspended": bool(r["suspended"]), "max_devices": r["max_devices"], "notes": r["notes"],
                         "devices": r["devices"], "online": r["online"],
                         "users": [user_public(u) for u in users]})
    return JSONResponse({"accounts": accounts})


async def admin_create_account(request: Request):
    admin = require_superadmin(request)
    data = await read_json(request)
    email, password, name = _validate_identity(data)
    account_name = s(data, "account_name", 80)
    max_devices = data.get("max_devices")
    if max_devices in ("", None):
        max_devices = None
    elif isinstance(max_devices, bool) or not isinstance(max_devices, int) or max_devices < 1:
        raise ApiError(400, "Nombre maximal de PC invalide.")
    pw_hash = await asyncio.to_thread(security.hash_password, password)
    with db.transaction():
        account_id, _uid = _create_account_with_owner(account_name, name, email, pw_hash, max_devices=max_devices)
        db.log_event("account_created", f"Compte client créé : {account_name}", admin["account_id"], admin["id"],
                     ip=client_ip(request))
    return JSONResponse({"ok": True, "account_id": account_id}, status_code=201)


async def admin_patch_account(request: Request):
    admin = require_superadmin(request)
    account_id = request.path_params["account_id"]
    account = db.q1("SELECT * FROM accounts WHERE id = ?", (account_id,))
    if account is None:
        raise ApiError(404, "Compte introuvable.")
    data = await read_json(request)
    if "suspended" in data:
        if account_id == admin["account_id"]:
            raise ApiError(400, "Vous ne pouvez pas suspendre votre propre compte.")
        db.ex("UPDATE accounts SET suspended = ? WHERE id = ?", (1 if data["suspended"] is True else 0, account_id))
        if data["suspended"] is True:
            db.ex("DELETE FROM sessions WHERE user_id IN (SELECT id FROM users WHERE account_id = ?)", (account_id,))
    if "name" in data:
        db.ex("UPDATE accounts SET name = ? WHERE id = ?", (s(data, "name", 80), account_id))
    if "notes" in data:
        db.ex("UPDATE accounts SET notes = ? WHERE id = ?", (s(data, "notes", 2000, required=False), account_id))
    if "max_devices" in data:
        md = data["max_devices"]
        if md in ("", None):
            md = None
        elif isinstance(md, bool) or not isinstance(md, int) or md < 1:
            raise ApiError(400, "Nombre maximal de PC invalide.")
        db.ex("UPDATE accounts SET max_devices = ? WHERE id = ?", (md, account_id))
    return JSONResponse({"ok": True})


async def admin_delete_account(request: Request):
    admin = require_superadmin(request)
    account_id = request.path_params["account_id"]
    if account_id == admin["account_id"]:
        raise ApiError(400, "Vous ne pouvez pas supprimer votre propre compte.")
    row = db.q1("SELECT * FROM accounts WHERE id = ?", (account_id,))
    if row is None:
        raise ApiError(404, "Compte introuvable.")
    devices = [r["id"] for r in db.q("SELECT id FROM devices WHERE account_id = ?", (account_id,))]
    with db.transaction():
        db.ex("DELETE FROM accounts WHERE id = ?", (account_id,))
        db.log_event("account_deleted", f"Compte client supprimé : {row['name']}", admin["account_id"], admin["id"],
                     ip=client_ip(request))
    for device_id in devices:
        hub.wake_device(device_id)
    return JSONResponse({"ok": True})


async def admin_set_user_password(request: Request):
    admin = require_superadmin(request)
    uid = request.path_params["user_id"]
    target = db.q1("SELECT * FROM users WHERE id = ?", (uid,))
    if target is None:
        raise ApiError(404, "Utilisateur introuvable.")
    data = await read_json(request)
    problem = security.password_problem(data.get("password"))
    if problem:
        raise ApiError(400, problem)
    pw_hash = await asyncio.to_thread(security.hash_password, data["password"])
    db.ex("UPDATE users SET password_hash = ? WHERE id = ?", (pw_hash, uid))
    db.ex("DELETE FROM sessions WHERE user_id = ?", (uid,))
    db.log_event("password_reset", f"Mot de passe réinitialisé : {target['email']}", admin["account_id"], admin["id"],
                 ip=client_ip(request))
    return JSONResponse({"ok": True})


async def admin_settings(request: Request):
    require_superadmin(request)
    if request.method == "PATCH":
        data = await read_json(request)
        if "server_name" in data:
            db.set_meta("server_name", s(data, "server_name", 80))
        if "registration_open" in data:
            db.set_meta("registration_open", "1" if data["registration_open"] is True else "0")
        if "download_url" in data:
            url = s(data, "download_url", 300, required=False)
            if url and not url.startswith("https://"):
                raise ApiError(400, "Le lien de téléchargement doit commencer par https://")
            db.set_meta("download_url", url or None)
    return JSONResponse(settings_public())


# --- agent API -------------------------------------------------------------------------------------------

def device_from_auth(request: Request):
    auth = request.headers.get("authorization", "")
    if not auth.startswith("Bearer ") or "." not in auth:
        raise ApiError(401, "Identifiants de l'agent manquants.")
    device_id, _, token = auth[7:].strip().partition(".")
    row = db.q1("SELECT d.*, a.suspended AS account_suspended FROM devices d JOIN accounts a ON a.id = d.account_id "
                "WHERE d.id = ?", (device_id,))
    if row is None or not hmac.compare_digest(row["token_hash"], security.token_hash(token)):
        raise ApiError(401, "PC inconnu ou retiré de la console.")
    if row["account_suspended"]:
        # 423: the agent keeps its credentials and retries later (unlike 401/403).
        raise ApiError(423, "Compte client suspendu.")
    return row


def _store_info_and_state(device, data: dict, ip: str) -> None:
    info = data.get("info") if isinstance(data.get("info"), dict) else {}
    fields = {"last_seen": time.time(), "last_ip": ip}
    for key in ("hostname", "os", "agent_version", "app_version"):
        value = info.get(key)
        if isinstance(value, str) and value:
            fields[key] = value[:200]
    state = data.get("state")
    if isinstance(state, dict):
        fields["state_json"] = db.dumps(state)
        fields["state_at"] = time.time()
    if device["uninstalled_at"]:
        fields["uninstalled_at"] = None
    sets = ", ".join(f"{k} = ?" for k in fields)
    db.ex(f"UPDATE devices SET {sets} WHERE id = ?", (*fields.values(), device["id"]))


def _store_results(device, results) -> None:
    if not isinstance(results, list):
        return
    now = time.time()
    for res in results[:200]:
        if not isinstance(res, dict):
            continue
        try:
            cid = int(res.get("id"))
        except (TypeError, ValueError):
            continue
        ok = res.get("ok") is True
        result = res.get("result")
        error = res.get("error") if isinstance(res.get("error"), str) else ""
        duration = res.get("duration_ms") if isinstance(res.get("duration_ms"), int) else None
        cur = db.ex("UPDATE commands SET status = ?, result_json = ?, error = ?, done_at = ?, duration_ms = ? "
                    "WHERE id = ? AND device_id = ? AND status IN ('sent', 'pending')",
                    ("done" if ok else "error", db.dumps(result) if result is not None else None,
                     error[:2000], now, duration, cid, device["id"]))
        if cur.rowcount:
            cmd = db.q1("SELECT action FROM commands WHERE id = ?", (cid,))
            if ok and cmd and cmd["action"] == "get_state" and isinstance(result, dict):
                db.ex("UPDATE devices SET state_json = ?, state_at = ? WHERE id = ?",
                      (db.dumps(result), now, device["id"]))
            hub.wake_command(cid)


def _take_pending(device_id: str) -> list:
    rows = db.q("SELECT * FROM commands WHERE device_id = ? AND status = 'pending' ORDER BY id LIMIT 20", (device_id,))
    if not rows:
        return []
    now = time.time()
    db.ex(f"UPDATE commands SET status = 'sent', sent_at = ? WHERE id IN ({','.join('?' * len(rows))})",
          (now, *[r["id"] for r in rows]))
    return [{"id": r["id"], "action": r["action"], "params": db.loads(r["params_json"], {})} for r in rows]


async def agent_enroll(request: Request):
    ip = client_ip(request)
    if not security.limiter.hit(f"enroll:{ip}", 20, 900):
        raise ApiError(429, "Trop de tentatives d'ajout depuis cette adresse. Patientez 15 minutes.")
    data = await read_json(request)
    code = security.normalize_code(data.get("code") if isinstance(data.get("code"), str) else "")
    now = time.time()
    row = db.q1("SELECT c.*, a.suspended, a.max_devices, a.name AS account_name FROM enroll_codes c "
                "JOIN accounts a ON a.id = c.account_id WHERE c.code = ?", (code,))
    if (row is None or row["revoked"] or row["expires_at"] < now
            or (row["max_uses"] is not None and row["uses"] >= row["max_uses"])):
        db.log_event("enroll_failed", "Code d'ajout invalide ou expiré", row["account_id"] if row else None, ip=ip)
        raise ApiError(403, "Code d'ajout invalide ou expiré. Générez un nouveau code dans la console.")
    if row["suspended"]:
        raise ApiError(403, "Ce compte client est suspendu.")
    hostname = (data.get("hostname") if isinstance(data.get("hostname"), str) else "")[:100] or "PC"
    machine_id = (data.get("machine_id") if isinstance(data.get("machine_id"), str) else "")[:100]
    existing = None
    if machine_id:
        existing = db.q1("SELECT * FROM devices WHERE account_id = ? AND machine_id = ?", (row["account_id"], machine_id))
    if existing is None and row["max_devices"] is not None:
        count = db.q1("SELECT COUNT(*) AS n FROM devices WHERE account_id = ?", (row["account_id"],))["n"]
        if count >= row["max_devices"]:
            raise ApiError(403, f"Nombre maximal de PC atteint pour ce compte ({row['max_devices']}).")
    token = security.new_token()
    info = {k: (data.get(k)[:200] if isinstance(data.get(k), str) else "") for k in ("os", "agent_version", "app_version")}
    with db.transaction():
        if existing is not None:
            device_id = existing["id"]
            db.ex("UPDATE devices SET token_hash = ?, hostname = ?, os = ?, agent_version = ?, app_version = ?, "
                  "uninstalled_at = NULL, enrolled_at = ? WHERE id = ?",
                  (security.token_hash(token), hostname, info["os"], info["agent_version"], info["app_version"],
                   now, device_id))
            message = f"PC reconnecté : {existing['name']}"
        else:
            device_id = security.new_device_id()
            label = row["label"].strip()
            name = f"{label} ({hostname})" if label and row["max_uses"] == 1 else hostname
            db.ex("INSERT INTO devices(id, account_id, token_hash, name, hostname, os, machine_id, agent_version, "
                  "app_version, enrolled_at, last_ip) VALUES(?,?,?,?,?,?,?,?,?,?,?)",
                  (device_id, row["account_id"], security.token_hash(token), name, hostname, info["os"], machine_id,
                   info["agent_version"], info["app_version"], now, ip))
            message = f"Nouveau PC ajouté : {hostname}"
        db.ex("UPDATE enroll_codes SET uses = uses + 1 WHERE id = ?", (row["id"],))
        db.log_event("device_enrolled", message, row["account_id"], device_id=device_id, ip=ip)
    return JSONResponse({"device_id": device_id, "token": token, "account_name": row["account_name"],
                         "poll_hold": settings.POLL_HOLD_SECONDS})


async def agent_poll(request: Request):
    device = device_from_auth(request)
    data = await read_json(request)
    ip = client_ip(request)
    with db.transaction():
        _store_info_and_state(device, data, ip)
        _store_results(device, data.get("results"))
    lang = settings.DEFAULT_AGENT_LANG
    deadline = time.monotonic() + settings.POLL_HOLD_SECONDS
    commands = []
    while True:
        if db.q1("SELECT 1 FROM devices WHERE id = ?", (device["id"],)) is None:
            raise ApiError(401, "PC retiré de la console.")
        commands = _take_pending(device["id"])
        remaining = deadline - time.monotonic()
        if commands or remaining <= 0:
            break
        ev = hub.device(device["id"])
        ev.clear()
        await wait_event(ev, min(remaining, 5.0))
        if await request.is_disconnected():
            return Response(status_code=204)  # nothing was taken: commands stay pending
    db.ex("UPDATE devices SET last_seen = ? WHERE id = ?", (time.time(), device["id"]))
    return JSONResponse({"commands": commands, "lang": lang, "server_time": time.time()})


async def agent_results(request: Request):
    device = device_from_auth(request)
    data = await read_json(request)
    with db.transaction():
        _store_info_and_state(device, data, client_ip(request))
        _store_results(device, data.get("results"))
    return JSONResponse({"ok": True})


async def agent_goodbye(request: Request):
    device = device_from_auth(request)
    db.ex("UPDATE devices SET uninstalled_at = ?, last_seen = ? WHERE id = ?", (time.time(), time.time(), device["id"]))
    db.ex("UPDATE commands SET status = 'cancelled', done_at = ? WHERE device_id = ? AND status IN ('pending','sent')",
          (time.time(), device["id"]))
    db.log_event("device_uninstalled", f"HOTS Hosts désinstallé de {device['name']}", device["account_id"],
                 device_id=device["id"], ip=client_ip(request))
    return JSONResponse({"ok": True})


async def health(request: Request):
    db.q1("SELECT 1")
    return JSONResponse({"ok": True, "version": __version__})


async def index(request: Request):
    return FileResponse(os.path.join(STATIC_DIR, "index.html"), headers={"Cache-Control": "no-cache"})


# --- maintenance ---------------------------------------------------------------------------------------

def maintenance_once() -> None:
    now = time.time()
    expired = db.q("SELECT id FROM commands WHERE (status = 'sent' AND sent_at < ?) OR (status = 'pending' AND created_at < ?)",
                   (now - SENT_TIMEOUT, now - PENDING_TIMEOUT))
    if expired:
        db.ex("UPDATE commands SET status = 'expired', error = 'Pas de réponse du PC dans le délai imparti.', done_at = ? "
              f"WHERE id IN ({','.join('?' * len(expired))})", (now, *[r["id"] for r in expired]))
        for r in expired:
            hub.wake_command(r["id"])
    db.ex(f"UPDATE commands SET result_json = NULL WHERE result_json IS NOT NULL AND done_at < ? "
          f"AND action IN ({','.join('?' * len(BULKY_RESULTS))})", (now - 86400, *BULKY_RESULTS))
    db.ex("DELETE FROM commands WHERE created_at < ?", (now - HISTORY_DAYS * 86400,))
    db.ex("DELETE FROM events WHERE created_at < ?", (now - 365 * 86400,))
    db.ex("DELETE FROM sessions WHERE expires_at < ?", (now,))


async def _maintenance_loop():
    while True:
        try:
            maintenance_once()
        except Exception:
            log.exception("maintenance failed")
        await asyncio.sleep(60)


@contextlib.asynccontextmanager
async def lifespan(app):
    db.init()
    token = ensure_setup_token()
    if token:
        log.warning("Server not configured yet: open /#/setup/%s to create the administrator account", token)
    task = asyncio.create_task(_maintenance_loop())
    try:
        yield
    finally:
        task.cancel()
        db.close()


# --- middlewares -----------------------------------------------------------------------------------------

SECURITY_HEADERS = [
    (b"x-content-type-options", b"nosniff"),
    (b"x-frame-options", b"DENY"),
    (b"referrer-policy", b"no-referrer"),
    (b"permissions-policy", b"camera=(), microphone=(), geolocation=()"),
    (b"content-security-policy",
     b"default-src 'self'; img-src 'self' data:; style-src 'self'; script-src 'self'; "
     b"connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'"),
]


class GuardMiddleware:
    """Body size limit, CSRF header on console writes, JSON errors, security headers."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        path = scope.get("path", "")
        method = scope.get("method", "GET")
        headers = {k.decode("latin-1").lower(): v.decode("latin-1") for k, v in scope.get("headers", [])}
        is_agent = path.startswith("/api/agent/")
        limit = MAX_AGENT_BODY if is_agent else (MAX_COMMAND_BODY if path.endswith("/commands") else MAX_DEFAULT_BODY)

        async def reply(status: int, detail: str):
            await JSONResponse({"detail": detail}, status_code=status)(scope, receive, send_with_headers)

        async def send_with_headers(message):
            if message["type"] == "http.response.start":
                message.setdefault("headers", [])
                message["headers"] = list(message["headers"]) + SECURITY_HEADERS
            await send(message)

        if path.startswith("/api/") and not is_agent and method in ("POST", "PUT", "PATCH", "DELETE"):
            if headers.get(CSRF_HEADER) != "1":
                return await reply(403, "Requête refusée (protection CSRF).")
        try:
            declared = int(headers.get("content-length", "0") or 0)
        except ValueError:
            declared = 0
        if declared > limit:
            return await reply(413, "Requête trop volumineuse.")

        received = 0

        async def limited_receive():
            nonlocal received
            message = await receive()
            if message["type"] == "http.request":
                received += len(message.get("body", b""))
                if received > limit:
                    raise ApiError(413, "Requête trop volumineuse.")
            return message

        try:
            await self.app(scope, limited_receive, send_with_headers)
        except ApiError as e:
            await reply(e.status, e.detail)


async def api_error_handler(request: Request, exc: ApiError):
    return err(exc.status, exc.detail)


def _int_path(name: str) -> str:
    return "{" + name + ":int}"


routes = [
    Route("/", index),
    Route("/healthz", health),
    Route("/api/bootstrap", bootstrap),
    Route("/api/setup", setup, methods=["POST"]),
    Route("/api/auth/login", login, methods=["POST"]),
    Route("/api/auth/logout", logout, methods=["POST"]),
    Route("/api/auth/register", register, methods=["POST"]),
    Route("/api/me/password", change_password, methods=["POST"]),
    Route("/api/me/profile", update_profile, methods=["POST"]),
    Route("/api/devices", list_devices),
    Route("/api/devices/{device_id}", get_device),
    Route("/api/devices/{device_id}", patch_device, methods=["PATCH"]),
    Route("/api/devices/{device_id}", delete_device, methods=["DELETE"]),
    Route("/api/devices/{device_id}/commands", create_command, methods=["POST"]),
    Route("/api/devices/{device_id}/commands", list_commands),
    Route(f"/api/commands/{_int_path('command_id')}", get_command),
    Route(f"/api/commands/{_int_path('command_id')}/cancel", cancel_command, methods=["POST"]),
    Route("/api/enroll-codes", list_codes),
    Route("/api/enroll-codes", create_code, methods=["POST"]),
    Route(f"/api/enroll-codes/{_int_path('code_id')}", revoke_code, methods=["DELETE"]),
    Route("/api/account/users", list_account_users),
    Route("/api/account/users", add_account_user, methods=["POST"]),
    Route(f"/api/account/users/{_int_path('user_id')}", delete_account_user, methods=["DELETE"]),
    Route("/api/events", list_events),
    Route("/api/admin/accounts", admin_accounts),
    Route("/api/admin/accounts", admin_create_account, methods=["POST"]),
    Route(f"/api/admin/accounts/{_int_path('account_id')}", admin_patch_account, methods=["PATCH"]),
    Route(f"/api/admin/accounts/{_int_path('account_id')}", admin_delete_account, methods=["DELETE"]),
    Route(f"/api/admin/users/{_int_path('user_id')}/password", admin_set_user_password, methods=["POST"]),
    Route("/api/admin/settings", admin_settings, methods=["GET", "PATCH"]),
    Route("/api/agent/enroll", agent_enroll, methods=["POST"]),
    Route("/api/agent/poll", agent_poll, methods=["POST"]),
    Route("/api/agent/results", agent_results, methods=["POST"]),
    Route("/api/agent/goodbye", agent_goodbye, methods=["POST"]),
    Mount("/static", app=StaticFiles(directory=STATIC_DIR), name="static"),
]


def create_app() -> Starlette:
    application = Starlette(routes=routes, lifespan=lifespan, exception_handlers={ApiError: api_error_handler})
    application.add_middleware(GuardMiddleware)
    return application


app = create_app()
