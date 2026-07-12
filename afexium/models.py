from datetime import datetime, timezone
from afexium import db


class Commodity(db.Model):
    __tablename__ = "commodities"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    symbol = db.Column(db.String(10), nullable=False, unique=True)
    unit = db.Column(db.String(20), nullable=False, default="kg")
    created_at = db.Column(
        db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    prices = db.relationship("CommodityPrice", backref="commodity", lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "symbol": self.symbol,
            "unit": self.unit,
            "created_at": self.created_at.isoformat(),
        }


class CommodityPrice(db.Model):
    __tablename__ = "commodity_prices"

    id = db.Column(db.Integer, primary_key=True)
    commodity_id = db.Column(
        db.Integer, db.ForeignKey("commodities.id"), nullable=False
    )
    price = db.Column(db.Numeric(12, 2), nullable=False)
    currency = db.Column(db.String(3), nullable=False, default="NGN")
    source = db.Column(db.String(100), nullable=True)
    recorded_at = db.Column(
        db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    def to_dict(self):
        return {
            "id": self.id,
            "commodity_id": self.commodity_id,
            "price": float(self.price),
            "currency": self.currency,
            "source": self.source,
            "recorded_at": self.recorded_at.isoformat(),
        }


class Warehouse(db.Model):
    __tablename__ = "warehouses"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    state = db.Column(db.String(100), nullable=False)
    lga = db.Column(db.String(100), nullable=True)
    address = db.Column(db.Text, nullable=True)
    capacity_mt = db.Column(db.Numeric(10, 2), nullable=False)
    utilized_mt = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(
        db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    def to_dict(self):
        utilization = (
            float(self.utilized_mt) / float(self.capacity_mt) * 100
            if self.capacity_mt > 0
            else 0
        )
        return {
            "id": self.id,
            "name": self.name,
            "state": self.state,
            "lga": self.lga,
            "address": self.address,
            "capacity_mt": float(self.capacity_mt),
            "utilized_mt": float(self.utilized_mt),
            "available_mt": float(self.capacity_mt - self.utilized_mt),
            "utilization_pct": round(utilization, 1),
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat(),
        }
