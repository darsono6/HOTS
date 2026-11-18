import sys
import types

import pytest


def _login(client, email, password):
    client.cookies.clear()
    r = client.post("/api/auth/login", json={"email": email, "password": password})
    assert r.status_code == 200, r.text


def _enroll(client, code, machine_id="m-1", hostname="PC-SALON"):
    r = client.post("/api/agent/enroll", json={"code": code, "hostname": hostname, "machine_id": machine_id,
                                               "os": "Windows 11", "agent_version": "1.0.0", "app_version": "2.5.1"})
    return r


def test_setup_requires_token(client):
    r = client.get("/api/bootstrap")
    assert r.json()["setup_required"] is True
    r = client.post("/api/setup", json={"token": "bad", "email": "a@b.fr", "password": "x" * 12})
    assert r.status_code == 403


def test_setup_and_login(admin):
    r = admin.get("/api/bootstrap").json()
    assert r["setup_required"] is False and r["user"]["is_superadmin"] is True and r["server_name"] == "Test"
    admin.post("/api/auth/logout")
    assert admin.get("/api/bootstrap").json()["user"] is None
    r = admin.post("/api/auth/login", json={"email": "admin@example.com", "password": "mauvais-mot-de-passe"})
    assert r.status_code == 401
    _login(admin, "ADMIN@example.com", "motdepasse-admin")
    assert admin.get("/api/devices").status_code == 200


def test_csrf_header_required(admin):
    r = admin.post("/api/enroll-codes", json={}, headers={"x-hots-csrf": "0"})
    assert r.status_code == 403


def test_security_headers(admin):
    r = admin.get("/api/bootstrap")
    assert "default-src 'self'" in r.headers["content-security-policy"]
    assert r.headers["x-frame-options"] == "DENY"


def test_accounts_are_isolated(admin):
    r = admin.post("/api/admin/accounts", json={"account_name": "Famille Martin", "name": "Paul",
                                                "email": "paul@example.com", "password": "motdepasse-paul"})
    assert r.status_code == 201, r.text
    code_admin = admin.post("/api/enroll-codes", json={"label": "PC admin"}).json()["code"]
    assert _enroll(admin, code_admin, machine_id="admin-pc").status_code == 200

    _login(admin, "paul@example.com", "motdepasse-paul")
    assert admin.get("/api/devices").json()["devices"] == []
    code = admin.post("/api/enroll-codes", json={"label": "Chambre", "max_uses": 1}).json()["code"]
    r = _enroll(admin, code.replace("-", "").lower(), machine_id="paul-pc")
    assert r.status_code == 200, r.text
    devices = admin.get("/api/devices").json()["devices"]
    assert len(devices) == 1 and devices[0]["name"] == "Chambre (PC-SALON)"
    # single-use code is exhausted
    assert _enroll(admin, code, machine_id="other").status_code == 403

    # Paul cannot see or command the admin's PC
    _login(admin, "admin@example.com", "motdepasse-admin")
    admin_pc = admin.get("/api/devices").json()["devices"][0]["id"]
    _login(admin, "paul@example.com", "motdepasse-paul")
    assert admin.get(f"/api/devices/{admin_pc}").status_code == 404
    assert admin.post(f"/api/devices/{admin_pc}/commands", json={"action": "agent.ping"}).status_code == 404
    assert admin.get("/api/admin/accounts").status_code == 403


def test_reenroll_same_machine_reuses_device(admin):
    code = admin.post("/api/enroll-codes", json={}).json()["code"]
    first = _enroll(admin, code, machine_id="same").json()
    second = _enroll(admin, code, machine_id="same").json()
    assert first["device_id"] == second["device_id"] and first["token"] != second["token"]
    # the old token no longer works
    r = admin.post("/api/agent/results", json={"results": []},
                   headers={"Authorization": f"Bearer {first['device_id']}.{first['token']}"})
    assert r.status_code == 401


def test_command_roundtrip(admin):
    code = admin.post("/api/enroll-codes", json={}).json()["code"]
    creds = _enroll(admin, code).json()
    auth = {"Authorization": f"Bearer {creds['device_id']}.{creds['token']}"}
    dev = creds["device_id"]

    assert admin.post(f"/api/devices/{dev}/commands", json={"action": "rm -rf"}).status_code == 400
    cmd = admin.post(f"/api/devices/{dev}/commands",
                     json={"action": "parental.set", "params": {"category": "tiktok.txt", "enabled": True},
                           "summary": "Bloquer TikTok"}).json()
    assert cmd["status"] == "pending"

    r = admin.post("/api/agent/poll", json={"info": {"hostname": "PC-SALON"}, "results": [],
                                            "state": {"parental": {"categories": [{"file": "tiktok.txt", "active": False}]}}},
                   headers=auth)
    assert r.status_code == 200
    commands = r.json()["commands"]
    assert [c["action"] for c in commands] == ["parental.set"]
    assert commands[0]["params"] == {"category": "tiktok.txt", "enabled": True}

    state = {"parental": {"categories": [{"file": "tiktok.txt", "active": True}]}}
    r = admin.post("/api/agent/results", json={"results": [{"id": cmd["id"], "ok": True, "result": {"x": 1}}],
                                               "state": state}, headers=auth)
    assert r.status_code == 200
    done = admin.get(f"/api/commands/{cmd['id']}").json()
    assert done["status"] == "done" and done["result"] == {"x": 1}
    device = admin.get(f"/api/devices/{dev}").json()
    assert device["online"] is True and device["summary"]["categories_active"] == 1
    history = admin.get(f"/api/devices/{dev}/commands").json()["commands"]
    assert history[0]["summary"] == "Bloquer TikTok"

    # a result for another device's command is ignored
    r = admin.post("/api/agent/results", json={"results": [{"id": cmd["id"], "ok": False, "error": "x"}]}, headers=auth)
    assert admin.get(f"/api/commands/{cmd['id']}").json()["status"] == "done"


def test_device_removal_revokes_agent(admin):
    code = admin.post("/api/enroll-codes", json={}).json()["code"]
    creds = _enroll(admin, code).json()
    auth = {"Authorization": f"Bearer {creds['device_id']}.{creds['token']}"}
    assert admin.delete(f"/api/devices/{creds['device_id']}").status_code == 200
    assert admin.post("/api/agent/poll", json={}, headers=auth).status_code == 401


def test_suspended_account_keeps_agent_credentials(admin):
    admin.post("/api/admin/accounts", json={"account_name": "Client", "email": "c@example.com",
                                            "password": "motdepasse-client"})
    _login(admin, "c@example.com", "motdepasse-client")
    code = admin.post("/api/enroll-codes", json={}).json()["code"]
    creds = _enroll(admin, code).json()
    _login(admin, "admin@example.com", "motdepasse-admin")
    account_id = [a for a in admin.get("/api/admin/accounts").json()["accounts"] if a["name"] == "Client"][0]["id"]
    admin.patch(f"/api/admin/accounts/{account_id}", json={"suspended": True})
    r = admin.post("/api/agent/poll", json={}, headers={"Authorization": f"Bearer {creds['device_id']}.{creds['token']}"})
    assert r.status_code == 423  # not 401: the agent must not forget its credentials
    r = admin.post("/api/auth/login", json={"email": "c@example.com", "password": "motdepasse-client"})
    assert r.status_code == 403


def test_max_devices(admin):
    admin.post("/api/admin/accounts", json={"account_name": "Petit", "email": "p@example.com",
                                            "password": "motdepasse-petit", "max_devices": 1})
    _login(admin, "p@example.com", "motdepasse-petit")
    code = admin.post("/api/enroll-codes", json={}).json()["code"]
    assert _enroll(admin, code, machine_id="a").status_code == 200
    assert _enroll(admin, code, machine_id="a").status_code == 200  # same PC again is fine
    assert _enroll(admin, code, machine_id="b").status_code == 403


def test_registration_toggle(admin):
    admin.post("/api/auth/logout")
    body = {"email": "new@example.com", "password": "motdepasse-new", "account_name": "Nouveau"}
    assert admin.post("/api/auth/register", json=body).status_code == 403
    _login(admin, "admin@example.com", "motdepasse-admin")
    admin.patch("/api/admin/settings", json={"registration_open": True})
    admin.post("/api/auth/logout")
    assert admin.post("/api/auth/register", json=body).status_code == 200
    assert admin.get("/api/bootstrap").json()["user"]["email"] == "new@example.com"


def test_account_members(admin):
    r = admin.post("/api/account/users", json={"email": "conjoint@example.com", "password": "motdepasse-conjoint",
                                               "name": "Conjoint"})
    assert r.status_code == 201
    users = admin.get("/api/account/users").json()["users"]
    assert {u["email"] for u in users} == {"admin@example.com", "conjoint@example.com"}
    _login(admin, "conjoint@example.com", "motdepasse-conjoint")
    assert admin.post("/api/account/users", json={"email": "x@example.com", "password": "motdepasse-xxxx"}).status_code == 403


def test_change_password(admin):
    assert admin.post("/api/me/password", json={"current": "faux", "new": "nouveau-mot-de-passe"}).status_code == 400
    assert admin.post("/api/me/password", json={"current": "motdepasse-admin", "new": "court"}).status_code == 400
    assert admin.post("/api/me/password", json={"current": "motdepasse-admin",
                                                "new": "nouveau-mot-de-passe"}).status_code == 200
    _login(admin, "admin@example.com", "nouveau-mot-de-passe")


def test_body_limit(admin):
    r = admin.post("/api/auth/login", content=b"{" + b" " * 300_000 + b"}",
                   headers={"content-type": "application/json"})
    assert r.status_code == 413


def test_server_and_agent_action_lists_match():
    sys.modules.setdefault("winreg", types.ModuleType("winreg"))
    from hosts_editor.remote import actions
    from hots_server.app import ACTIONS
    assert sorted(ACTIONS) == actions.list_actions()
    for name, mutating in ACTIONS.items():
        assert actions.is_mutating(name) == mutating, name


@pytest.mark.parametrize("raw,expected", [("abcd-efgh", "ABCDEFGH"), (" ab cd ef gh ", "ABCDEFGH")])
def test_code_normalization(raw, expected):
    from hots_server.security import normalize_code
    assert normalize_code(raw) == expected
