from decimal import Decimal
from flask import Blueprint, jsonify, request
from marshmallow import Schema, fields, validate
from afexium import db
from afexium.models import Commodity, CommodityPrice

commodities_bp = Blueprint("commodities", __name__)


class PriceCreateSchema(Schema):
    price = fields.Float(required=True, validate=validate.Range(min=0))
    currency = fields.Str(
        missing="NGN", validate=validate.Length(min=3, max=3)
    )
    source = fields.Str(load_default=None)


price_schema = PriceCreateSchema()


@commodities_bp.route("", methods=["GET"])
def list_commodities():
    commodities = Commodity.query.order_by(Commodity.name).all()
    return jsonify({"commodities": [c.to_dict() for c in commodities]}), 200


@commodities_bp.route("/<int:commodity_id>", methods=["GET"])
def get_commodity(commodity_id):
    commodity = db.session.get(Commodity, commodity_id)
    if not commodity:
        return jsonify({"error": "Commodity not found"}), 404
    return jsonify(commodity.to_dict()), 200


@commodities_bp.route("/<int:commodity_id>/prices", methods=["GET"])
def list_prices(commodity_id):
    commodity = db.session.get(Commodity, commodity_id)
    if not commodity:
        return jsonify({"error": "Commodity not found"}), 404

    limit = request.args.get("limit", 10, type=int)
    prices = (
        CommodityPrice.query.filter_by(commodity_id=commodity_id)
        .order_by(CommodityPrice.recorded_at.desc())
        .limit(limit)
        .all()
    )
    return jsonify({"prices": [p.to_dict() for p in prices]}), 200


@commodities_bp.route("/<int:commodity_id>/prices", methods=["POST"])
def record_price(commodity_id):
    commodity = db.session.get(Commodity, commodity_id)
    if not commodity:
        return jsonify({"error": "Commodity not found"}), 404

    errors = price_schema.validate(request.get_json())
    if errors:
        return jsonify({"errors": errors}), 400

    data = request.get_json()
    new_price = CommodityPrice(
        commodity_id=commodity_id,
        price=Decimal(str(data["price"])),
        currency=data.get("currency", "NGN"),
        source=data.get("source"),
    )
    db.session.add(new_price)
    db.session.commit()

    return jsonify(new_price.to_dict()), 201


@commodities_bp.route("/<int:commodity_id>/prices/latest", methods=["GET"])
def latest_price(commodity_id):
    commodity = db.session.get(Commodity, commodity_id)
    if not commodity:
        return jsonify({"error": "Commodity not found"}), 404

    price = (
        CommodityPrice.query.filter_by(commodity_id=commodity_id)
        .order_by(CommodityPrice.recorded_at.desc())
        .first()
    )
    if not price:
        return jsonify({"error": "No prices recorded"}), 404

    return jsonify(
        {
            "commodity": commodity.to_dict(),
            "latest_price": price.to_dict(),
        }
    ), 200
