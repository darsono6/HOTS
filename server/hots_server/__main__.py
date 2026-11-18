"""Command line: `python -m hots_server <command>`.

  serve [--host 127.0.0.1] [--port 8080]   run the web server (used by systemd)
  setup-link                                 print the setup token if no admin exists yet
  reset-password EMAIL                       set a new random password for a user (printed once)
  info                                       show accounts / PCs counts
  backup DIR [--keep N]                      consistent copy of the database (keeps the N newest)
"""

import argparse
import secrets
import sys
import time


def _serve(args):
    import uvicorn
    uvicorn.run("hots_server.app:app", host=args.host, port=args.port, proxy_headers=True,
                forwarded_allow_ips=args.forwarded_allow_ips, log_level="info", workers=1,
                timeout_keep_alive=75)


def _setup_link(args):
    from . import app, db
    db.init()
    token = app.ensure_setup_token()
    if token:
        print(token)
        return 0
    print("already-configured")
    return 1


def _reset_password(args):
    from . import db, security
    db.init()
    row = db.q1("SELECT * FROM users WHERE email = ?", (args.email.lower(),))
    if row is None:
        print(f"Utilisateur introuvable : {args.email}", file=sys.stderr)
        return 1
    alphabet = "abcdefghijkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    password = "".join(secrets.choice(alphabet) for _ in range(16))
    db.ex("UPDATE users SET password_hash = ?, disabled = 0 WHERE id = ?", (security.hash_password(password), row["id"]))
    db.ex("DELETE FROM sessions WHERE user_id = ?", (row["id"],))
    db.log_event("password_reset", f"Mot de passe réinitialisé en ligne de commande : {row['email']}", row["account_id"])
    print(password)
    return 0


def _info(args):
    from . import db, settings
    db.init()
    accounts = db.q1("SELECT COUNT(*) AS n FROM accounts")["n"]
    users = db.q1("SELECT COUNT(*) AS n FROM users")["n"]
    devices = db.q1("SELECT COUNT(*) AS n FROM devices")["n"]
    online = db.q1("SELECT COUNT(*) AS n FROM devices WHERE last_seen > ?",
                   (time.time() - settings.ONLINE_GRACE_SECONDS,))["n"]
    print(f"Comptes clients : {accounts}\nUtilisateurs : {users}\nPC : {devices} (en ligne : {online})\n"
          f"Base de données : {settings.DB_PATH}")
    return 0


def _backup(args):
    import os
    import sqlite3
    from . import db, settings
    db.init()
    os.makedirs(args.dir, exist_ok=True)
    target = os.path.join(args.dir, time.strftime("hots-%Y%m%d-%H%M%S.db"))
    dst = sqlite3.connect(target)
    with dst:
        db.get().backup(dst)
    dst.close()
    os.chmod(target, 0o600)
    backups = sorted(f for f in os.listdir(args.dir) if f.startswith("hots-") and f.endswith(".db"))
    for old in backups[:-args.keep] if args.keep > 0 else []:
        os.remove(os.path.join(args.dir, old))
    print(target)
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="hots_server", description="Console web HOTS Hosts")
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("serve")
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=8080)
    p.add_argument("--forwarded-allow-ips", default="127.0.0.1")
    p.set_defaults(func=_serve)
    sub.add_parser("setup-link").set_defaults(func=_setup_link)
    p = sub.add_parser("reset-password")
    p.add_argument("email")
    p.set_defaults(func=_reset_password)
    sub.add_parser("info").set_defaults(func=_info)
    p = sub.add_parser("backup")
    p.add_argument("dir")
    p.add_argument("--keep", type=int, default=14)
    p.set_defaults(func=_backup)
    args = parser.parse_args(argv)
    return args.func(args) or 0


if __name__ == "__main__":
    sys.exit(main())
