# ============================================================================
# Tests: Notes API CRUD, Validation, RBAC, Audit trail
# ============================================================================
from fastapi.testclient import TestClient

# Ensure app import works from src.api
from src.api.main import app

client = TestClient(app)


def auth_headers(user_id="u1", role="user"):
    return {"X-User-Id": user_id, "X-User-Role": role}


def test_health():
    resp = client.get("/")
    assert resp.status_code == 200
    assert resp.json()["message"] == "Healthy"


def test_create_note_requires_validation_and_creates_audit():
    payload = {"title": "My Note", "content": "Hello", "reason": "initial"}
    resp = client.post("/notes", json=payload, headers=auth_headers())
    assert resp.status_code == 201, resp.text
    data = resp.json()
    assert data["title"] == "My Note"


def test_list_and_pagination_scoped_by_owner():
    # Create two notes for u1 and one for u2
    client.post("/notes", json={"title": "n1", "content": "c"}, headers=auth_headers("u1"))
    client.post("/notes", json={"title": "n2", "content": "c"}, headers=auth_headers("u1"))
    client.post("/notes", json={"title": "n3", "content": "c"}, headers=auth_headers("u2"))
    # u1 should see only 2
    resp = client.get("/notes?limit=10&offset=0", headers=auth_headers("u1"))
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] >= 2
    assert all(item["owner_id"] == "u1" for item in data["items"])
    # admin sees all
    resp_admin = client.get("/notes", headers=auth_headers("admin", "admin"))
    assert resp_admin.status_code == 200
    assert resp_admin.json()["total"] >= data["total"]


def test_get_note_rbac_and_not_found():
    # Create note as u1
    r = client.post("/notes", json={"title": "solo", "content": "x"}, headers=auth_headers("u1"))
    nid = r.json()["id"]
    # u2 cannot access
    r2 = client.get(f"/notes/{nid}", headers=auth_headers("u2"))
    assert r2.status_code == 404
    # admin can access
    ra = client.get(f"/notes/{nid}", headers=auth_headers("admin", "admin"))
    assert ra.status_code == 200
    # unknown id
    r404 = client.get("/notes/999999", headers=auth_headers("admin", "admin"))
    assert r404.status_code in (404, 422)


def test_update_note_and_audit():
    r = client.post("/notes", json={"title": "before", "content": "x"}, headers=auth_headers("u1"))
    nid = r.json()["id"]
    up = client.put(f"/notes/{nid}", json={"title": "after", "reason": "typo"}, headers=auth_headers("u1"))
    assert up.status_code == 200
    assert up.json()["title"] == "after"
    # invalid update with no fields
    bad = client.put(f"/notes/{nid}", json={}, headers=auth_headers("u1"))
    assert bad.status_code == 400


def test_delete_note_rbac_and_audit():
    r = client.post("/notes", json={"title": "todel", "content": "x"}, headers=auth_headers("u1"))
    nid = r.json()["id"]
    # u2 cannot delete
    rforbid = client.delete(f"/notes/{nid}", headers=auth_headers("u2"))
    assert rforbid.status_code in (404, 403)
    # owner can delete
    rdel = client.delete(f"/notes/{nid}", headers=auth_headers("u1"))
    assert rdel.status_code == 204
    # then not found
    rnf = client.get(f"/notes/{nid}", headers=auth_headers("u1"))
    assert rnf.status_code == 404


def test_validation_errors():
    # empty title
    r = client.post("/notes", json={"title": " ", "content": "c"}, headers=auth_headers("u1"))
    assert r.status_code in (400, 422)
    # empty content
    r2 = client.post("/notes", json={"title": "x", "content": " "}, headers=auth_headers("u1"))
    assert r2.status_code in (400, 422)
