import pytest
import app as app_module

@pytest.fixture
def ring():
    return app_module.ConsistentHashRing(replicas=20)

@pytest.fixture
def client():
    app_module.ring = app_module.ConsistentHashRing(replicas=20)
    app_module.ring.add_node("node-a")
    app_module.ring.add_node("node-b")
    app_module.app.config["TESTING"] = True
    with app_module.app.test_client() as c:
        yield c

def test_add_remove(ring):
    assert ring.add_node("node-a") is True
    assert ring.add_node("node-a") is False
    assert ring.get_nodes() == ["node-a"]
    assert ring.remove_node("node-a") is True
    assert ring.get_nodes() == []

def test_route_is_stable(ring):
    ring.add_node("node-a"); ring.add_node("node-b")
    assert ring.get_node("user-123") == ring.get_node("user-123")
    assert ring.get_node("user-123") in {"node-a", "node-b"}

def test_empty_ring(ring):
    assert ring.get_node("key") is None

def test_api_route(client):
    r = client.get("/api/route/customer-100")
    assert r.status_code == 200
    assert r.get_json()["node"] in {"node-a", "node-b"}

def test_api_add_remove(client):
    assert client.post("/api/nodes", json={"node": "node-c"}).status_code == 201
    assert client.delete("/api/nodes/node-c").status_code == 200
    assert client.delete("/api/nodes/missing").status_code == 404

def test_stats(client):
    data = client.get("/api/stats").get_json()
    assert data["nodes"] == 2
    assert data["virtual_nodes"] == 40
