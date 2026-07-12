import pytest
from afexium import create_app, db as _db


@pytest.fixture(scope="session")
def app():
    app = create_app("testing")
    with app.app_context():
        _db.create_all()
        yield app
        _db.drop_all()


@pytest.fixture(scope="function")
def client(app):
    return app.test_client()


@pytest.fixture(scope="function")
def db_session(app):
    with app.app_context():
        _db.session.begin_nested()
        yield _db.session
        _db.session.rollback()


@pytest.fixture
def sample_commodity(db_session):
    from afexium.models import Commodity

    commodity = Commodity(name="Maize", symbol="MAZ", unit="kg")
    db_session.add(commodity)
    db_session.commit()
    return commodity


@pytest.fixture
def sample_warehouse(db_session):
    from afexium.models import Warehouse

    warehouse = Warehouse(
        name="Jos Central Warehouse",
        state="Plateau",
        lga="Jos North",
        address="123 Market Road, Jos",
        capacity_mt=Decimal("5000"),
    )
    db_session.add(warehouse)
    db_session.commit()
    return warehouse


from decimal import Decimal
