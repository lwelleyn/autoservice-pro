import pytest


def test_create_work_order_defaults_to_pending(client, make_car):
    car = make_car()
    response = client.post("/work-orders", json={"car_id": car["id"], "description": "Oil change"})
    assert response.status_code == 200
    body = response.json()
    assert body["id"] == 1
    assert body["car_id"] == car["id"]
    assert body["description"] == "Oil change"
    assert body["status"] == "pending"
    assert body["created_at"]


@pytest.mark.parametrize("status", ["pending", "in_progress", "completed", "cancelled"])
def test_all_statuses_are_accepted(client, make_car, status):
    car = make_car()
    payload = {"car_id": car["id"], "description": "Brakes", "status": status}
    response = client.post("/work-orders", json=payload)
    assert response.status_code == 200
    assert response.json()["status"] == status


def test_list_and_get_work_orders(client, make_work_order):
    order = make_work_order()
    assert client.get("/work-orders").json() == [order]
    response = client.get(f"/work-orders/{order['id']}")
    assert response.status_code == 200
    assert response.json() == order


def test_update_work_order(client, make_work_order):
    order = make_work_order()
    payload = {"car_id": order["car_id"], "description": "Replace pads", "status": "completed"}
    response = client.put(f"/work-orders/{order['id']}", json=payload)
    assert response.status_code == 200
    assert response.json() == {**order, **payload}


def test_delete_work_order(client, make_work_order):
    order = make_work_order()
    assert client.delete(f"/work-orders/{order['id']}").status_code == 200
    assert client.get(f"/work-orders/{order['id']}").status_code == 404
    # The car is untouched.
    assert len(client.get("/cars").json()) == 1


@pytest.mark.parametrize("method", ["get", "put", "delete"])
def test_missing_work_order_returns_404(client, make_car, method):
    car = make_car()
    kwargs = {"json": {"car_id": car["id"], "description": "x"}} if method == "put" else {}
    response = getattr(client, method)("/work-orders/999", **kwargs)
    assert response.status_code == 404
    assert response.json() == {"detail": "Work order not found"}


def test_create_work_order_for_missing_car_returns_404(client):
    response = client.post("/work-orders", json={"car_id": 999, "description": "x"})
    assert response.status_code == 404
    assert response.json() == {"detail": "Car not found"}


def test_update_work_order_to_missing_car_returns_404(client, make_work_order):
    order = make_work_order()
    response = client.put(
        f"/work-orders/{order['id']}", json={"car_id": 999, "description": "x"}
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "Car not found"}
    assert client.get(f"/work-orders/{order['id']}").json()["car_id"] == order["car_id"]


@pytest.mark.parametrize(
    "overrides",
    [
        {"status": "done"},
        {"status": ""},
        {"description": ""},
        {"description": "x" * 501},
    ],
)
def test_invalid_work_order_returns_422(client, make_work_order, overrides):
    order = make_work_order()
    payload = {"car_id": order["car_id"], "description": "Oil change", **overrides}
    assert client.post("/work-orders", json=payload).status_code == 422
    assert client.put(f"/work-orders/{order['id']}", json=payload).status_code == 422
