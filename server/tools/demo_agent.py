"""Simulated Windows PC for demos and UI tests (no Windows needed).

Uses the real agent loop (hosts_editor/remote/agent.py) and the real catalogs (categories,
privacy settings, browsers), but every action only changes an in-memory state.

    python server/tools/demo_agent.py --server http://127.0.0.1:8080 --code ABCD-EFGH --name PC-LEA
"""

import argparse
import hashlib
import os
import sys
import tempfile
import threading
import time
import types

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
sys.modules.setdefault("winreg", types.ModuleType("winreg"))  # catalogs only, nothing touches the registry

from hosts_editor.core import _parse_line  # noqa: E402
from hosts_editor.core_antispy import ITEMS  # noqa: E402
from hosts_editor.core_doh import BROWSERS  # noqa: E402
from hosts_editor.i18n import T, set_lang  # noqa: E402
from hosts_editor.parental_catalog import CATEGORIES, TELEMETRY_CATEGORY, comment_for_category  # noqa: E402
from hosts_editor.remote import AGENT_VERSION  # noqa: E402
from hosts_editor.remote.actions import normalize_domains  # noqa: E402
from hosts_editor.remote.agent import Agent, enroll  # noqa: E402

HOSTS_HEADER = """# Copyright (c) 1993-2009 Microsoft Corp.
#
# This is a sample HOSTS file used by Microsoft TCP/IP for Windows.
#
127.0.0.1 localhost
::1 localhost
192.168.1.20 nas.maison # NAS du salon
# 10.0.0.5 imprimante.local
"""


class DemoPC:
    def __init__(self, hostname: str):
        self.hostname = hostname
        self.lock = threading.RLock()
        self.cats = {c["file"]: False for c in CATEGORIES}
        self.cats["youtube.txt"] = True
        self.telemetry = False
        self.custom = ["jeux-flash.example", "casino.example"]
        self.custom_active = True
        self.cf = False
        self.prot = {"hosts_lock": True, "netblock": False, "vpn": False, "rstrui": False}
        self.doh = {b["id"]: b["id"] in ("chrome", "edge") for b in BROWSERS}
        self.apps = [{"exe_name": "fortnite.exe", "display_name": "Fortnite", "category": "custom", "enabled": True,
                      "locked_path": "", "added_at": time.time() - 86400}]
        self.privacy = {it["id"]: it["level"] == "basic" and it["kind"] != "hkcu_reg" for it in ITEMS}
        self.hosts = HOSTS_HEADER.splitlines()
        self.backups = [("hosts.bak_20261115_201500", "2026-11-15T20:15:00", 1210)]

    def info(self):
        return {"hostname": self.hostname, "os": "Windows 11 Famille 24H2 (build 26100.2314)",
                "app_version": "2.5.1", "agent_version": AGENT_VERSION, "machine_id": "demo-" + self.hostname}

    def state(self, lang="fr"):
        set_lang(lang)
        with self.lock:
            entries = [_parse_line(line) for line in self.hosts]
            return {
                "collected_at": time.time(), "errors": {},
                "system": dict(self.info(), uptime_s=3 * 3600 + 1200, is_admin=True),
                "parental": {
                    "categories": [{"file": c["file"], "label": comment_for_category(c), "icon": c["icon"],
                                    "color": c["color"], "active": self.cats[c["file"]], "available": True}
                                   for c in CATEGORIES],
                    "telemetry": {"file": "telemetry.txt", "label": comment_for_category(TELEMETRY_CATEGORY),
                                  "active": self.telemetry},
                    "custom": {"file": "custom_domains.txt", "active": self.custom_active, "domains": list(self.custom)},
                },
                "cf_family": {"active": self.cf, "details": "Wi-Fi: " + ("1.1.1.3, 1.0.0.3" if self.cf else "DHCP (192.168.1.1)")},
                "protections": dict(self.prot, doh=[{"id": b["id"], "name": b["name"], "installed": b["id"] != "vivaldi",
                                                     "blocked": self.doh[b["id"]]} for b in BROWSERS]),
                "apps": [dict(a) for a in self.apps],
                "privacy": {"levels": [{"id": lvl, "label": T(f"par_antispy_{lvl}_btn"), "items": [
                    {"id": it["id"], "label": T(it["label_key"]), "desc": T(it["desc_key"]), "kind": it["kind"],
                     "user_scope": it["kind"] == "hkcu_reg",
                     "active": None if it["kind"] == "hkcu_reg" else self.privacy[it["id"]],
                     "missing": it["id"] == "medium_task_usbceip"}
                    for it in ITEMS if it["level"] == lvl]} for lvl in ("basic", "medium", "advanced", "extra")]},
                "hosts": {"path": r"C:\Windows\System32\drivers\etc\hosts", "size": len("\n".join(self.hosts)),
                          "lines": len(entries), "active_entries": sum(1 for e in entries if e["enabled"] is True),
                          "disabled_entries": sum(1 for e in entries if e["enabled"] is False), "backups": len(self.backups)},
            }

    def _hosts_payload(self):
        text = "\n".join(self.hosts) + "\n"
        entries = [_parse_line(line) for line in self.hosts]
        return {"path": r"C:\Windows\System32\drivers\etc\hosts", "sha256": hashlib.sha256(text.encode()).hexdigest(),
                "size": len(text), "locked": self.prot["hosts_lock"], "text": text,
                "entries": [{"line": i, "enabled": e["enabled"], "ip": e["ip"], "hostname": e["hostname"],
                             "comment": e["comment"], "raw": e["raw"]} for i, e in enumerate(entries) if e["enabled"] is not None]}

    def execute(self, action, p, lang):
        time.sleep(0.4)  # a real PC takes a moment
        with self.lock:
            try:
                return self._execute(action, p, lang)
            except KeyError as e:
                return False, None, f"Paramètre manquant : {e}", True

    def _execute(self, action, p, lang):
        ok = lambda result=None, mutating=True: (True, result or {}, "", mutating)  # noqa: E731
        if action == "agent.ping":
            return ok({"pong": True}, False)
        if action == "get_state":
            return ok(self.state(lang), False)
        if action == "parental.set":
            if p["category"] == "custom_domains.txt":
                self.custom_active = p["enabled"]
            elif p["category"] == "telemetry.txt":
                self.telemetry = p["enabled"]
            else:
                self.cats[p["category"]] = p["enabled"]
            return ok()
        if action == "custom_domains.set":
            valid, invalid = normalize_domains(p["domains"])
            if invalid:
                return False, None, "Domaines invalides : " + ", ".join(invalid[:15]), True
            self.custom = valid
            self.custom_active = bool(valid) and (self.custom_active or p.get("apply") is True)
            return ok({"count": len(valid)})
        if action == "cf_family.set":
            self.cf = p["enabled"]
            if self.cf:
                self.cats["adult.txt"] = False
            return ok()
        if action in ("hosts_lock.set", "netblock.set", "vpn.set", "rstrui_lock.set"):
            key = {"hosts_lock.set": "hosts_lock", "netblock.set": "netblock", "vpn.set": "vpn", "rstrui_lock.set": "rstrui"}[action]
            self.prot[key] = p["enabled"]
            return ok()
        if action == "doh.set":
            self.doh[p["browser"]] = p["enabled"]
            return ok()
        if action == "apps.add":
            name = p["exe_name"].lower()
            name = name if name.endswith(".exe") else name + ".exe"
            if name in ("explorer.exe", "cmd.exe"):
                return False, None, "Ce programme système ne peut pas être bloqué.", True
            self.apps = [a for a in self.apps if a["exe_name"] != name]
            self.apps.append({"exe_name": name, "display_name": p.get("display_name") or name, "category": "custom",
                              "enabled": True, "locked_path": p.get("path") or "", "added_at": time.time()})
            return ok()
        if action == "apps.set_enabled":
            for a in self.apps:
                if a["exe_name"] == p["exe_name"]:
                    a["enabled"] = p["enabled"]
            return ok()
        if action == "apps.remove":
            self.apps = [a for a in self.apps if a["exe_name"] != p["exe_name"]]
            return ok()
        if action == "apps.list_installed":
            progs = [("Minecraft Launcher", r"C:\Program Files (x86)\Minecraft Launcher\MinecraftLauncher.exe"),
                     ("Roblox Player", r"C:\Users\lea\AppData\Local\Roblox\Versions\RobloxPlayerBeta.exe"),
                     ("Discord", r"C:\Users\lea\AppData\Local\Discord\app-1.0.9\Discord.exe"),
                     ("Steam", r"C:\Program Files (x86)\Steam\steam.exe"),
                     ("VLC media player", r"C:\Program Files\VideoLAN\VLC\vlc.exe")]
            return ok({"programs": [{"name": n, "path": path, "exe": path.rsplit("\\", 1)[-1]} for n, path in progs]}, False)
        if action == "privacy.set_item":
            self.privacy[p["id"]] = p["enabled"]
            return ok()
        if action == "privacy.set_level":
            for it in ITEMS:
                if it["level"] == p["level"] and it["kind"] != "hkcu_reg":
                    self.privacy[it["id"]] = p["enabled"]
            return ok()
        if action == "privacy.check_drift":
            return ok({"regressed": [], "restored": []}, False)
        if action == "system.restore_point":
            return ok({"status": "created"})
        if action == "dns.flush":
            return ok({"flushed": True})
        if action == "hosts.read":
            return ok(self._hosts_payload(), False)
        if action == "hosts.backups":
            return ok({"backups": [{"name": n, "date": d, "size": s} for n, d, s in self.backups]}, False)
        if action == "hosts.add_entry":
            line = f"{p['ip']} {p['hostname']}" + (f" # {p['comment']}" if p.get("comment") else "")
            self.hosts.append(line if p.get("enabled", True) else "# " + line)
            return ok()
        if action in ("hosts.update_entry", "hosts.delete_entry"):
            i = p["line"]
            if i >= len(self.hosts) or self.hosts[i] != p["expect"]:
                return False, None, "Le fichier hosts a été modifié entre-temps : rechargez la page et réessayez.", True
            if action == "hosts.delete_entry":
                del self.hosts[i]
                return ok()
            e = _parse_line(self.hosts[i])
            ip, host, comment = p.get("ip", e["ip"]), p.get("hostname", e["hostname"]), p.get("comment", e["comment"])
            enabled = p.get("enabled", e["enabled"])
            line = f"{ip} {host}" + (f" # {comment}" if comment else "")
            self.hosts[i] = line if enabled else "# " + line
            return ok()
        if action == "hosts.save_text":
            self.hosts = p["text"].rstrip("\n").split("\n")
            return ok()
        if action == "hosts.restore_backup":
            self.hosts = HOSTS_HEADER.splitlines()
            return ok()
        return False, None, f"Action inconnue : {action}", False


def main():
    ap = argparse.ArgumentParser(description="PC Windows simulé pour la démo de la console HOTS")
    ap.add_argument("--server", required=True)
    ap.add_argument("--code", required=True)
    ap.add_argument("--name", default="PC-DEMO")
    args = ap.parse_args()
    os.environ.setdefault("HOTS_AGENT_DIR", tempfile.mkdtemp(prefix=f"hots-demo-{args.name}-"))
    pc = DemoPC(args.name)
    cfg = enroll(args.server, args.code, pc.info())
    print(f"{args.name} connecté ({cfg['device_id']}) — Ctrl+C pour arrêter", flush=True)
    agent = Agent(cfg, executor=pc.execute, state_builder=pc.state, info_builder=pc.info)
    try:
        agent.run()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
