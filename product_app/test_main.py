from fastapi.testclient import TestClient
from product_app.main import app

TEST_USER = {"username": "test_user", "password": "test_password"}
TEST_PRODUCT = {"id": 99999, "name": "Test Product", "description": "Created by pytest", "price": 9.99}

def get_auth_header(client):
    client.post("/register", json=TEST_USER)  # 409 if already registered, that's fine
    r = client.post("/login", data=TEST_USER)
    return {"Authorization": f"Bearer {r.json()['token']}"}

def test_add_product():
    with TestClient(app) as client:
        headers = get_auth_header(client)
        client.delete(f"/products/{TEST_PRODUCT['id']}", headers=headers)

        r = client.post("/products", json=TEST_PRODUCT, headers=headers)
        assert r.status_code == 201
        assert r.json()["name"] == TEST_PRODUCT["name"]
        assert r.json()["price"] == TEST_PRODUCT["price"]

        r = client.get(f"/products/{TEST_PRODUCT['id']}")
        assert r.status_code == 200

        r = client.delete(f"/products/{TEST_PRODUCT['id']}", headers=headers)
        assert r.status_code == 200
