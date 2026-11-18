"""End to end: real uvicorn server + the real agent loop (hosts_editor.remote.agent) with a fake executor."""

import socket
import threading
import time

import httpx
import pytest
import uvicorn


def _free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


@pytest.fixture()
def live_server(fresh_db):
    from hots_server.app import create_app
    port = _free_port()
    server = uvicorn.Server(uvicorn.Config(create_app(), host="127.0.0.1", port=port, log_level="warning"))
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    for _ in range(100):
        if server.started:
            break
        time.sleep(0.05)
    yield f"http://127.0.0.1:{port}"
    server.should_exit = True
    thread.join(timeout=10)


def test_agent_end_to_end(live_server, tmp_path, monkeypatch):
    monkeypatch.setenv("HOTS_AGENT_DIR", str(tmp_path / "agent"))
    from hots_server import db
    from hosts_editor.remote import config
    from hosts_editor.remote.agent import Agent, enroll

    console = httpx.Client(base_url=live_server, headers={"x-hots-csrf": "1"}, timeout=30)
    r = console.post("/api/setup", json={"token": db.get_meta("setup_token"), "email": "parent@example.com",
                                         "password": "motdepasse-parent"})
    assert r.status_code == 200, r.text
    code = console.post("/api/enroll-codes", json={"label": "Chambre"}).json()["code"]

    cfg = enroll(live_server, code, {"hostname": "PC-ENFANT", "os": "Windows 11 Famille", "machine_id": "abc",
                                     "agent_version": "1.0.0", "app_version": "2.5.1"})
    assert config.load()["device_id"] == cfg["device_id"]
    assert cfg["server_ips"] == ["127.0.0.1"]

    state = {"parental": {"categories": [{"file": "tiktok.txt", "label": "TikTok", "active": False}]}}
    executed = []

    def executor(action, params, lang):
        executed.append((action, params, lang))
        if action == "parental.set":
            state["parental"]["categories"][0]["active"] = params["enabled"]
            return True, {"category": params["category"]}, "", True
        if action == "hosts.read":
            return False, None, "Le fichier hosts est verrouillé", False
        return False, None, f"Action inconnue : {action}", False

    stop = threading.Event()
    agent = Agent(cfg, executor=executor, state_builder=lambda lang: {**state, "lang": lang},
                  info_builder=lambda: {"hostname": "PC-ENFANT", "agent_version": "1.0.0"}, stop_event=stop)
    thread = threading.Thread(target=agent.run, daemon=True)
    thread.start()
    try:
        device_id = cfg["device_id"]
        for _ in range(50):
            device = console.get(f"/api/devices/{device_id}").json()
            if device["online"] and device["state"]:
                break
            time.sleep(0.1)
        assert device["online"] is True
        assert device["summary"]["categories_active"] == 0

        started = time.monotonic()
        cmd = console.post(f"/api/devices/{device_id}/commands",
                           json={"action": "parental.set", "params": {"category": "tiktok.txt", "enabled": True}}).json()
        done = console.get(f"/api/commands/{cmd['id']}", params={"wait": 10}).json()
        latency = time.monotonic() - started
        assert done["status"] == "done", done
        assert latency < 3, f"command took {latency:.1f}s"
        assert executed[-1] == ("parental.set", {"category": "tiktok.txt", "enabled": True}, "fr")

        device = console.get(f"/api/devices/{device_id}").json()
        assert device["summary"]["categories_active"] == 1  # state pushed with the result

        cmd = console.post(f"/api/devices/{device_id}/commands", json={"action": "hosts.read"}).json()
        failed = console.get(f"/api/commands/{cmd['id']}", params={"wait": 10}).json()
        assert failed["status"] == "error" and "verrouillé" in failed["error"]

        # Removing the PC from the console revokes the agent, which forgets its credentials.
        assert console.delete(f"/api/devices/{device_id}").status_code == 200
        thread.join(timeout=15)
        assert not thread.is_alive()
        assert agent.revoked is True
        assert config.load() is None
    finally:
        stop.set()
        thread.join(timeout=5)


def test_agent_survives_server_outage(tmp_path, monkeypatch):
    """No server: the agent keeps retrying with backoff and records the error, without crashing."""
    monkeypatch.setenv("HOTS_AGENT_DIR", str(tmp_path / "agent"))
    from hosts_editor.remote import agent as agent_mod, config
    monkeypatch.setattr(agent_mod, "MAX_BACKOFF", 1)
    cfg = {"server_url": f"http://127.0.0.1:{_free_port()}", "device_id": "pc_x", "token": "t", "server_ips": []}
    config.save(cfg)
    stop = threading.Event()
    agent = agent_mod.Agent(cfg, executor=lambda *a: (True, None, "", False), state_builder=lambda lang: {},
                            info_builder=lambda: {}, stop_event=stop)
    thread = threading.Thread(target=agent.run, daemon=True)
    thread.start()
    time.sleep(2.5)
    assert thread.is_alive()
    assert config.read_status()["connected"] is False
    stop.set()
    thread.join(timeout=5)
    assert config.load() is not None  # credentials kept: only a 401 from the server removes them
