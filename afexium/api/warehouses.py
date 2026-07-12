from decimal import Decimal
from flask import Blueprint, jsonify, request
from marshmallow import Schema, fields, validate
from afexium import db
from afexium.models import Warehouse

warehouses_bp = Blueprint("warehouses", __name__)


class WarehouseCreateSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=1, max=200))
    state = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    lga = fields.Str(load_default=None)
    address = fields.Str(load_default=None)
    capacity_mt = fields.Float(
        required=True, validate=validate.Range(min=0.1)
    )


warehouse_schema = WarehouseCreateSchema()


@warehouses_bp.route("", methods=["GET"])
def list_warehouses():
    state = request.args.get("state")
    active_only = request.args.get("active_only", "true").lower() == "true"

    query = Warehouse.query
    if state:
        query = query.filter(Warehouse.state.ilike(f"%{state}%"))
    if active_only:
        query = query.filter_by(is_active=True)

    warehouses = query.order_by(Warehouse.state, Warehouse.name).all()
    return jsonify({"warehouses": [w.to_dict() for w in warehouses]}), 200


@warehouses_bp.route("/<int:warehouse_id>", methods=["GET"])
def get_warehouse(warehouse_id):
    warehouse = db.session.get(Warehouse, warehouse_id)
    if not warehouse:
        return jsonify({"error": "Warehouse not found"}), 404
    return jsonify(warehouse.to_dict()), 200


@warehouses_bp.route("", methods=["POST"])
def create_warehouse():
    errors = warehouse_schema.validate(request.get_json())
    if errors:
        return jsonify({"errors": errors}), 400

    data = request.get_json()
    warehouse = Warehouse(
        name=data["name"],
        state=data["state"],
        lga=data.get("lga"),
        address=data.get("address"),
        capacity_mt=Decimal(str(data["capacity_mt"])),
    )
    db.session.add(warehouse)
    db.session.commit()

    return jsonify(warehouse.to_dict()), 201


@warehouses_bp.route("/available", methods=["GET"])
def available_warehouses():
    state = request.args.get("state")
    min_capacity = request.args.get("min_capacity", 0, type=float)

    query = Warehouse.query.filter_by(is_active=True)
    if state:
        query = query.filter(Warehouse.state.ilike(f"%{state}%"))

    warehouses = query.all()
    available = [
        w
        for w in warehouses
        if float(w.capacity_mt - w.utilized_mt) >= min_capacity
    ]

    return jsonify({"warehouses": [w.to_dict() for w in available]}), 200
