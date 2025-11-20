import copy
import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

# Fixture que restaura el estado de 'activities' tras cada prueba
ORIGINAL_ACTIVITIES = copy.deepcopy(activities)

@pytest.fixture(autouse=True)
def reset_activities():
    yield
    activities.clear()
    activities.update(copy.deepcopy(ORIGINAL_ACTIVITIES))

def test_root_redirect():
    client = TestClient(app)
    resp = client.get("/")
    assert resp.status_code in (307, 308)
    assert resp.headers.get("location", "").endswith("/static/index.html")

def test_get_activities():
    client = TestClient(app)
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data

def test_signup_duplicate_and_unregister_flow():
    client = TestClient(app)
    activity = "Chess Club"
    email = "teststudent@example.com"

    # signup exitoso
    r = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert r.status_code == 200
    assert email in activities[activity]["participants"]

    # signup duplicado -> 400
    r2 = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert r2.status_code == 400

    # unregister exitoso
    r3 = client.post(f"/activities/{activity}/unregister", params={"email": email})
    assert r3.status_code == 200
    assert email not in activities[activity]["participants"]

    # unregister no registrado -> 400
    r4 = client.post(f"/activities/{activity}/unregister", params={"email": email})
    assert r4.status_code == 400

def test_activity_not_found_errors():
    client = TestClient(app)
    r = client.post("/activities/Nonexistent/signup", params={"email": "a@b.com"})
    assert r.status_code == 404
    r2 = client.post("/activities/Nonexistent/unregister", params={"email": "a@b.com"})
    assert r2.status_code == 404
