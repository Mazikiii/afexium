import json


class TestCommoditiesAPI:
    def test_list_commodities_empty(self, client):
        response = client.get("/api/v1/commodities")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["commodities"] == []

    def test_list_commodities(self, client, sample_commodity):
        response = client.get("/api/v1/commodities")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data["commodities"]) == 1
        assert data["commodities"][0]["name"] == "Maize"
        assert data["commodities"][0]["symbol"] == "MAZ"

    def test_get_commodity(self, client, sample_commodity):
        response = client.get(f"/api/v1/commodities/{sample_commodity.id}")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["name"] == "Maize"

    def test_get_commodity_not_found(self, client):
        response = client.get("/api/v1/commodities/999")
        assert response.status_code == 404

    def test_record_price(self, client, sample_commodity):
        payload = {"price": 1500.00, "currency": "NGN", "source": "LCFE"}
        response = client.post(
            f"/api/v1/commodities/{sample_commodity.id}/prices",
            data=json.dumps(payload),
            content_type="application/json",
        )
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data["price"] == 1500.00
        assert data["currency"] == "NGN"
        assert data["source"] == "LCFE"

    def test_record_price_invalid_payload(self, client, sample_commodity):
        payload = {"price": -100}
        response = client.post(
            f"/api/v1/commodities/{sample_commodity.id}/prices",
            data=json.dumps(payload),
            content_type="application/json",
        )
        assert response.status_code == 400

    def test_record_price_commodity_not_found(self, client):
        payload = {"price": 1500.00}
        response = client.post(
            "/api/v1/commodities/999/prices",
            data=json.dumps(payload),
            content_type="application/json",
        )
        assert response.status_code == 404

    def test_list_prices(self, client, sample_commodity):
        for price in [1000, 1100, 1200]:
            client.post(
                f"/api/v1/commodities/{sample_commodity.id}/prices",
                data=json.dumps({"price": price}),
                content_type="application/json",
            )

        response = client.get(
            f"/api/v1/commodities/{sample_commodity.id}/prices?limit=2"
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data["prices"]) == 2
        assert data["prices"][0]["price"] == 1200.0

    def test_latest_price(self, client, sample_commodity):
        client.post(
            f"/api/v1/commodities/{sample_commodity.id}/prices",
            data=json.dumps({"price": 1000}),
            content_type="application/json",
        )
        client.post(
            f"/api/v1/commodities/{sample_commodity.id}/prices",
            data=json.dumps({"price": 1500}),
            content_type="application/json",
        )

        response = client.get(
            f"/api/v1/commodities/{sample_commodity.id}/prices/latest"
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["latest_price"]["price"] == 1500.0
        assert data["commodity"]["name"] == "Maize"

    def test_latest_price_no_prices(self, client, sample_commodity):
        response = client.get(
            f"/api/v1/commodities/{sample_commodity.id}/prices/latest"
        )
        assert response.status_code == 404
