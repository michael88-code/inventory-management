"""
Tests for restocking order API endpoints.
"""
from datetime import datetime

import pytest

import main


@pytest.fixture(autouse=True)
def clear_restock_orders():
    """Restock orders are stored in a module-level list, so reset it around each test."""
    main.restock_orders.clear()
    yield
    main.restock_orders.clear()


class TestDemandForecastPricing:
    """Demand forecasts carry the pricing the Restocking tab depends on."""

    def test_forecasts_have_cost_and_lead_time(self, client):
        """Every forecast item has a positive unit cost and lead time."""
        response = client.get("/api/demand")
        assert response.status_code == 200

        for forecast in response.json():
            assert forecast["unit_cost"] > 0
            assert isinstance(forecast["lead_time_days"], int)
            assert forecast["lead_time_days"] > 0


class TestRestockOrderEndpoints:
    """Test suite for /api/restock-orders."""

    def test_list_is_empty_initially(self, client):
        """No orders exist before any are submitted."""
        response = client.get("/api/restock-orders")
        assert response.status_code == 200
        assert response.json() == []

    def test_create_restock_order(self, client):
        """A valid order is priced from server data and returned with 201."""
        payload = {
            "budget": 5000,
            "items": [
                {"sku": "WDG-001", "quantity": 100},
                {"sku": "GSK-203", "quantity": 50},
            ],
        }
        response = client.post("/api/restock-orders", json=payload)
        assert response.status_code == 201

        order = response.json()
        assert order["status"] == "Submitted"
        assert order["order_number"].startswith("RST-")
        assert len(order["items"]) == 2
        # WDG-001 is 24.50 x 100, GSK-203 is 6.75 x 50
        assert order["total_cost"] == pytest.approx(2450 + 337.5)
        assert order["budget"] == 5000

    def test_lead_time_is_longest_item(self, client):
        """The order arrives when its slowest item does."""
        payload = {
            "budget": 10000,
            "items": [
                {"sku": "FLT-405", "quantity": 10},  # 4 days
                {"sku": "CTL-330", "quantity": 1},   # 12 days
            ],
        }
        order = client.post("/api/restock-orders", json=payload).json()
        assert order["lead_time_days"] == 12

        submitted = datetime.fromisoformat(order["submitted_date"])
        expected = datetime.fromisoformat(order["expected_delivery"])
        assert (expected - submitted).days == 12

    def test_submitted_order_is_listed(self, client):
        """Submitted orders come back from GET, newest first."""
        first = client.post("/api/restock-orders", json={"budget": 1000, "items": [{"sku": "GSK-203", "quantity": 1}]}).json()
        second = client.post("/api/restock-orders", json={"budget": 1000, "items": [{"sku": "FLT-405", "quantity": 1}]}).json()

        orders = client.get("/api/restock-orders").json()
        assert [o["id"] for o in orders] == [second["id"], first["id"]]

    def test_over_budget_is_rejected(self, client):
        """An order costing more than the budget returns 400 and is not saved."""
        payload = {"budget": 100, "items": [{"sku": "MTR-304", "quantity": 1}]}
        response = client.post("/api/restock-orders", json=payload)
        assert response.status_code == 400
        assert "exceeds budget" in response.json()["detail"]
        assert client.get("/api/restock-orders").json() == []

    def test_unknown_sku_is_rejected(self, client):
        """SKUs outside the demand forecast return 400."""
        payload = {"budget": 1000, "items": [{"sku": "NOPE-999", "quantity": 1}]}
        response = client.post("/api/restock-orders", json=payload)
        assert response.status_code == 400

    def test_duplicate_sku_is_rejected(self, client):
        """The same SKU can't appear twice in one order."""
        payload = {
            "budget": 1000,
            "items": [{"sku": "GSK-203", "quantity": 1}, {"sku": "GSK-203", "quantity": 2}],
        }
        response = client.post("/api/restock-orders", json=payload)
        assert response.status_code == 400

    @pytest.mark.parametrize("payload", [
        {"budget": 1000, "items": []},
        {"budget": 1000, "items": [{"sku": "GSK-203", "quantity": 0}]},
        {"budget": -1, "items": [{"sku": "GSK-203", "quantity": 1}]},
    ])
    def test_invalid_payload_returns_422(self, client, payload):
        """Empty orders, zero quantities and negative budgets fail validation."""
        response = client.post("/api/restock-orders", json=payload)
        assert response.status_code == 422
