def test_root(client):
    assert client.get("/").status_code == 200


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_metrics_are_exposed(client):
    client.get("/clients")
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "http_requests_total" in response.text


def test_cors_allows_both_default_dev_origins(client):
    for origin in ("http://localhost:5173", "http://127.0.0.1:5173"):
        response = client.get("/clients", headers={"Origin": origin})
        assert response.headers["access-control-allow-origin"] == origin
    response = client.get("/clients", headers={"Origin": "http://evil.example"})
    assert "access-control-allow-origin" not in response.headers
