import pytest

from tests.conftest import CLIENT, OTHER_VIN


def test_create_client(client):
    response = client.post("/clients", json=CLIENT)
    assert response.status_code == 200
    assert response.json() == {"id": 1, **CLIENT}


def test_list_clients_is_flat(client, make_client, make_car):
    created = make_client()
    make_car(client_id=created["id"])
    response = client.get("/clients")
    assert response.status_code == 200
    assert response.json() == [created]
    assert "cars" not in response.json()[0]


def test_get_client_includes_cars_and_work_orders(client, make_client, make_car, make_work_order):
    created = make_client()
    car = make_car(client_id=created["id"])
    order = make_work_order(car_id=car["id"])
    response = client.get(f"/clients/{created['id']}")
    assert response.status_code == 200
    assert response.json() == {**created, "cars": [{**car, "work_orders": [order]}]}


def test_update_client(client, make_client):
    created = make_client()
    updated = {"name": "Petr Ivanov", "phone": "123", "email": "petr@example.com"}
    response = client.put(f"/clients/{created['id']}", json=updated)
    assert response.status_code == 200
    assert response.json() == {"id": created["id"], **updated}
    assert client.get(f"/clients/{created['id']}").json()["name"] == "Petr Ivanov"


def test_delete_client(client, make_client):
    created = make_client()
    assert client.delete(f"/clients/{created['id']}").status_code == 200
    assert client.get(f"/clients/{created['id']}").status_code == 404
    assert client.get("/clients").json() == []


def test_delete_client_cascades_to_cars_and_work_orders(
    client, make_client, make_car, make_work_order
):
    doomed = make_client()
    survivor = make_client(email="other@example.com")
    doomed_car = make_car(client_id=doomed["id"])
    surviving_car = make_car(client_id=survivor["id"], vin=OTHER_VIN)
    make_work_order(car_id=doomed_car["id"])
    surviving_order = make_work_order(car_id=surviving_car["id"])

    assert client.delete(f"/clients/{doomed['id']}").status_code == 200

    assert client.get("/clients").json() == [survivor]
    assert client.get("/cars").json() == [surviving_car]
    assert client.get("/work-orders").json() == [surviving_order]


@pytest.mark.parametrize("method", ["get", "put", "delete"])
def test_missing_client_returns_404(client, method):
    kwargs = {"json": CLIENT} if method == "put" else {}
    response = getattr(client, method)("/clients/999", **kwargs)
    assert response.status_code == 404
    assert response.json() == {"detail": "Client not found"}


@pytest.mark.parametrize(
    "overrides",
    [
        {"name": ""},
        {"name": "x" * 101},
        {"phone": ""},
        {"phone": "1" * 21},
        {"email": "not-an-email"},
        {"email": "a" * 95 + "@example.com"},
    ],
)
def test_invalid_client_returns_422(client, make_client, overrides):
    assert client.post("/clients", json={**CLIENT, **overrides}).status_code == 422
    created = make_client()
    response = client.put(f"/clients/{created['id']}", json={**CLIENT, **overrides})
    assert response.status_code == 422


def test_client_missing_field_returns_422(client):
    assert client.post("/clients", json={"name": "No contacts"}).status_code == 422
