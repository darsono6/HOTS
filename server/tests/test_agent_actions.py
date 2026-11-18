"""The real agent actions (hosts_editor/remote/actions.py) run against a temporary hosts file.

Windows-only parts (registry, firewall, services) are not exercised here; the hosts-file logic,
parameter validation and the parental blocks are the same code that runs on the PC.
"""

import hashlib
import sys
import types

import pytest

sys.modules.setdefault("winreg", types.ModuleType("winreg"))

from hosts_editor import constants, core  # noqa: E402
from hosts_editor.remote import actions, config, netutil  # noqa: E402

HOSTS = "127.0.0.1 localhost\n# commentaire\n192.168.1.20 nas.maison # NAS\n# 10.0.0.5 imprimante.local\n"


@pytest.fixture()
def hosts(tmp_path, monkeypatch):
    path = tmp_path / "hosts"
    path.write_text(HOSTS, encoding="utf-8")
    monkeypatch.setattr(constants, "HOSTS_PATH", str(path))
    monkeypatch.setattr(core, "HOSTS_PATH", str(path))
    monkeypatch.setattr(constants, "CUSTOM_DOMAINS_PATH", tmp_path / "custom_domains.txt")
    monkeypatch.setattr(core, "flush_dns_cache_debounced", lambda: None)
    monkeypatch.setattr(core, "_MIN_WRITE_GAP", 0)
    return path


def run(action, **params):
    ok, result, error, _mutating = actions.execute(action, params)
    return ok, result, error


def test_parental_category_block_and_unblock(hosts):
    ok, _, err = run("parental.set", category="tiktok.txt", enabled=True)
    assert ok, err
    text = hosts.read_text(encoding="utf-8")
    assert "# === HOSTS_EDITOR_PARENTAL_TIKTOK_START ===" in text
    assert "0.0.0.0 tiktok.com" in text
    assert "192.168.1.20 nas.maison # NAS" in text  # user entries untouched
    state = actions._state_parental()
    assert next(c for c in state["categories"] if c["file"] == "tiktok.txt")["active"] is True
    assert next(c for c in state["categories"] if c["file"] == "tiktok.txt")["label"] == "TikTok"

    ok, _, err = run("parental.set", category="tiktok.txt", enabled=False)
    assert ok, err
    assert "tiktok" not in hosts.read_text(encoding="utf-8").lower()


def test_parental_rejects_unknown_category_and_bad_params(hosts):
    assert run("parental.set", category="../../windows/win.ini", enabled=True)[2].startswith("Catégorie inconnue")
    assert "invalide" in run("parental.set", category="tiktok.txt", enabled="yes")[2]
    assert run("parental.set", category="custom_domains.txt", enabled=True)[2] == "La liste de domaines personnalisés est vide."


def test_custom_domains(hosts):
    ok, result, err = run("custom_domains.set", domains=["https://www.Casino.example/page", "jeux.example"], apply=True)
    assert ok, err
    assert result == {"count": 2, "active": True}
    assert "0.0.0.0 www.casino.example" in hosts.read_text(encoding="utf-8")
    ok, _, err = run("custom_domains.set", domains=["pas un domaine!"])
    assert not ok and "Domaines invalides" in err
    ok, result, _ = run("custom_domains.set", domains=[])
    assert result == {"count": 0, "active": False}
    assert "casino" not in hosts.read_text(encoding="utf-8")


def test_hosts_entries_roundtrip(hosts):
    ok, data, err = run("hosts.read")
    assert ok, err
    assert [(e["ip"], e["hostname"], e["enabled"]) for e in data["entries"]] == [
        ("127.0.0.1", "localhost", True), ("192.168.1.20", "nas.maison", True), ("10.0.0.5", "imprimante.local", False)]
    assert data["sha256"] == hashlib.sha256(HOSTS.encode()).hexdigest()

    assert run("hosts.add_entry", ip="0.0.0.0", hostname="roblox.com", comment="jeu")[0]
    assert "0.0.0.0 roblox.com # jeu" in hosts.read_text(encoding="utf-8")

    printer = next(e for e in run("hosts.read")[1]["entries"] if e["hostname"] == "imprimante.local")
    ok, _, err = run("hosts.update_entry", line=printer["line"], expect=printer["raw"], enabled=True)
    assert ok, err
    assert "\n10.0.0.5 imprimante.local\n" in hosts.read_text(encoding="utf-8")

    # stale "expect": the file changed since the console read it
    ok, _, err = run("hosts.delete_entry", line=printer["line"], expect=printer["raw"])
    assert not ok and "modifié entre-temps" in err

    nas = next(e for e in run("hosts.read")[1]["entries"] if e["hostname"] == "nas.maison")
    assert run("hosts.delete_entry", line=nas["line"], expect=nas["raw"])[0]
    assert "nas.maison" not in hosts.read_text(encoding="utf-8")
    assert run("hosts.backups")[1]["backups"]  # a backup is made before each write


def test_hosts_validation(hosts):
    assert "Adresse IP invalide" in run("hosts.add_entry", ip="999.1.1.1", hostname="a.com")[2]
    assert "Nom d'hôte invalide" in run("hosts.add_entry", ip="0.0.0.0", hostname="a.com;rm -rf")[2]
    assert "retour à la ligne" in run("hosts.add_entry", ip="0.0.0.0", hostname="a.com\n1.2.3.4 b.com")[2]


def test_hosts_save_text_requires_current_hash(hosts):
    assert "modifié entre-temps" in run("hosts.save_text", text="127.0.0.1 localhost\n", expect_sha256="0" * 64)[2]
    sha = run("hosts.read")[1]["sha256"]
    assert run("hosts.save_text", text="127.0.0.1 localhost\n0.0.0.0 x.com\n", expect_sha256=sha)[0]
    assert hosts.read_text(encoding="utf-8") == "127.0.0.1 localhost\n0.0.0.0 x.com\n"


def test_backup_restore_rejects_path_tricks(hosts):
    assert run("hosts.restore_backup", name="../../etc/passwd")[2] == "Nom de sauvegarde invalide."
    assert run("hosts.restore_backup", name="hosts.bak_20000101_000000")[2] == "Sauvegarde introuvable."


def test_app_names_are_validated():
    assert "invalide" in run("apps.add", exe_name="..\\..\\windows\\system32\\cmd")[2]
    assert "ne peut pas se bloquer" in run("apps.add", exe_name="HOTS Remote Agent.exe")[2]


def test_privacy_user_scope_items_are_refused():
    assert "session de l'utilisateur" in run("privacy.set_item", id="advertising_id", enabled=True)[2]
    assert run("privacy.set_level", level="root", enabled=True)[2] == "Niveau inconnu : root"


def test_state_never_raises_on_missing_windows_parts(hosts):
    state = actions.build_state()
    assert "parental" in state and "hosts" in state
    assert state["hosts"]["active_entries"] == 2
    assert isinstance(state["errors"], dict)  # registry / firewall sections fail cleanly on Linux


def test_netblock_keeps_console_reachable():
    spec = "1.0.0.0-9.255.255.255,11.0.0.0-126.255.255.255"
    carved = netutil.carve_ranges(spec, ["8.8.8.8", "51.15.20.30"])
    assert carved == "1.0.0.0-8.8.8.7,8.8.8.9-9.255.255.255,11.0.0.0-51.15.20.29,51.15.20.31-126.255.255.255"
    assert netutil.carve_ranges("2000::/3", ["2001:db8::1"]) == "2000::-2001:db8::,2001:db8::2-3fff:ffff:ffff:ffff:ffff:ffff:ffff:ffff"
    assert netutil.carve_ranges(spec, ["not-an-ip"]) == spec


def test_console_url_must_be_https(monkeypatch):
    monkeypatch.delenv("HOTS_AGENT_ALLOW_HTTP", raising=False)
    assert config.normalize_server_url("Console.Example.fr/") == "https://console.example.fr"
    with pytest.raises(ValueError):
        config.normalize_server_url("http://192.168.1.10")
    with pytest.raises(ValueError):
        config.normalize_server_url("https://user:pass@console.example.fr")
    assert config.normalize_server_url("http://127.0.0.1:8080") == "http://127.0.0.1:8080"
