import pytest
from afexium import create_app, db as _db


@pytest.fixture(scope="session")
def app():
    app = create_app("testing")
    with app.app_context():
        _db.create_all()
        yield app
        _db.drop_all()


@pytest.fixture(autouse=True)
def _setup_db(app):
    with app.app_context():
        yield
        _db.session.rollback()
        for table in reversed(_db.metadata.sorted_tables):
            _db.session.execute(table.delete())
        _db.session.commit()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def sample_commodity(app):
    with app.app_context():
        from afexium.models import Commodity

        commodity = Commodity(name="Maize", symbol="MAZ", unit="kg")
        _db.session.add(commodity)
        _db.session.commit()
        yield commodity


@pytest.fixture
def sample_warehouse(app):
    from decimal import Decimal

    with app.app_context():
        from afexium.models import Warehouse

        warehouse = Warehouse(
            name="Jos Central Warehouse",
            state="Plateau",
            lga="Jos North",
            address="123 Market Road, Jos",
            capacity_mt=Decimal("5000"),
        )
        _db.session.add(warehouse)
        _db.session.commit()
        yield warehouse
