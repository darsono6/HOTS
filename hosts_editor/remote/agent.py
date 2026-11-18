"""Agent main loop.

- The main thread long-polls ``POST /api/agent/poll`` (heartbeat + pending results + state).
- Commands received are queued and run one at a time by a worker thread; each result is
  pushed right away with ``POST /api/agent/results`` (or with the next poll if that fails).
- Only outbound HTTPS: works behind any home router / NAT without opening a port.
"""

import logging
import queue
import random
import threading
import time

from . import AGENT_VERSION, PROTOCOL_VERSION, config
from .transport import ApiError, Transport, Unauthorized, install_dns_fallback, remember_ips

log = logging.getLogger("HOTS.remote.agent")

ENROLL_PATH = "/api/agent/enroll"
POLL_PATH = "/api/agent/poll"
RESULTS_PATH = "/api/agent/results"
GOODBYE_PATH = "/api/agent/goodbye"

POLL_TIMEOUT = 70            # server holds the request up to ~25 s
STATE_REFRESH = 15 * 60      # periodic full state upload
PERIODIC_CHECKS = 30 * 60    # netblock exclusions / drift checks
MAX_BACKOFF = 120


class EnrollError(Exception):
    def __init__(self, message: str, network: bool = False):
        super().__init__(message)
        self.network = network


def enroll(server_url: str, code: str, info: dict) -> dict:
    """Exchange a one-time enrollment code (shown in the console) for device credentials."""
    url = config.normalize_server_url(server_url)
    transport = Transport(url, timeout=30)
    payload = dict(info)
    payload.update({"code": (code or "").strip().upper(), "protocol": PROTOCOL_VERSION})
    try:
        resp = transport.request("POST", ENROLL_PATH, payload)
    except Unauthorized as e:
        raise EnrollError(e.message or "Code refusé par le serveur.") from None
    except ApiError as e:
        raise EnrollError(e.message, network=e.status == 0) from None
    device_id, token = resp.get("device_id"), resp.get("token")
    if not (isinstance(device_id, str) and isinstance(token, str) and device_id and token):
        raise EnrollError("Réponse inattendue du serveur.")
    cfg = {
        "server_url": url,
        "device_id": device_id,
        "token": token,
        "account": resp.get("account_name", ""),
        "enrolled_at": time.time(),
        "server_ips": transport.resolve_server_ips(),
    }
    config.save(cfg)
    return cfg


def goodbye(cfg: dict) -> None:
    """Tell the server this PC is being uninstalled (best effort)."""
    try:
        Transport(cfg["server_url"], auth=f"{cfg['device_id']}.{cfg['token']}", timeout=10).request(
            "POST", GOODBYE_PATH, {"reason": "uninstall"})
    except Exception:
        pass


class Agent:
    def __init__(self, cfg: dict, executor, state_builder, info_builder, periodic=None,
                 stop_event: threading.Event = None, lang: str = "fr"):
        """
        executor(action, params, lang) -> (ok, result, error, mutating)
        state_builder(lang) -> dict
        info_builder() -> dict  (hostname, os, versions...)
        periodic(agent) -> None  (called every PERIODIC_CHECKS seconds from the worker thread)
        """
        self.cfg = cfg
        self.executor = executor
        self.state_builder = state_builder
        self.info_builder = info_builder
        self.periodic = periodic
        self.stop_event = stop_event or threading.Event()
        self.lang = lang
        self.transport = Transport(cfg["server_url"], auth=f"{cfg['device_id']}.{cfg['token']}",
                                   timeout=POLL_TIMEOUT)
        remember_ips(self.transport.host, cfg.get("server_ips") or [])
        self._queue: "queue.Queue" = queue.Queue()
        self._pending_results: list = []
        self._pending_state = None
        self._lock = threading.Lock()
        self._state_due = True
        self._last_state = 0.0
        self._last_periodic = 0.0
        self.revoked = False
        self._worker = threading.Thread(target=self._worker_loop, name="hots-agent-worker", daemon=True)

    # -- worker ------------------------------------------------------------------------------
    def _worker_loop(self):
        while not self.stop_event.is_set():
            try:
                cmd = self._queue.get(timeout=5)
            except queue.Empty:
                self._maybe_periodic()
                continue
            if cmd is None:
                return
            result = self._run_command(cmd)
            state = None
            if result.pop("_mutating", False) and self._queue.empty():
                state = self._safe_state()
            self._push(result, state)

    def _run_command(self, cmd: dict) -> dict:
        cid = cmd.get("id")
        action = cmd.get("action", "")
        params = cmd.get("params") or {}
        started = time.monotonic()
        log.info("command %s: %s", cid, action)
        try:
            ok, result, error, mutating = self.executor(action, params, self.lang)
        except Exception as e:  # executor must never kill the worker
            log.exception("executor crashed on %s", action)
            ok, result, error, mutating = False, None, f"{type(e).__name__}: {e}", False
        if action == "get_state" and ok and isinstance(result, dict):
            with self._lock:
                self._pending_state = result
                self._last_state = time.monotonic()
        return {"id": cid, "ok": bool(ok), "result": result, "error": error or "",
                "duration_ms": int((time.monotonic() - started) * 1000), "_mutating": bool(mutating)}

    def _safe_state(self):
        try:
            state = self.state_builder(self.lang)
            self._last_state = time.monotonic()
            return state
        except Exception:
            log.exception("state builder failed")
            return None

    def _push(self, result: dict, state) -> None:
        payload = {"results": [result]}
        if state is not None:
            payload["state"] = state
        try:
            self.transport.request("POST", RESULTS_PATH, payload, timeout=30)
            return
        except Unauthorized:
            self._revoke()
            return
        except ApiError as e:
            log.warning("result push failed (%s), will retry with next poll", e.message)
        with self._lock:
            self._pending_results.append(result)
            if state is not None:
                self._pending_state = state

    def _maybe_periodic(self):
        now = time.monotonic()
        if self.periodic and now - self._last_periodic >= PERIODIC_CHECKS:
            self._last_periodic = now
            try:
                self.periodic(self)
            except Exception:
                log.exception("periodic checks failed")
        if now - self._last_state >= STATE_REFRESH:
            self._state_due = True

    # -- main loop ---------------------------------------------------------------------------
    def _revoke(self):
        if not self.revoked:
            log.warning("device credentials refused by the server: remote administration disabled")
            self.revoked = True
            config.clear()
            config.write_status(connected=False, revoked=True, last_error="device removed from the console")
            self.stop_event.set()

    def run(self) -> None:
        install_dns_fallback()
        self._worker.start()
        backoff = 1.0
        connected = None
        while not self.stop_event.is_set():
            with self._lock:
                results, self._pending_results = self._pending_results, []
                state, self._pending_state = self._pending_state, None
            if state is None and self._state_due:
                state = self._safe_state()
                self._state_due = False
            payload = {"protocol": PROTOCOL_VERSION, "info": self.info_builder(), "results": results}
            if state is not None:
                payload["state"] = state
            started = time.monotonic()
            try:
                resp = self.transport.request("POST", POLL_PATH, payload, timeout=POLL_TIMEOUT)
            except Unauthorized:
                self._revoke()
                break
            except ApiError as e:
                with self._lock:
                    self._pending_results = results + self._pending_results
                    if state is not None and self._pending_state is None:
                        self._pending_state = state
                if connected is not False:
                    log.warning("server unreachable: %s", e.message)
                    config.write_status(connected=False, last_error=e.message)
                connected = False
                delay = min(MAX_BACKOFF, backoff) * random.uniform(0.7, 1.3)
                backoff = min(MAX_BACKOFF, backoff * 2)
                self.stop_event.wait(delay)
                continue

            backoff = 1.0
            if connected is not True:
                log.info("connected to %s", self.cfg["server_url"])
                config.write_status(connected=True, last_error="", revoked=False,
                                    server_url=self.cfg["server_url"])
            connected = True
            if isinstance(resp.get("lang"), str):
                self.lang = resp["lang"][:5]
            if resp.get("request_state"):
                self._state_due = True
            for cmd in resp.get("commands") or []:
                if isinstance(cmd, dict) and isinstance(cmd.get("id"), (int, str)):
                    self._queue.put(cmd)
            if resp.get("commands"):
                # Results come back through RESULTS_PATH; keep polling right away.
                continue
            if time.monotonic() - self._last_state >= STATE_REFRESH:
                self._state_due = True
            if time.monotonic() - started < 1.0:
                # Server answered without holding the request: avoid a tight loop.
                retry = resp.get("retry_after")
                retry = retry if isinstance(retry, (int, float)) and not isinstance(retry, bool) else 2
                self.stop_event.wait(min(60.0, max(1.0, float(retry))))
        self._queue.put(None)
