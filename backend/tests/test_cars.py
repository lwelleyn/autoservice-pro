from datetime import datetime, timezone

import pytest

from tests.conftest import OTHER_VIN, VIN

CAR = {"brand": "Honda", "model": "Accord", "year": 2003, "vin": VIN}


def test_create_car(client, make_client):
    owner = make_client()
    response = client.post("/cars", json={"client_id": owner["id"], **CAR})
    assert response.status_code == 200
    assert response.json() == {"id": 1, "client_id": owner["id"], **CAR}


def test_vin_is_normalized_to_upper_case(client, make_client):
    owner = make_client()
    payload = {"client_id": owner["id"], **CAR, "vin": f" {VIN.lower()} "}
    response = client.post("/cars", json=payload)
    assert response.status_code == 200
    assert response.json()["vin"] == VIN


def test_list_cars_is_flat(client, make_car, make_work_order):
    car = make_car()
    make_work_order(car_id=car["id"])
    response = client.get("/cars")
    assert response.status_code == 200
    assert response.json() == [car]
    assert "work_orders" not in response.json()[0]


def test_get_car_includes_work_orders(client, make_car, make_work_order):
    car = make_car()
    order = make_work_order(car_id=car["id"])
    response = client.get(f"/cars/{car['id']}")
    assert response.status_code == 200
    assert response.json() == {**car, "work_orders": [order]}


def test_update_car(client, make_client, make_car):
    car = make_car()
    new_owner = make_client(email="new@example.com")
    updated = {
        "client_id": new_owner["id"],
        "brand": "Toyota",
        "model": "Camry",
        "year": 2020,
        "vin": OTHER_VIN,
    }
    response = client.put(f"/cars/{car['id']}", json=updated)
    assert response.status_code == 200
    assert response.json() == {"id": car["id"], **updated}


def test_update_car_keeping_its_own_vin(client, make_car):
    car = make_car()
    payload = {**car, "model": "Civic"}
    payload.pop("id")
    response = client.put(f"/cars/{car['id']}", json=payload)
    assert response.status_code == 200
    assert response.json()["model"] == "Civic"


def test_delete_car_cascades_to_work_orders(client, make_car, make_work_order):
    car = make_car()
    make_work_order(car_id=car["id"])
    assert client.delete(f"/cars/{car['id']}").status_code == 200
    assert client.get(f"/cars/{car['id']}").status_code == 404
    assert client.get("/work-orders").json() == []
    # The owner is untouched.
    assert len(client.get("/clients").json()) == 1


@pytest.mark.parametrize("method", ["get", "put", "delete"])
def test_missing_car_returns_404(client, make_client, method):
    owner = make_client()
    kwargs = {"json": {"client_id": owner["id"], **CAR}} if method == "put" else {}
    response = getattr(client, method)("/cars/999", **kwargs)
    assert response.status_code == 404
    assert response.json() == {"detail": "Car not found"}


def test_create_car_for_missing_client_returns_404(client):
    response = client.post("/cars", json={"client_id": 999, **CAR})
    assert response.status_code == 404
    assert response.json() == {"detail": "Client not found"}


def test_update_car_to_missing_client_returns_404(client, make_car):
    car = make_car()
    response = client.put(f"/cars/{car['id']}", json={"client_id": 999, **CAR})
    assert response.status_code == 404
    assert response.json() == {"detail": "Client not found"}
    assert client.get(f"/cars/{car['id']}").json()["client_id"] == car["client_id"]


def test_create_car_with_duplicate_vin_returns_409(client, make_car):
    car = make_car()
    response = client.post("/cars", json={"client_id": car["client_id"], **CAR})
    assert response.status_code == 409
    assert VIN in response.json()["detail"]
    assert len(client.get("/cars").json()) == 1


def test_duplicate_vin_check_is_case_insensitive(client, make_car):
    car = make_car()
    payload = {"client_id": car["client_id"], **CAR, "vin": VIN.lower()}
    assert client.post("/cars", json=payload).status_code == 409


def test_update_car_to_duplicate_vin_returns_409(client, make_car):
    first = make_car()
    second = make_car(client_id=first["client_id"], vin=OTHER_VIN)
    payload = {"client_id": second["client_id"], **CAR, "vin": VIN}
    response = client.put(f"/cars/{second['id']}", json=payload)
    assert response.status_code == 409
    assert client.get(f"/cars/{second['id']}").json()["vin"] == OTHER_VIN


@pytest.mark.parametrize(
    "overrides",
    [
        {"vin": "1HGCM82633A00435"},  # 16 characters
        {"vin": "1HGCM82633A0043522"},  # 18 characters
        {"vin": "IHGCM82633A004352"},  # contains I
        {"vin": "1HGCM82633A00435O"},  # contains O
        {"vin": "1HGCM82633A00435Q"},  # contains Q
        {"vin": "1HGCM82633A00435-"},  # not alphanumeric
        {"year": 1899},
        {"year": datetime.now(timezone.utc).year + 2},
        {"brand": ""},
        {"brand": "x" * 51},
        {"model": ""},
        {"model": "x" * 51},
    ],
)
def test_invalid_car_returns_422(client, make_client, make_car, overrides):
    owner = make_client()
    payload = {"client_id": owner["id"], **CAR, **overrides}
    assert client.post("/cars", json=payload).status_code == 422
    car = make_car(client_id=owner["id"])
    assert client.put(f"/cars/{car['id']}", json=payload).status_code == 422


@pytest.mark.parametrize("year", [1900, datetime.now(timezone.utc).year + 1])
def test_boundary_years_are_accepted(client, make_client, year):
    owner = make_client()
    response = client.post("/cars", json={"client_id": owner["id"], **CAR, "year": year})
    assert response.status_code == 200
