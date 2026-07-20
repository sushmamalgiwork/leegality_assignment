import pytest
from fastapi.testclient import TestClient

from app.database import engine
from app.main import app
from app.models import Base


@pytest.fixture(autouse=True)
def reset_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


client = TestClient(app)


def test_create_and_list_nodes():
    response = client.post("/nodes", json={"name": "ServerA"})
    assert response.status_code == 201
    assert response.json() == {"id": 1, "name": "ServerA"}

    response = client.get("/nodes")
    assert response.status_code == 200
    assert response.json() == [{"id": 1, "name": "ServerA"}]


def test_duplicate_node_is_rejected():
    client.post("/nodes", json={"name": "ServerA"})
    response = client.post("/nodes", json={"name": "ServerA"})
    assert response.status_code == 400


def test_create_edge_with_missing_nodes_is_rejected():
    response = client.post(
        "/edges",
        json={"source": "ServerA", "destination": "ServerB", "latency": 10.0},
    )
    assert response.status_code == 400


def test_create_edge_with_negative_latency_is_rejected():
    client.post("/nodes", json={"name": "ServerA"})
    client.post("/nodes", json={"name": "ServerB"})
    response = client.post(
        "/edges",
        json={"source": "ServerA", "destination": "ServerB", "latency": -1.0},
    )
    assert response.status_code == 400


def test_duplicate_edge_is_rejected():
    client.post("/nodes", json={"name": "ServerA"})
    client.post("/nodes", json={"name": "ServerB"})
    client.post(
        "/edges",
        json={"source": "ServerA", "destination": "ServerB", "latency": 10.0},
    )
    response = client.post(
        "/edges",
        json={"source": "ServerA", "destination": "ServerB", "latency": 12.0},
    )
    assert response.status_code == 400


def test_direct_edge_shortest_path():
    client.post("/nodes", json={"name": "ServerA"})
    client.post("/nodes", json={"name": "ServerB"})
    client.post(
        "/edges",
        json={"source": "ServerA", "destination": "ServerB", "latency": 5.5},
    )

    response = client.post(
        "/routes/shortest",
        json={"source": "ServerA", "destination": "ServerB"},
    )

    assert response.status_code == 200
    assert response.json() == {"total_latency": 5.5, "path": ["ServerA", "ServerB"]}


def test_dijkstra_favors_multi_hop_route_over_expensive_direct_edge():
    client.post("/nodes", json={"name": "ServerA"})
    client.post("/nodes", json={"name": "ServerB"})
    client.post("/nodes", json={"name": "ServerC"})
    client.post("/nodes", json={"name": "ServerD"})

    client.post(
        "/edges",
        json={"source": "ServerA", "destination": "ServerB", "latency": 1.0},
    )
    client.post(
        "/edges",
        json={"source": "ServerB", "destination": "ServerD", "latency": 2.0},
    )
    client.post(
        "/edges",
        json={"source": "ServerA", "destination": "ServerD", "latency": 10.0},
    )
    client.post(
        "/edges",
        json={"source": "ServerA", "destination": "ServerC", "latency": 1.5},
    )

    response = client.post(
        "/routes/shortest",
        json={"source": "ServerA", "destination": "ServerD"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "total_latency": 3.0,
        "path": ["ServerA", "ServerB", "ServerD"],
    }


def test_returns_404_when_no_path_exists():
    client.post("/nodes", json={"name": "ServerA"})
    client.post("/nodes", json={"name": "ServerB"})
    client.post(
        "/edges",
        json={"source": "ServerA", "destination": "ServerB", "latency": 5.0},
    )

    response = client.post(
        "/routes/shortest",
        json={"source": "ServerB", "destination": "ServerA"},
    )

    assert response.status_code == 404
    assert response.json() == {"error": "No path exists between ServerB and ServerA"}


def test_unknown_nodes_return_400_for_route_query():
    response = client.post(
        "/routes/shortest",
        json={"source": "MissingA", "destination": "MissingB"},
    )
    assert response.status_code == 400


def test_route_history_is_recorded_and_can_be_filtered():
    client.post("/nodes", json={"name": "ServerA"})
    client.post("/nodes", json={"name": "ServerB"})
    client.post("/nodes", json={"name": "ServerC"})
    client.post(
        "/edges",
        json={"source": "ServerA", "destination": "ServerB", "latency": 3.0},
    )
    client.post(
        "/edges",
        json={"source": "ServerA", "destination": "ServerC", "latency": 4.0},
    )

    client.post("/routes/shortest", json={"source": "ServerA", "destination": "ServerB"})
    client.post(
        "/routes/shortest",
        json={"source": "ServerA", "destination": "ServerZ"},
    )

    response = client.get("/routes/history?source=ServerA&limit=1")
    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 1
    assert payload[0]["source"] == "ServerA"
    assert payload[0]["destination"] in {"ServerB", "ServerZ"}


def test_delete_node_and_edge():
    client.post("/nodes", json={"name": "ServerA"})
    client.post("/nodes", json={"name": "ServerB"})
    client.post(
        "/edges",
        json={"source": "ServerA", "destination": "ServerB", "latency": 7.0},
    )

    delete_node = client.delete("/nodes/1")
    assert delete_node.status_code == 200

    delete_edge = client.delete("/edges/1")
    assert delete_edge.status_code == 200

    assert client.get("/nodes").json() == [{"id": 2, "name": "ServerB"}]
    assert client.get("/edges").json() == []
