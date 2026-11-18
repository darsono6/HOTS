import os
import sys
import tempfile

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SERVER = os.path.join(ROOT, "server")
for path in (SERVER, ROOT):
    if path not in sys.path:
        sys.path.insert(0, path)

os.environ.setdefault("HOTS_PBKDF2_ITERATIONS", "1000")
os.environ.setdefault("HOTS_POLL_HOLD", "2")
os.environ["HOTS_DATA_DIR"] = tempfile.mkdtemp(prefix="hots-test-")


@pytest.fixture()
def fresh_db(monkeypatch, tmp_path):
    from hots_server import db, security, settings
    db.close()
    security.limiter._hits.clear()
    monkeypatch.setattr(settings, "DATA_DIR", str(tmp_path))
    monkeypatch.setattr(settings, "DB_PATH", str(tmp_path / "hots.db"))
    yield tmp_path
    db.close()


@pytest.fixture()
def client(fresh_db):
    from starlette.testclient import TestClient
    from hots_server.app import create_app
    with TestClient(create_app(), base_url="https://testserver") as c:
        c.headers["x-hots-csrf"] = "1"
        yield c


@pytest.fixture()
def admin(client):
    from hots_server import db
    token = db.get_meta("setup_token")
    r = client.post("/api/setup", json={"token": token, "email": "admin@example.com", "password": "motdepasse-admin",
                                        "name": "Admin", "server_name": "Test"})
    assert r.status_code == 200, r.text
    return client
