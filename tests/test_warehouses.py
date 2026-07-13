import json
from decimal import Decimal


class TestWarehousesAPI:
    def test_list_warehouses_empty(self, client):
        response = client.get("/api/v1/warehouses")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["warehouses"] == []

    def test_list_warehouses(self, client, sample_warehouse):
        response = client.get("/api/v1/warehouses")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data["warehouses"]) == 1
        assert data["warehouses"][0]["state"] == "Plateau"

    def test_filter_by_state(self, client, sample_warehouse):
        response = client.get("/api/v1/warehouses?state=Plateau")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data["warehouses"]) == 1

        response = client.get("/api/v1/warehouses?state=Lagos")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data["warehouses"]) == 0

    def test_get_warehouse(self, client, sample_warehouse):
        response = client.get(f"/api/v1/warehouses/{sample_warehouse.id}")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["name"] == "Jos Central Warehouse"
        assert data["capacity_mt"] == 5000.0
        assert data["utilization_pct"] == 0.0

    def test_get_warehouse_not_found(self, client):
        response = client.get("/api/v1/warehouses/999")
        assert response.status_code == 404

    def test_create_warehouse(self, client):
        payload = {
            "name": "Kano Warehouse",
            "state": "Kano",
            "lga": "Kano Municipal",
            "capacity_mt": 3000,
        }
        response = client.post(
            "/api/v1/warehouses",
            data=json.dumps(payload),
            content_type="application/json",
        )
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data["name"] == "Kano Warehouse"
        assert data["capacity_mt"] == 3000.0
        assert data["is_active"] is True

    def test_create_warehouse_invalid_payload(self, client):
        payload = {"name": "Test"}
        response = client.post(
            "/api/v1/warehouses",
            data=json.dumps(payload),
            content_type="application/json",
        )
        assert response.status_code == 400

    def test_available_warehouses(self, client, sample_warehouse):
        response = client.get("/api/v1/warehouses/available")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data["warehouses"]) == 1
        assert data["warehouses"][0]["available_mt"] == 5000.0

    def test_available_warehouses_with_min_capacity(self, client, sample_warehouse):
        from afexium import db
        from afexium.models import Warehouse

        warehouse = Warehouse(
            name="Small Warehouse",
            state="Lagos",
            capacity_mt=Decimal("200"),
            utilized_mt=Decimal("100"),
        )
        db.session.add(warehouse)
        db.session.commit()

        response = client.get("/api/v1/warehouses/available?min_capacity=50")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data["warehouses"]) == 2

        response = client.get("/api/v1/warehouses/available?min_capacity=200")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data["warehouses"]) == 1
        assert data["warehouses"][0]["name"] == "Jos Central Warehouse"

    def test_warehouse_utilization_calculation(self, client):
        payload = {
            "name": "Partially Used Warehouse",
            "state": "Oyo",
            "capacity_mt": 1000,
        }
        response = client.post(
            "/api/v1/warehouses",
            data=json.dumps(payload),
            content_type="application/json",
        )
        warehouse_id = json.loads(response.data)["id"]

        from afexium import db
        from afexium.models import Warehouse

        warehouse = db.session.get(Warehouse, warehouse_id)
        warehouse.utilized_mt = Decimal("750")
        db.session.commit()

        response = client.get(f"/api/v1/warehouses/{warehouse_id}")
        data = json.loads(response.data)
        assert data["utilization_pct"] == 75.0
        assert data["available_mt"] == 250.0
