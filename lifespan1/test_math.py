from fastapi.testclient import TestClient
from main import app

def test_without_with_lifespan_does_not_run():
    client = TestClient(app, raise_server_exceptions=False)
    r = client.post("/predict", json={"x": 2})
    assert r.status_code == 500
    
def test_with_lifespan_runs():
    with TestClient(app) as client:
        r = client.post("/predict", json={"x": 2})
        assert r.status_code == 200
        assert r.json()["prediction"] == 84.0