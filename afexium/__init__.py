import os
import logging
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def create_app(config_name=None):
    app = Flask(__name__)

    if config_name == "testing":
        app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
            "TEST_DATABASE_URL", "sqlite:///:memory:"
        )
        app.config["TESTING"] = True
    else:
        app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
            "DATABASE_URL",
            "postgresql://admin:password@localhost:5432/afexium",
        )

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
    }

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    db.init_app(app)

    from afexium.api.commodities import commodities_bp
    from afexium.api.warehouses import warehouses_bp

    app.register_blueprint(commodities_bp, url_prefix="/api/v1/commodities")
    app.register_blueprint(warehouses_bp, url_prefix="/api/v1/warehouses")

    @app.route("/health")
    def health():
        try:
            db.session.execute(db.text("SELECT 1"))
            db_status = "healthy"
        except Exception:
            db_status = "unhealthy"

        return jsonify(
            {
                "status": "healthy" if db_status == "healthy" else "degraded",
                "database": db_status,
            }
        ), (200 if db_status == "healthy" else 503)

    @app.route("/")
    def index():
        return jsonify(
            {
                "service": "Afexium",
                "version": "1.0.0",
                "endpoints": {
                    "health": "/health",
                    "commodities": "/api/v1/commodities",
                    "warehouses": "/api/v1/warehouses",
                },
            }
        )

    return app
